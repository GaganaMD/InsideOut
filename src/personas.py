"""C/D. Persona generator (CLI). Builds a persona from outer-layer criteria using the TRAIN split only.

Criteria syntax:  "var=level[|level...]; var2=level"   e.g.  "age_band=65+"  or
                  "age_band=18-29|30-49; income=Less than $30,000|$30,000-$50,000"
Variables must be on the Tier A whitelist (party only with --allow-party, labelled as a sensitivity persona).

Usage:
  python src/personas.py build --name retirees --criteria "age_band=65+"     # NEW group, corrected scores (default)
  python src/personas.py build ... --legacy-scores   # historical reproduction: shipped SD/CRT WITH known scoring defects
  python src/personas.py select-p3           # pre-registered rule, train data only
  python src/personas.py build-config        # the three submission personas (frozen estimates + one-page cards)
  python src/personas.py list-levels         # valid variables and levels

Scoring modes. CORRECTED (default for `build`): social desirability and CRT are re-scored from items. LEGACY
(`--legacy-scores`, and the frozen `build-config` estimates/evidence files): the dataset's shipped scores, which are
mis-scored for 180 (social desirability) and 450 (CRT) people; kept only to reproduce the pre-audit results exactly.
See reports/final_audit/statistical_audit.md.
"""
import argparse
import itertools
import json
import re
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from common import CONSTRUCTS, RESULTS, ROOT, TIER_A, TIER_B, load_green, load_people, low_income, wilson

MIN_N_TRAIN = 30          # below this the persona is "insufficient evidence"
MIN_N_BEHAVIOUR = 20      # per default condition, for the green-choice estimate
D_DISTINCT = 0.20         # |Cohen's d| threshold for calling a construct distinctive
OUT = ROOT / "reports/personas"


class CriteriaError(ValueError):
    pass


# ----------------------------------------------------------------------------- criteria
def parse_criteria(text: str, people: pd.DataFrame, allow_party: bool = False) -> dict[str, list[str]]:
    allowed = TIER_A + (TIER_B if allow_party else [])
    crit = {}
    for part in [p.strip() for p in text.split(";") if p.strip()]:
        if "=" not in part:
            raise CriteriaError(f"'{part}': expected var=level")
        var, levels = (s.strip() for s in part.split("=", 1))
        if var not in allowed:
            hint = " (party needs --allow-party; it is self-reported, Tier B)" if var in TIER_B else ""
            raise CriteriaError(f"'{var}' is not an allowed outer-layer variable{hint}. Allowed: {allowed}")
        valid = list(people[var].cat.categories)
        lv = [l.strip() for l in levels.split("|")]
        bad = [l for l in lv if l not in valid]
        if bad:
            raise CriteriaError(f"{var}: unknown level(s) {bad}. Valid: {valid}")
        lv = list(dict.fromkeys(lv))                      # drop duplicate levels, keep order
        if var in crit:                                   # repeated variable: clauses are ANDed, so intersect levels
            both = [l for l in crit[var] if l in lv]       # (previously the last clause silently overwrote the first)
            if not both:
                raise CriteriaError(f"{var}: contradictory repeated criteria {crit[var]} and {lv} (no level satisfies both)")
            lv = both
        crit[var] = lv
    if not crit:
        raise CriteriaError("empty criteria")
    return crit


def mask(people: pd.DataFrame, crit: dict) -> pd.Series:
    m = pd.Series(True, index=people.index)
    for var, lv in crit.items():
        m &= people[var].astype(str).isin(lv)
    return m


def describe(crit: dict) -> str:
    return "; ".join(f"{v} in {{{', '.join(l)}}}" if len(l) > 1 else f"{v} = {l[0]}" for v, l in crit.items())


# ----------------------------------------------------------------------------- shrinkage prior
def tau2_by_construct(train: pd.DataFrame) -> dict[str, float]:
    """Method-of-moments between-group variance across single-level Tier A groups (n_train >= 30)."""
    out = {}
    for c in CONSTRUCTS:
        means, noise = [], []
        for var in TIER_A:
            for _, g in train.groupby(var, observed=True):
                if len(g) >= 30:
                    means.append(g[c].mean())
                    noise.append(g[c].var(ddof=1) / len(g))
        out[c] = max(0.0, float(np.var(means, ddof=1) - np.mean(noise)))
    return out


# ----------------------------------------------------------------------------- core
def build(name: str, crit: dict, people: pd.DataFrame, green: pd.DataFrame, sensitivity_label: str = "") -> dict:
    train = people[people.split == "train"]
    m = mask(people, crit)
    mem_tr = people[m & (people.split == "train")]
    rep = dict(name=name, definition=describe(crit), criteria=crit, label=sensitivity_label,
               n_total=int(m.sum()), n_train=len(mem_tr), n_test=int((m & (people.split == "test")).sum()),
               share_of_population=float(m.mean()), built_from="train split only")
    if len(mem_tr) < MIN_N_TRAIN:
        rep["status"] = f"INSUFFICIENT EVIDENCE: n_train={len(mem_tr)} < {MIN_N_TRAIN}"
        return rep
    rep["status"] = "ok"
    tau2 = tau2_by_construct(train)
    inner = []
    for c, (_, label, _) in CONSTRUCTS.items():
        x, pop = mem_tr[c], train[c]
        n, mu_p, s_p = len(x), x.mean(), x.std(ddof=1)
        mu0, sd0 = pop.mean(), pop.std(ddof=1)
        se = s_p / np.sqrt(n)
        w = tau2[c] / (tau2[c] + se ** 2) if tau2[c] > 0 else 0.0
        shrunk = w * mu_p + (1 - w) * mu0
        d, d_se = (mu_p - mu0) / sd0, se / sd0
        d_lo, d_hi = d - 1.96 * d_se, d + 1.96 * d_se
        distinct = abs(d) >= D_DISTINCT and (d_lo > 0 or d_hi < 0)
        weak = (not distinct) and (d_lo > 0 or d_hi < 0)
        side = np.sign(mu_p - mu0)
        opposite = float(((x - pop.median()) * side < 0).mean()) if side != 0 else np.nan   # strict: ties excluded
        at_median = float((x == pop.median()).mean())
        # Shrinkage-consistent label (display only; the pre-registered `confidence` above is unchanged and still used
        # for every frozen result). Normal-normal posterior: mean = shrunk, SD = sqrt(w) * se. Because the posterior z is
        # sqrt(w) times the raw z, this label can only be equal to or weaker than the pre-registered one.
        post_se = np.sqrt(w) * se
        shrunk_d = (shrunk - mu0) / sd0
        s_lo, s_hi = shrunk - 1.96 * post_se, shrunk + 1.96 * post_se
        s_excl = (s_lo > mu0) or (s_hi < mu0)
        adj = ("distinct" if (abs(shrunk_d) >= D_DISTINCT and s_excl)
               else "weak difference" if s_excl else "not distinguishable from population")
        inner.append(dict(
            construct=c, label=label, n=n, typical_shrunk=shrunk, raw_mean=mu_p,
            mean_ci_lo=mu_p - 1.96 * se, mean_ci_hi=mu_p + 1.96 * se, shrink_weight=w,
            sd=s_p, p10=x.quantile(.1), median=x.median(), p90=x.quantile(.9),
            pop_mean=mu0, pop_sd=sd0, d=d, d_lo=d_lo, d_hi=d_hi,
            share_opposite_side_of_pop_median=opposite, share_at_pop_median=at_median,
            confidence="distinct" if distinct else ("weak difference" if weak else "not distinguishable from population"),
            shrunk_d=shrunk_d, shrunk_ci_lo=s_lo, shrunk_ci_hi=s_hi, confidence_shrinkage_adjusted=adj,
            source=f"Twin-2K-500 {CONSTRUCTS[c][0]}"))
    rep["inner"] = inner

    # Behaviour: hypothetical green-energy choice (default_eric), train members only
    gtr = green[green.split == "train"]
    gm = gtr[gtr.pid.isin(mem_tr.pid)]
    beh = []
    for cond in ("grey_default", "green_default"):
        s, p = gm[gm.green_condition == cond], gtr[gtr.green_condition == cond]
        k, n = int(s.chose_green.sum()), len(s)
        lo, hi = wilson(k, n)
        beh.append(dict(condition=cond, n=n, rate=k / n if n else np.nan, lo=lo, hi=hi,
                        pop_rate=p.chose_green.mean(), pop_n=len(p),
                        status="ok" if n >= MIN_N_BEHAVIOUR else f"INSUFFICIENT EVIDENCE (n={n} < {MIN_N_BEHAVIOUR})"))
    rep["green_choice"] = beh
    # say-do: among members with GREEN in the population top tercile, share declining green per condition
    thr = gtr.green.quantile(2 / 3)
    gap = []
    for cond in ("grey_default", "green_default"):
        s = gm[(gm.green >= thr) & (gm.green_condition == cond)]
        p = gtr[(gtr.green >= thr) & (gtr.green_condition == cond)]
        lo, hi = wilson(int((1 - s.chose_green).sum()), len(s))
        gap.append(dict(condition=cond, n_high_green=len(s), share_declining=1 - s.chose_green.mean() if len(s) else np.nan,
                        lo=lo, hi=hi, pop_share_declining=1 - p.chose_green.mean(),
                        status="ok" if len(s) >= MIN_N_BEHAVIOUR else f"INSUFFICIENT EVIDENCE (n={len(s)} < {MIN_N_BEHAVIOUR})"))
        # (was n >= 10; aligned 2026-11-15 with the pre-registered floor of 20 per default condition, hypotheses.md)
    rep["say_do_gap"] = gap
    rep["mega_study_participation"] = dict(n_train_in_default_eric=len(gm))
    return rep


# ----------------------------------------------------------------------------- P3 selection (pre-registered)
def select_p3(people: pd.DataFrame, p1: dict, p2: dict) -> pd.DataFrame:
    tr = people[people.split == "train"]
    m1, m2 = mask(tr, p1), mask(tr, p2)
    mu, sd = tr[list(CONSTRUCTS)].mean(), tr[list(CONSTRUCTS)].std(ddof=1)
    singles = [(v, str(l)) for v in TIER_A for l in tr[v].cat.categories]
    cands = [{v: [l]} for v, l in singles]
    cands += [{a[0]: [a[1]], b[0]: [b[1]]} for a, b in itertools.combinations(singles, 2) if a[0] != b[0]]
    rows = []
    for c in cands:
        mm = mask(tr, c)
        n = int(mm.sum())
        if n < 150:
            continue
        ov1, ov2 = (mm & m1).sum() / n, (mm & m2).sum() / n
        if ov1 > 0.5 or ov2 > 0.5:
            continue
        d = ((tr.loc[mm, list(CONSTRUCTS)].mean() - mu) / sd).abs()
        rows.append(dict(definition=describe(c), criteria=json.dumps(c), n_train=n, overlap_p1=ov1, overlap_p2=ov2,
                         mean_abs_d=d.mean(), **{f"d_{k}": v for k, v in d.items()}))
    return pd.DataFrame(rows).sort_values("mean_abs_d", ascending=False)


# ----------------------------------------------------------------------------- rendering
def fmt(x, nd=2):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


def confidence_text(r: dict, pre: str | None = None, adj: str | None = None) -> str:
    """Pre-registered label, plus the shrinkage-adjusted label when it is weaker (never silently replaced)."""
    pre, adj = pre or r["confidence"], adj or r.get("confidence_shrinkage_adjusted", r["confidence"])
    return pre if adj == pre else f"{pre} before shrinkage; **{adj} after shrinkage**"


def other_side_text(r: dict) -> str:
    o, t = r["share_opposite_side_of_pop_median"], r.get("share_at_pop_median", np.nan)
    if o is None or (isinstance(o, float) and np.isnan(o)):
        return "–"
    return f"{o:.0%}" + ("" if t is None or np.isnan(t) else f" ({t:.0%})")


def to_markdown(rep: dict, interp: dict | None = None, holdout: pd.DataFrame | None = None,
                scores_note: str | None = None) -> str:
    L = [f"# Persona: {rep['name']}", ""]
    if rep.get("label"):
        L += [f"> **{rep['label']}**", ""]
    L += [f"**Outer-layer definition:** {rep['definition']}  ",
          f"**n** = {rep['n_total']} ({rep['share_of_population']:.1%} of the panel); built from {rep['n_train']} "
          f"train members, {rep['n_test']} held out.", ""]
    if rep.get("scores") or scores_note:
        L += [f"> **Scores:** {scores_note or rep['scores']}.", ""]
    if rep["status"] != "ok":
        return "\n".join(L + [f"**{rep['status']}** — no profile is reported for this group.", ""])
    if interp and "Bottom line" in interp:
        L += ["## Bottom line", "", interp["Bottom line"], ""]
    L += ["## Inner layer (train members; typical = shrunken mean)", "",
          "| Construct | Typical | 95% CI (raw mean) | Spread p10–p90 (SD) | vs population (d, 95% CI) | % strictly on other side of pop. median (% exactly at it) | Confidence |",
          "|---|---|---|---|---|---|---|"]
    for r in rep["inner"]:
        L.append(f"| {r['label']} | {fmt(r['typical_shrunk'])} | {fmt(r['mean_ci_lo'])}–{fmt(r['mean_ci_hi'])} | "
                 f"{fmt(r['p10'], 1)}–{fmt(r['p90'], 1)} ({fmt(r['sd'])}) | {r['d']:+.2f} ({r['d_lo']:+.2f}, {r['d_hi']:+.2f}) | "
                 f"{other_side_text(r)} | {confidence_text(r)} |")
    L += ["", "Source: Twin-2K-500 wave 1–3 scores (spendthrift re-scored from items; see audit). "
          "**Typical** is an empirical-Bayes estimate pulled toward the population mean by an amount set by n and by how "
          "much Tier A groups differ on that construct (none, for dictator giving, so it equals the population mean). "
          "The **95% CI** is for the raw member mean, a different estimand. **d** is relative to the train population SD. "
          "**Confidence**: *distinct* = |d| ≥ 0.20 and CI excludes 0; *weak* = CI excludes 0 but |d| < 0.20 (pre-registered, "
          "on the raw mean). The same rule is then re-applied to the shrunken estimate (d of Typical; posterior CI = "
          "Typical ± 1.96·√w·SE, w = shrink weight); if it gives a weaker label, both are shown and only the shrinkage-"
          "adjusted label should be narrated. **Other side of median** counts members strictly beyond the population "
          "median on the opposite side; members exactly at the median (common on discrete scales) are shown separately.", ""]
    corr_path = ROOT / "reports/final_audit/corrected_scores/personas_sd_crt.csv"
    if corr_path.exists() and not rep.get("scores"):
        cc = pd.read_csv(corr_path)
        cc = cc[cc.persona == rep["name"]]
        if len(cc):
            L += ["**Measurement correction (final audit).** The shipped social-desirability and CRT scores are mis-scored "
                  "for 180 and 450 people (case- and format-sensitive string matching; see "
                  "`reports/final_audit/statistical_audit.md`). The table above keeps the frozen original values. "
                  "With corrected scores (same definition, train-built):", ""]
            for _, c in cc.iterrows():
                L.append(f"- {c['construct']}: d {c['d_train_original']:+.2f} → **{c['d_train_corrected']:+.2f}** "
                         f"({c['d_lo_corrected']:+.2f}, {c['d_hi_corrected']:+.2f}), {c['confidence_corrected']}; "
                         f"holdout d {c['d_test_corrected']:+.2f}, MAE gain {c['gain_pct_corrected']:+.1f}% "
                         f"(reduction CI {c['gain_lo_corrected']:+.3f} to {c['gain_hi_corrected']:+.3f} scale units)")
            L.append("")
    L += [
          "## Behaviour: hypothetical $39 renewable vs $32 supplier (Mega-Study `default_eric`)", "",
          "| Default condition | n | Chose renewable | 95% CI | Population |", "|---|---|---|---|---|"]
    for b in rep["green_choice"]:
        val = f"{b['rate']:.0%}" if b["status"] == "ok" else b["status"]
        L.append(f"| {b['condition']} | {b['n']} | {val} | {fmt(b['lo'])}–{fmt(b['hi'])} | {b['pop_rate']:.0%} (n={b['pop_n']}) |")
    L += ["", "**Say vs do** — members at or above the population's 67th-percentile green-values score (with ties, more than a third of people) who still declined the renewable option:", ""]
    for g in rep["say_do_gap"]:
        val = f"{g['share_declining']:.0%} ({fmt(g['lo'])}–{fmt(g['hi'])})" if g["status"] == "ok" else g["status"]
        L.append(f"- {g['condition']}: {val}, n={g['n_high_green']} (population {g['pop_share_declining']:.0%})")
    L += ["", "*These are hypothetical survey choices, not purchases.*", ""]
    if interp:
        for k, v in interp.items():
            if k != "Bottom line":
                L += [f"## {k}", "", v, ""]
    if holdout is not None and len(holdout):
        L += ["## Held-out check (frozen test split, evaluated once)", "",
              "| Construct | n test | MAE persona | MAE population mean | Gain, % of population MAE | MAE reduction in scale units (95% CI) | 80% interval coverage: persona / population |",
              "|---|---|---|---|---|---|---|"]
        for _, h in holdout.iterrows():
            L.append(f"| {h['construct']} | {int(h['n_test'])} | {fmt(h['mae_persona'])} | {fmt(h['mae_pop'])} | "
                     f"{h['gain_pct']:+.1f}% | {h['mae_pop'] - h['mae_persona']:+.3f} ({h['gain_lo']:+.3f}, {h['gain_hi']:+.3f}) | "
                     f"{h['cov_persona']:.0%} / {h['cov_pop']:.0%} |")
        L += ["", "*The CI is a participant bootstrap of the mean reduction in absolute error, in the construct's own units "
                  "(not in percent).*", ""]
        bp = RESULTS / "holdout_persona_behaviour.csv"
        if bp.exists():
            hb = pd.read_csv(bp)
            hb = hb[hb.persona == rep["name"]]
            L += ["Green choice on held-out members (Brier score; lower is better; persona rate used only if n ≥ 20 on train):", "",
                  "| Condition | n test | Test rate | Persona train rate | Brier persona / population |", "|---|---|---|---|---|"]
            for _, h in hb.iterrows():
                L.append(f"| {h['condition']} | {int(h['n_test'])} | {h['test_rate']:.0%} | {h['persona_train_rate']:.0%}"
                         f"{'' if h['used_persona_rate'] else ' (not used)'} | {h['brier_persona']:.3f} / {h['brier_pop']:.3f} |")
            L.append("")
    return "\n".join(L)


def to_card(rep: dict, interp: dict, holdout: pd.DataFrame | None, rep_corrected: dict | None = None) -> str:
    """One-page persona card (template fields); full tables live in <name>_evidence.md."""
    L = [f"# Persona: {rep['name']}", "",
         f"**Who (outer layer only):** {rep['definition']} · **n = {rep['n_total']}** "
         f"({rep['n_train']} train / {rep['n_test']} held out) · source: Twin-2K-500 waves 1–3 · "
         f"evidence: `{rep['name']}_evidence.md`", "", f"**Bottom line.** {interp['Bottom line']}", "",
         "| Part | Typical [p10–p90] | d vs pop. (95% CI) | Held-out d | Held-out error cut | Confidence |",
         "|---|---|---|---|---|---|"]
    hd = holdout.set_index("construct") if holdout is not None and len(holdout) else None
    corr_path = ROOT / "reports/final_audit/corrected_scores/personas_sd_crt.csv"
    cc = pd.read_csv(corr_path) if corr_path.exists() else pd.DataFrame(columns=["persona", "construct"])
    cc = cc[cc.persona == rep["name"]].set_index("construct")
    for r in rep["inner"]:
        c = r["construct"]
        if c in cc.index:  # corrected measurement (final audit) shown; original kept in the evidence file
            x = cc.loc[c]
            dtxt = f"{x.d_train_corrected:+.2f} ({x.d_lo_corrected:+.2f}, {x.d_hi_corrected:+.2f})†"
            ttxt = f"{x.d_test_corrected:+.2f}†"
            rc = next((q for q in (rep_corrected or {}).get("inner", []) if q["construct"] == c), None)
            conf = confidence_text(rc, pre=x.confidence_corrected) if rc else x.confidence_corrected
            typ = f"{fmt(x.typical_corrected)} [{fmt(x.p10_corrected, 0)}–{fmt(x.p90_corrected, 0)}]†"
            gain = x.gain_pct_corrected
        else:
            dtxt = f"{r['d']:+.2f} ({r['d_lo']:+.2f}, {r['d_hi']:+.2f})"
            ttxt = f"{hd.loc[c, 'test_d']:+.2f}" if hd is not None else "–"
            conf, typ = confidence_text(r), f"{fmt(r['typical_shrunk'])} [{fmt(r['p10'], 1)}–{fmt(r['p90'], 1)}]"
            gain = hd.loc[c, "gain_pct"] if hd is not None else np.nan
        for long, short in (("not distinguishable from population", "same as population"), ("weak difference", "weak")):
            conf = conf.replace(long, short)
        gtxt = "–" if pd.isna(gain) else ("0%" if abs(gain) < 0.5 else f"{gain:+.0f}%")
        L.append(f"| {r['label'].split(' (')[0].split(',')[0]} | {typ} | {dtxt} | {ttxt} | {gtxt} | {conf} |")
    L += ["", "Held-out error cut = reduction in absolute error vs the population mean on held-out members. "
          "*Distinct* = |d| ≥ 0.20 with CI excluding 0. † Corrected item-level scores; the dataset's shipped social-desirability "
          "and CRT scores are mis-scored for 180/450 people (`reports/final_audit/statistical_audit.md`, values in "
          "`reports/final_audit/corrected_scores/personas_sd_crt.csv`). Frozen legacy values: evidence file.", ""]
    for k, v in interp.items():
        if k not in ("Bottom line",):
            L += [f"**{k}.** {v}", ""]
    return "\n".join(L)


LEGACY_LABEL = ("LEGACY (historical reproduction): shipped social-desirability and CRT scores, which contain known "
                "scoring defects (180 and 450 people mis-scored). Do not use these values as current findings")


def save(rep: dict, md: str, out=OUT) -> None:
    out.mkdir(parents=True, exist_ok=True)
    slug = rep["name"].replace(" ", "_")
    json.dump(rep, open(out / f"{slug}.json", "w", encoding="utf-8"), indent=1, default=float)
    (out / f"{slug}.md").write_text(md, encoding="utf-8")
    print("wrote", out / f"{slug}.md")


def load_config() -> dict:
    return json.load(open(ROOT / "config/personas.json", encoding="utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--name", required=True)
    b.add_argument("--criteria", required=True)
    b.add_argument("--allow-party", action="store_true")
    b.add_argument("--out", default=str(ROOT / "reports/generated"), help="output folder")
    mode = b.add_mutually_exclusive_group()
    mode.add_argument("--corrected-scores", action="store_true",
                      help="(default) item-level re-scored social desirability and CRT; flag kept for compatibility")
    mode.add_argument("--legacy-scores", action="store_true",
                      help="HISTORICAL REPRODUCTION ONLY: shipped SD/CRT scores, which contain known scoring defects")
    sub.add_parser("select-p3")
    sub.add_parser("build-config")
    sub.add_parser("list-levels")
    a = ap.parse_args(argv)

    people = load_people()
    if a.cmd == "list-levels":
        for v in TIER_A + TIER_B:
            print(f"{v}{' (Tier B, needs --allow-party)' if v in TIER_B else ''}: {list(people[v].cat.categories)}")
        return 0
    green = load_green()
    if a.cmd == "build" and not a.legacy_scores:  # corrected scores are the default for new personas
        people, green = load_people(corrected=True), load_green(corrected=True)
    if a.cmd == "build":
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", a.name) or ".." in a.name:   # file-name safe, no paths
            print(f"ERROR: --name must use letters, digits, '_', '-', '.' only (got {a.name!r})", file=sys.stderr)
            return 2
        try:
            crit = parse_criteria(a.criteria, people, a.allow_party)
        except CriteriaError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        label = "SENSITIVITY PERSONA — uses self-reported party (Tier B), not census-observable" if "party" in crit else ""
        rep = build(a.name, crit, people, green, label)
        rep["scores"] = (LEGACY_LABEL if a.legacy_scores
                         else "CORRECTED (default): social desirability and CRT re-scored from items (final audit)")
        save(rep, to_markdown(rep), out=__import__("pathlib").Path(a.out))
        print(rep["status"])
        return 0
    cfg = load_config()
    if a.cmd == "select-p3":
        p1, p2 = (parse_criteria(cfg[k]["criteria"], people) for k in ("P1", "P2"))
        t = select_p3(people, p1, p2)
        RESULTS.mkdir(exist_ok=True)
        t.round(4).to_csv(RESULTS / "p3_selection.csv", index=False)
        print(t.head(10).round(3).to_string(index=False))
        return 0
    if a.cmd == "build-config":
        hold = pd.read_csv(RESULTS / "holdout_personas.csv") if (RESULTS / "holdout_personas.csv").exists() else None
        for key, p in cfg.items():
            crit = parse_criteria(p["criteria"], people, allow_party=p.get("allow_party", False))
            rep = build(p["name"], crit, people, green, p.get("label", ""))
            h = hold[hold.persona == p["name"]] if hold is not None else None
            interp = p.get("interpretation", {})
            # evidence file: every table (frozen original values + correction note); card: one-page summary
            ev = {k: v for k, v in interp.items() if k in ("Bottom line",)}
            note = ("FROZEN HISTORICAL ESTIMATES. Tables below use the " + LEGACY_LABEL + ". Corrected values for those two constructs follow the inner-layer table and are the ones cited "
                    "in the persona card and memo")
            (OUT / f"{p['name']}_evidence.md").write_text(to_markdown(rep, ev, h, scores_note=note), encoding="utf-8")
            pc, gc = load_people(corrected=True), load_green(corrected=True)   # for the corrected rows' shrinkage label
            rep_c = build(p["name"], parse_criteria(p["criteria"], pc, allow_party=p.get("allow_party", False)), pc, gc)
            save(rep, to_card(rep, interp, h, rep_c))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
