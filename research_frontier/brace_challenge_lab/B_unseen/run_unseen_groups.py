"""Workstream B: stress-test the FROZEN persona generator on 25 unseen groups (+ supplementary probes).

- Calls the unchanged CLI `src/personas.py build` via subprocess (corrected scores, which is the default) and writes
  every output under this folder (outputs/, logs/).
- Independently recounts membership with the criteria AS THE USER MEANT THEM (duplicate variables = AND).
- "Held-out evaluation of frozen generator": scores the generator's train-built numbers on held-out members.
  This is pure evaluation. Nothing in the generator is tuned or selected on it.
- Separate training-only nested check (train split 70/30, seed 20261114) for one PROPOSED labelling fix.
  The fix is not applied to the generator.

Run:  PYTHONUTF8=1 python research_frontier/brace_challenge_lab/B_unseen/run_unseen_groups.py
Thresholds come from VALIDITY_CRITERIA.md (written before this script was run).
"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT, LOGS = HERE / "outputs", HERE / "logs"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "src"))
from common import CONSTRUCTS, SEED, TIER_A, TIER_B, load_green, load_people  # noqa: E402  (unchanged modules)
from personas import build, mask, parse_criteria  # noqa: E402

ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}
CONTINUOUS_MIN_DISTINCT = 10   # VALIDITY_CRITERIA §4
PERSONA_MASKS: dict = {}
SUPPLEMENTARY = [  # malformed-syntax / file-handling probes (not part of the 25)
    ("X1", "trailing_pipe", "age_band=65+|", "supplementary: malformed", "empty level after |"),
    ("X2", "extra_whitespace", "  age_band = 65+ ;  sex = Male ; ", "supplementary: formatting", "should be accepted"),
    ("X3", "probe/slash_in_name", "age_band=65+", "supplementary: file handling", "name with a path separator"),
    ("X4", "../X4_traversal_probe", "age_band=65+", "supplementary: file handling", "name with ../ (writes inside B_unseen)"),
    ("X5", "no_equals", "age_band", "supplementary: malformed", "missing ="),
]


def intended_members(text: str, people: pd.DataFrame):
    """Membership under the user's evident meaning: clauses are ANDed, a repeated variable intersects its level sets.
    Returns (mask or None, note)."""
    clauses = [c.strip() for c in text.split(";") if c.strip()]
    sets: dict[str, set] = {}
    for c in clauses:
        if "=" not in c:
            return None, "malformed"
        v, lv = (s.strip() for s in c.split("=", 1))
        if v not in people.columns or v not in TIER_A + TIER_B:
            return None, f"unknown variable {v}"
        lv = {x.strip() for x in lv.split("|")}
        if not lv <= set(people[v].cat.categories):
            return None, f"unknown level in {v}"
        sets[v] = sets[v] & lv if v in sets else lv
    m = pd.Series(True, index=people.index)
    for v, lv in sets.items():
        m &= people[v].astype(str).isin(lv)
    dup = len(clauses) != len(sets)
    return m, ("duplicate variable intersected" if dup else "")


def heldout_eval(rep, test, train):
    rows = {}
    te = test[mask(test, rep["criteria"])]
    for r in rep["inner"]:
        c = r["construct"]
        y = te[c].to_numpy()
        n = len(y)
        e = dict(n_test=n)
        if n >= 20:
            e_p, e_0 = np.abs(y - r["typical_shrunk"]), np.abs(y - r["pop_mean"])
            e["test_d"] = (y.mean() - r["pop_mean"]) / r["pop_sd"]
            e["mae_gain_pct"] = 100 * (e_0.mean() - e_p.mean()) / e_0.mean()
        ndist = train[c].nunique()
        if n >= 30 and ndist >= CONTINUOUS_MIN_DISTINCT:
            e["cov80"] = float(((y >= r["p10"]) & (y <= r["p90"])).mean())
            pq = train[c].quantile([.1, .9])
            e["cov80_pop_interval"] = float(((y >= pq[.1]) & (y <= pq[.9])).mean())
        rows[c] = e
    return rows


def triggers(rep, ev, people):
    w = []
    sh = rep["share_of_population"]
    if 30 <= rep["n_train"] < 60:
        w.append(f"T1 n_train={rep['n_train']}<60")
    if rep["n_test"] < 20:
        w.append(f"T2 n_test={rep['n_test']}<20 not evaluable")
    elif rep["n_test"] < 40:
        w.append(f"T2 n_test={rep['n_test']}<40 imprecise")
    if sh >= 0.90:
        w.append(f"T3 share={sh:.3f}>=0.90 (group ~ population)")
    for v, lv in rep["criteria"].items():
        for l in lv:
            k = int((people[v].astype(str) == l).sum())
            if k < 30:
                w.append(f"T4 rare level {v}={l} (panel n={k})")
    for r in rep["inner"]:
        c, lo, hi = r["construct"], *CONSTRUCTS[r["construct"]][2]
        rng = hi - lo
        lab = r["confidence"]
        if lab != "not distinguishable from population" and r["shrink_weight"] < 0.5:
            w.append(f"T5 {c}: '{lab}' but shrink weight {r['shrink_weight']:.2f}")
        if (r["mean_ci_hi"] - r["mean_ci_lo"]) > 0.25 * rng:
            w.append(f"T6 {c}: mean CI width {r['mean_ci_hi'] - r['mean_ci_lo']:.2f} > 25% of range")
        if (r["p90"] - r["p10"]) >= 0.8 * rng:
            w.append(f"T7 {c}: p10-p90 spans {(r['p90'] - r['p10']) / rng:.0%} of range")
        sd_shift = abs(r["typical_shrunk"] - r["pop_mean"]) / r["pop_sd"]
        if lab == "distinct" and sd_shift < 0.10:
            w.append(f"T9 {c}: 'distinct' (d={r['d']:+.2f}) but Typical only {sd_shift:.2f} SD from population")
        if not (r["mean_ci_lo"] <= r["typical_shrunk"] <= r["mean_ci_hi"]):
            w.append(f"T9 {c}: Typical {r['typical_shrunk']:.2f} outside raw-mean CI "
                     f"{r['mean_ci_lo']:.2f}-{r['mean_ci_hi']:.2f}")
        e = ev.get(c, {})
        if lab == "distinct" and "test_d" in e and np.sign(e["test_d"]) != np.sign(r["d"]) and abs(e["test_d"]) >= 0.10:
            w.append(f"T11 {c}: train d {r['d']:+.2f} vs held-out d {e['test_d']:+.2f}")
        if "cov80" in e and e["cov80"] < 0.65:
            w.append(f"T12 {c}: 80% coverage {e['cov80']:.2f}")
    # T10: overlap with submission personas. The 0.5 cut is the generator's own P3 overlap rule; it was set after the
    # first run because VALIDITY_CRITERIA.md named T10 without a number.
    m = mask(people, rep["criteria"])
    for key, pm in PERSONA_MASKS.items():
        ov = float((m & pm).sum() / max(m.sum(), 1))
        if ov >= 0.5:
            w.append(f"T10 overlap {ov:.0%} with {key}")
    # Observation (not a pre-set trigger): '% on other side of pop. median' ignores ties at the median
    tr = people[people.split == "train"]
    mt = m & (people.split == "train")
    for r in rep["inner"]:
        c = r["construct"]
        at = float((people.loc[mt, c] == tr[c].median()).mean())
        if at >= 0.25:
            w.append(f"RENDER {c}: {at:.0%} of members tied at pop. median; '% other side' = "
                     f"{r['share_opposite_side_of_pop_median']:.0%} omits them")
    for b in rep["green_choice"]:
        if b["status"] == "ok" and b["n"] < 40:
            w.append(f"T8 behaviour {b['condition']} n={b['n']}<40")
    return w


def run_cli(gid, name, crit):
    slug = f"{gid}_{name}" if not name.startswith(("..", "probe/")) else name
    cmd = [sys.executable, str(ROOT / "src/personas.py"), "build", "--name", slug, "--criteria", crit, "--out", str(OUT)]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=ENV)
    dt = time.time() - t0
    (LOGS / f"{gid}.stdout.txt").write_text(p.stdout, encoding="utf-8")
    (LOGS / f"{gid}.stderr.txt").write_text(p.stderr, encoding="utf-8")
    jpath = (OUT / f"{slug.replace(' ', '_')}.json").resolve()
    return p, dt, jpath


def nested_training_check(groups, people, green):
    """PROPOSAL (not applied): label 'distinct' only if the SHRUNKEN d is >= 0.20 and the raw CI excludes 0.
    Validated on the TRAIN split only: inner 70/30 split of train with seed 20261114. The generator's build() is
    called unchanged, with inner-train relabelled 'train' and inner-validation relabelled 'test'."""
    tr = people[people.split == "train"].copy()
    rng = np.random.default_rng(SEED)
    pids = tr.pid.to_numpy().copy()
    rng.shuffle(pids)
    inner_tr = set(pids[: int(round(0.7 * len(pids)))])
    tr["split"] = np.where(tr.pid.isin(inner_tr), "train", "test")
    g = green[green.pid.isin(tr.pid)].drop(columns="split").merge(tr[["pid", "split"]], on="pid")
    rows = []
    for gid, name, crit, cat, _ in groups:
        try:
            cr = parse_criteria(crit, tr)
        except Exception:
            continue
        rep = build(name, cr, tr, g)
        if rep["status"] != "ok":
            continue
        val = tr[(tr.split == "test") & mask(tr, cr)]
        if len(val) < 20:
            continue
        for r in rep["inner"]:
            c = r["construct"]
            vd = (val[c].mean() - r["pop_mean"]) / r["pop_sd"]
            sd_shrunk = (r["typical_shrunk"] - r["pop_mean"]) / r["pop_sd"]
            cur = r["confidence"] == "distinct"
            prop = cur and abs(sd_shrunk) >= 0.20
            rows.append(dict(id=gid, construct=c, inner_n_train=rep["n_train"], inner_n_val=len(val), d=r["d"],
                             shrunk_d=sd_shrunk, w=r["shrink_weight"], current_distinct=cur, proposed_distinct=prop,
                             val_d=vd, same_sign_ge_0p10=bool(np.sign(vd) == np.sign(r["d"]) and abs(vd) >= 0.10)))
    return pd.DataFrame(rows)


def main():
    for d in (OUT, LOGS):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    people, green = load_people(corrected=True), load_green(corrected=True)
    train, test = people[people.split == "train"], people[people.split == "test"]
    cfg = json.load(open(ROOT / "config/personas.json", encoding="utf-8"))
    PERSONA_MASKS.update({k: mask(people, parse_criteria(v["criteria"], people)) for k, v in cfg.items()})
    groups =list(csv.reader(open(HERE / "groups.csv", encoding="utf-8")))[1:]
    rows, inner_rows = [], []
    for gid, name, crit, cat, why in groups + SUPPLEMENTARY:
        p, dt, jpath = run_cli(gid, name, crit)
        row = dict(id=gid, name=name, criteria=crit, category=cat, exit_code=p.returncode, seconds=round(dt, 1),
                   traceback="Traceback" in p.stderr, stderr=p.stderr.strip().replace("\n", " | ")[:600],
                   stdout_last=(p.stdout.strip().splitlines() or [""])[-1])
        im, note = intended_members(crit, people)
        if im is not None:
            row.update(intended_n_total=int(im.sum()), intended_n_train=int((im & (people.split == "train")).sum()),
                       intended_n_test=int((im & (people.split == "test")).sum()))
        row["intended_note"] = note
        warns = []
        if p.returncode == 0 and jpath.exists():
            rep = json.load(open(jpath, encoding="utf-8"))
            if gid.startswith("X4"):  # move the escaped file back under outputs/ for tidiness (recorded)
                row["wrote_outside_out_dir"] = str(jpath.relative_to(HERE))
                warns.append(f"FILE: --name with '../' wrote {jpath.relative_to(HERE)} outside --out (path traversal)")
                esc = OUT / "escaped"
                esc.mkdir(exist_ok=True)
                for ext in (".json", ".md"):
                    shutil.move(str(jpath.with_suffix(ext)), esc / jpath.with_suffix(ext).name)
            row.update(status=rep["status"], generator_definition=rep["definition"], train_n=rep["n_train"],
                       test_n=rep["n_test"], n_total=rep["n_total"], share=round(rep["share_of_population"], 4))
            if im is not None and int(im.sum()) != rep["n_total"]:
                warns.append(f"SILENT MEMBERSHIP MISMATCH: generator n={rep['n_total']} vs intended n={int(im.sum())} "
                             f"(generator definition '{rep['definition']}')")
            if rep["status"] == "ok":
                ev = heldout_eval(rep, test, train)
                warns += triggers(rep, ev, people)
                for r in rep["inner"]:
                    c, e = r["construct"], ev[r["construct"]]
                    row[f"{c}_d"] = round(r["d"], 3)
                    row[f"{c}_d_ci"] = f"{r['d_lo']:+.2f},{r['d_hi']:+.2f}"
                    row[f"{c}_w"] = round(r["shrink_weight"], 3)
                    row[f"{c}_label"] = r["confidence"]
                    row[f"{c}_heldout_d"] = round(e["test_d"], 3) if "test_d" in e else ""
                    row[f"{c}_mae_gain_pct"] = round(e["mae_gain_pct"], 2) if "mae_gain_pct" in e else ""
                    row[f"{c}_cov80"] = round(e["cov80"], 3) if "cov80" in e else ""
                for b in rep["green_choice"]:
                    row[f"beh_{b['condition']}_n"] = b["n"]
                    row[f"beh_{b['condition']}_status"] = b["status"]
                    row[f"beh_{b['condition']}_rate"] = round(b["rate"], 3) if b["n"] else ""
            md = jpath.with_suffix(".md")
            mdtxt = md.read_text(encoding="utf-8") if md.exists() else ""
            if re.search(r"\bnan\b", mdtxt, flags=re.IGNORECASE):
                warns.append("RENDER: 'nan' string in generated markdown")
        # verdict
        if row.get("traceback") or any(x.startswith("SILENT") for x in warns):
            verdict = "error"
        elif p.returncode != 0 or row.get("status", "").startswith("INSUFFICIENT"):
            verdict = "abstain"
        elif any(not x.startswith(("T2", "RENDER")) for x in warns):  # RENDER = generator-wide display issue
            verdict = "warn"
        else:
            verdict = "valid"
        row["warnings"] = " ; ".join(warns)
        row["verdict"] = verdict
        rows.append(row)
        print(f"{gid} exit={p.returncode} {row.get('status', '')[:40]:40s} verdict={verdict} warns={len(warns)}")
    df = pd.DataFrame(rows)
    df[df.id.str.startswith("G")].to_csv(HERE / "UNSEEN_GROUP_TESTS.csv", index=False)
    df[df.id.str.startswith("X")].to_csv(HERE / "supplementary_probes.csv", index=False)
    nest = nested_training_check(groups, people, green)
    nest.round(4).to_csv(HERE / "nested_training_label_check.csv", index=False)
    if len(nest):
        for col in ("current_distinct", "proposed_distinct"):
            s = nest[nest[col]]
            print(f"[nested, train-only] {col}: n={len(s)} replicate(same sign, |d|>=0.10)={s.same_sign_ge_0p10.mean():.2f}")


if __name__ == "__main__":
    main()
