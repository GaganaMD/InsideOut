"""Final independent audit: scale verification, reliability, integrity checks, corrected-score reruns.

Original (frozen) results in results/ and reports/personas/ are NOT modified. Corrected-score analyses are written to
reports/final_audit/ next to the originals so every changed number has a documented reason.

Exploratory/audit status: the corrected reruns re-evaluate the SAME pre-registered models and SAME persona definitions
with corrected measurement; nothing is selected or tuned on the (already inspected) holdout.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONSTRUCTS, RAW_TWIN, ROOT, SD_FALSE_KEYED, SD_TRUE_KEYED, SEED, TIER_A, TIER_B,  # noqa: E402
                    load_green, load_people, low_income, rescore_sd_crt, rescore_st_tw)
from personas import build, load_config, mask, parse_criteria, select_p3  # noqa: E402
from predictability import cv_eval, model  # noqa: E402

OUT = ROOT / "reports/final_audit"
CAT = RAW_TWIN / "question_catalog_and_human_response_csv"
AFFECTED = ["social_desirability", "crt"]


# ----------------------------------------------------------------------------- 1. scale verification
def scale_verification() -> pd.DataFrame:
    num = pd.read_csv(CAT / "wave1_3_response.csv", low_memory=False)
    s = pd.read_parquet(ROOT / "data/processed/scores.parquet")
    rows = []

    def add(name, shipped_col, item_score, rule, bug_rule=None, bug_score=None):
        m = num[["pid"]].assign(item=item_score.to_numpy()).merge(s[["pid", shipped_col]], on="pid")
        r = dict(construct=name, shipped_column=shipped_col, scoring_rule=rule, n=len(m),
                 exact_match=float(np.isclose(m.item, m[shipped_col], atol=1e-9).mean()),
                 n_mismatch=int((~np.isclose(m.item, m[shipped_col], atol=1e-9)).sum()),
                 corr=float(m.item.corr(m[shipped_col])))
        if bug_score is not None:
            b = bug_score.merge(s[["pid", shipped_col]], on="pid")
            r["shipped_reproduced_by"] = bug_rule
            r["bug_rule_exact_match"] = float((b.bug == b[shipped_col]).mean())
        rows.append(r)

    g = num[[f"QID235_{i}" for i in range(1, 7)]].mean(axis=1)
    add("green", "w1_score_GREEN", g, "mean QID235_1-6 (all pro-environment, 1-5)")
    n = num[[f"QID25_{i}" for i in (4, 9, 14, 19, 24, 29, 34, 39)]].copy()
    for i in (9, 24, 34):
        n[f"QID25_{i}"] = 6 - n[f"QID25_{i}"]
    add("neuroticism", "w1_score_neuroticism", n.mean(axis=1), "BFI-44 N: mean items 4,9R,14,19,24R,29,34R,39")
    st = rescore_st_tw().set_index("pid").loc[num.pid].st_tw_rescored
    raw31 = num.QID31.where(~num.QID31.isin([6, 11]), 0)  # shipped behaviour: text-labelled options 6, 11 -> 0
    bug = pd.DataFrame({"pid": num.pid, "bug": raw31 + num.QID32 + (6 - num.QID33) + (6 - num.QID34)})
    add("spendthrift", "w3_score_ST-TW", st, "Q31+Q32+(6-Q33)+(6-Q34)", "QID31 options 6 and 11 scored 0", bug)
    rs = rescore_sd_crt().set_index("pid").loc[num.pid]
    raw2 = pd.read_csv(RAW_TWIN / "raw_data/wave_2_labels_anonymized.csv", low_memory=False).iloc[2:].copy()
    raw2["pid"] = pd.to_numeric(raw2.TWIN_ID, errors="coerce")
    c = lambda i: raw2[f"Social Desirability_{i}"].astype(str)
    sdbug = sum((c(i) == "TRUE").astype(int) for i in SD_TRUE_KEYED) + sum((c(i) == "FALSE").astype(int) for i in SD_FALSE_KEYED)
    add("social_desirability", "w2_score_socialdesirability", rs.sd_rescored,
        "Reynolds Form C count, TRUE-keyed 5,7,9,10,13; FALSE-keyed rest; case-insensitive",
        "case-sensitive match on 'TRUE'/'FALSE' (178 exports read 'True'/'False')",
        pd.DataFrame({"pid": raw2.pid, "bug": sdbug}))
    raw1 = pd.read_csv(RAW_TWIN / "raw_data/wave_1_labels_anonymized.csv", low_memory=False).iloc[2:].copy()
    raw1["pid"] = pd.to_numeric(raw1.TWIN_ID, errors="coerce")
    t = lambda col: raw1[col].astype(str).str.strip()
    crtbug = (t("CRT 1") == "Emily").astype(int) + (t("CRT 2") == "0").astype(int) + (t("CRT 3") == "2").astype(int) \
        + (t("CRT4") == "8").astype(int)
    add("crt", "w1_crt2_score", rs.crt_rescored, "CRT-2: emily (case-insens.), 0, 2, 8 (numeric)",
        "case-sensitive 'Emily' and exact strings '0','2','8' ('8.0'/'emily' marked wrong)",
        pd.DataFrame({"pid": raw1.pid, "bug": crtbug}))
    add("dictator_give", "w3_score_dictator_sender", (6 - num.QID231) * 20, "(6 - QID231 code) x 20 = % of $5 sent")
    return pd.DataFrame(rows)


def misscore_by_age() -> pd.DataFrame:
    p = load_people(False)[["pid", "age_band", "social_desirability", "crt"]]
    c = load_people(True)[["pid", "social_desirability", "crt"]]
    m = p.merge(c, on="pid", suffixes=("_shipped", "_corrected"))
    out = []
    for k in AFFECTED:
        m[f"{k}_wrong"] = m[f"{k}_shipped"] != m[f"{k}_corrected"]
        m[f"{k}_bias"] = m[f"{k}_shipped"] - m[f"{k}_corrected"]
    for band, g in m.groupby("age_band", observed=True):
        out.append(dict(age_band=band, n=len(g), **{f"{k}_share_misscored": g[f"{k}_wrong"].mean() for k in AFFECTED},
                        **{f"{k}_mean_bias": g[f"{k}_bias"].mean() for k in AFFECTED}))
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------- 2. reliability
def kr20_alpha(items: pd.DataFrame) -> float:
    k = items.shape[1]
    return float(k / (k - 1) * (1 - items.var(ddof=1).sum() / items.sum(axis=1).var(ddof=1)))


def reliability() -> pd.DataFrame:
    num = pd.read_csv(CAT / "wave1_3_response.csv", low_memory=False)
    lab = pd.read_csv(CAT / "wave1_3_response_label.csv", low_memory=False)
    n = num[[f"QID25_{i}" for i in (4, 9, 14, 19, 24, 29, 34, 39)]].copy()
    for i in (9, 24, 34):
        n[f"QID25_{i}"] = 6 - n[f"QID25_{i}"]
    true = pd.DataFrame({i: lab[f"QID27_{i}"].astype(str).str.upper().eq("TRUE").astype(int) for i in range(1, 14)})
    sd = pd.concat([true[SD_TRUE_KEYED], 1 - true[SD_FALSE_KEYED]], axis=1)
    numc = lambda col: pd.to_numeric(lab[col], errors="coerce")
    crt = pd.DataFrame({"a": lab.QID52_TEXT.astype(str).str.strip().str.lower().str.rstrip(".").eq("emily").astype(int),
                        "b": (numc("QID53_TEXT") == 0).astype(int), "c": (numc("QID54_TEXT") == 2).astype(int),
                        "d": (numc("QID55_TEXT") == 8).astype(int)})
    st = pd.DataFrame({"q31": num.QID31, "q32": num.QID32, "q33": 6 - num.QID33, "q34": 6 - num.QID34})
    st = (st - st.mean()) / st.std()
    rows = [("green", kr20_alpha(num[[f"QID235_{i}" for i in range(1, 7)]]), 6, "Cronbach alpha"),
            ("neuroticism", kr20_alpha(n), 8, "Cronbach alpha"),
            ("social_desirability (corrected)", kr20_alpha(sd), 13, "KR-20"),
            ("crt (corrected)", kr20_alpha(crt), 4, "KR-20"),
            ("spendthrift", kr20_alpha(st), 4, "alpha on standardised items (mixed 11-/5-point)"),
            ("dictator_give", np.nan, 1, "single item: reliability not estimable")]
    return pd.DataFrame(rows, columns=["construct", "reliability", "n_items", "method"])


# ----------------------------------------------------------------------------- 3. integrity checks
def integrity() -> dict:
    p = load_people(False)
    split = pd.read_csv(ROOT / "data/split.csv")
    cfg = load_config()
    crit_vars = {k: list(parse_criteria(v["criteria"], p)) for k, v in cfg.items()}
    g = load_green(False)
    raw = pd.read_parquet(ROOT / "data/processed/mega_default_eric.parquet")
    log = subprocess.run(["git", "log", "--format=%h %s", "8104628..HEAD", "--", "src/predictability.py",
                          "src/saydo.py", "src/holdout.py", "data/split.csv", "hypotheses.md", "config/personas.json"],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip().splitlines()
    fit = smf.logit("chose_green ~ green_z * green_default + low_inc",
                    g[g.split == "train"].assign(green_z=lambda d: (d.green - d.green.mean()) / d.green.std(),
                                                 low_inc=lambda d: low_income(d.income).astype(int))).fit(disp=0)
    sd_json = json.load(open(ROOT / "results/saydo.json"))
    or_reported = next(t["OR"] for t in sd_json["primary"] if t["term"] == "green_z")
    return {
        "people_unique_pid": bool(p.pid.is_unique), "n_people": len(p),
        "split_disjoint_and_complete": bool(split.pid.is_unique and set(split.pid) == set(p.pid)),
        "split_counts": split.split.value_counts().to_dict(),
        "persona_criteria_variables": crit_vars,
        "persona_criteria_tier_a_only": all(set(v) <= set(TIER_A) for v in crit_vars.values()),
        "green_rows": len(g), "green_condition_counts": g.green_condition.value_counts().to_dict(),
        "green_each_person_one_condition": bool(raw.pid.is_unique),
        "commits_touching_models_split_hypotheses_config_after_holdout_script": log,
        "saydo_OR_green_recomputed": float(np.exp(fit.params["green_z"])), "saydo_OR_green_reported": or_reported,
    }


# ----------------------------------------------------------------------------- 4. corrected reruns
def corrected_reruns() -> dict:
    out = {}
    orig = pd.read_csv(ROOT / "results/predictability_map.csv")
    pc = load_people(True)
    tr, te = pc[pc.split == "train"].reset_index(drop=True), pc[pc.split == "test"]
    rows = []
    for c in AFFECTED:
        r = cv_eval(tr, c, TIER_A)
        o = orig[(orig.construct == c) & (orig.features == "TierA")].iloc[0]
        m = model(TIER_A).fit(tr[TIER_A].astype(str), tr[c])
        y, base = te[c].to_numpy(), tr[c].mean()
        test_r2 = 1 - ((y - m.predict(te[TIER_A].astype(str))) ** 2).sum() / ((y - base) ** 2).sum()
        rows.append(dict(construct=c, cv_r2_original=o.cv_r2, cv_r2_corrected=r["cv_r2"],
                         cv_r2_corrected_lo=r["cv_r2_lo"], cv_r2_corrected_hi=r["cv_r2_hi"],
                         mae_gain_pct_corrected=r["mae_gain_pct"], test_r2_corrected=test_r2))
    out["predictability"] = pd.DataFrame(rows)
    po = load_people(False)
    trs = po[po.split == "train"]
    ag = []
    for c in AFFECTED:
        for band in ["18-29", "30-49", "50-64", "65+"]:
            ag.append(dict(construct=c, age_band=band, mean_original=trs[trs.age_band == band][c].mean(),
                           mean_corrected=tr[tr.age_band == band][c].mean()))
    out["age_means"] = pd.DataFrame(ag)

    # personas: same definitions, train-built, corrected SD/CRT; holdout comparison with the same code path
    hold_orig = pd.read_csv(ROOT / "results/holdout_personas.csv")
    green_c = load_green(True)
    rng = np.random.default_rng(SEED)
    prow = []
    for key, p in load_config().items():
        crit = parse_criteria(p["criteria"], pc)
        rep = build(p["name"], crit, pc, green_c)
        tem = te[mask(te, crit)]
        for r in rep["inner"]:
            if r["construct"] not in AFFECTED:
                continue
            y = tem[r["construct"]].to_numpy()
            e_p, e_0 = np.abs(y - r["typical_shrunk"]), np.abs(y - r["pop_mean"])
            boots = rng.choice(e_0 - e_p, size=(2000, len(y)), replace=True).mean(axis=1)
            ho = hold_orig[(hold_orig.persona == p["name"]) & (hold_orig.construct == r["construct"])].iloc[0]
            prow.append(dict(persona=p["name"], construct=r["construct"], d_train_original=ho.train_d,
                             d_train_corrected=r["d"], d_lo_corrected=r["d_lo"], d_hi_corrected=r["d_hi"],
                             confidence_corrected=r["confidence"], d_test_original=ho.test_d,
                             d_test_corrected=(y.mean() - r["pop_mean"]) / r["pop_sd"],
                             gain_pct_original=ho.gain_pct, gain_pct_corrected=100 * (e_0.mean() - e_p.mean()) / e_0.mean(),
                             gain_lo_corrected=float(np.quantile(boots, .025)), gain_hi_corrected=float(np.quantile(boots, .975)),
                             cov_corrected=float(((y >= r["p10"]) & (y <= r["p90"])).mean()),
                             typical_corrected=r["typical_shrunk"], p10_corrected=r["p10"], p90_corrected=r["p90"]))
    out["personas"] = pd.DataFrame(prow)
    cfg = load_config()
    p1, p2 = (parse_criteria(cfg[k]["criteria"], pc) for k in ("P1", "P2"))
    sel = select_p3(pc, p1, p2)
    out["p3_rule_top_corrected"] = sel.head(3)[["definition", "n_train", "mean_abs_d"]].to_dict("records")
    # say-do SD sensitivity with corrected SD
    g = green_c[green_c.split == "train"].copy()
    g["green_z"] = (g.green - g.green.mean()) / g.green.std()
    g["low_inc"] = low_income(g.income).astype(int)
    g["sd_z"] = (g.social_desirability - g.social_desirability.mean()) / g.social_desirability.std()
    f = smf.logit("chose_green ~ green_z * green_default + low_inc + sd_z", g).fit(disp=0)
    out["saydo_sd_sensitivity_corrected"] = {k: float(np.exp(f.params[k])) for k in ("green_z", "sd_z")}
    # P1 neuroticism gap adjusted for corrected SD (memo claim: -0.50 -> -0.32 with shipped SD)
    t = tr.assign(neu_z=(tr.neuroticism - tr.neuroticism.mean()) / tr.neuroticism.std(),
                  sd_z=(tr.social_desirability - tr.social_desirability.mean()) / tr.social_desirability.std(),
                  old=(tr.age_band == "65+").astype(int))
    fa = smf.ols("neu_z ~ old + sd_z", t).fit()
    out["p1_neuroticism_sd_adjusted_corrected"] = dict(est=float(fa.params.old), lo=float(fa.conf_int().loc["old", 0]),
                                                       hi=float(fa.conf_int().loc["old", 1]),
                                                       corr_sd_neuroticism=float(tr.social_desirability.corr(tr.neuroticism)))
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sv = scale_verification()
    sv.round(4).to_csv(OUT / "scale_verification.csv", index=False)
    mb = misscore_by_age()
    mb.round(4).to_csv(OUT / "misscoring_by_age.csv", index=False)
    rel = reliability()
    rel.round(3).to_csv(OUT / "reliability.csv", index=False)
    chk = integrity()
    json.dump(chk, open(OUT / "integrity_checks.json", "w"), indent=1, default=str)
    cr = corrected_reruns()
    cd = OUT / "corrected_scores"
    cd.mkdir(exist_ok=True)
    cr["predictability"].round(4).to_csv(cd / "predictability_sd_crt.csv", index=False)
    cr["age_means"].round(3).to_csv(cd / "age_band_means_sd_crt.csv", index=False)
    cr["personas"].round(4).to_csv(cd / "personas_sd_crt.csv", index=False)
    json.dump({k: cr[k] for k in ("p3_rule_top_corrected", "saydo_sd_sensitivity_corrected",
                                  "p1_neuroticism_sd_adjusted_corrected")}, open(cd / "other.json", "w"), indent=1, default=float)
    pd.set_option("display.width", 250)
    print(sv.round(3).to_string(index=False)); print(mb.round(3).to_string(index=False)); print(rel.round(3).to_string(index=False))
    print(json.dumps(chk, indent=1, default=str))
    for k in ("predictability", "age_means", "personas"):
        print(cr[k].round(3).to_string(index=False))
    print(json.dumps({k: cr[k] for k in ("p3_rule_top_corrected", "saydo_sd_sensitivity_corrected",
                                         "p1_neuroticism_sd_adjusted_corrected")}, indent=1, default=float))


if __name__ == "__main__":
    main()
