"""EXPLORATORY robustness #2: persona stability under one-criterion changes. TRAIN split only (via personas.build).

For each submission persona, each variant changes exactly one demographic criterion (narrow, widen, shift, or
drop/add one condition). For every construct we compare the variant's d (vs train population) and its
confidence class with the original persona. Original persona files are not touched; outputs go to
reports/robustness/persona_stability/.

A construct conclusion is 'stable' for a persona if, across all variants with sufficient n, the sign of d matches the
original and the variant's 95% CI for d excludes 0 whenever the original was classed 'distinct'.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONSTRUCTS, ROOT, load_green, load_people  # noqa: E402
from personas import build, load_config, parse_criteria  # noqa: E402

OUT = ROOT / "reports/robustness/persona_stability"
LOW = "Less than $30,000|$30,000-$50,000"
VARIANTS = {
    "P1": [
        ("shift age: 50-64", "age_band=50-64"),
        ("widen age: 50+", "age_band=50-64|65+"),
        ("add: retired only", "age_band=65+; employment=Retired"),
        ("add: income < $50k", f"age_band=65+; income={LOW}"),
        ("add: college degree", "age_band=65+; education=College graduate/some postgrad|Postgraduate"),
    ],
    "P2": [
        ("narrow age: 18-29", f"age_band=18-29; income={LOW}"),
        ("narrow age: 30-49", f"age_band=30-49; income={LOW}"),
        ("widen age: 18-64", f"age_band=18-29|30-49|50-64; income={LOW}"),
        ("narrow income: < $30k", "age_band=18-29|30-49; income=Less than $30,000"),
        ("widen income: < $75k", f"age_band=18-29|30-49; income={LOW}|$50,000-$75,000"),
        ("drop income criterion", "age_band=18-29|30-49"),
    ],
    "P3": [
        ("drop marital criterion", "age_band=18-29"),
        ("shift age: 30-49", "age_band=30-49; marital=Never been married"),
        ("drop age criterion", "marital=Never been married"),
        ("widen marital: + living with partner", "age_band=18-29; marital=Never been married|Living with a partner"),
        ("add: male", "age_band=18-29; marital=Never been married; sex=Male"),
        ("add: female", "age_band=18-29; marital=Never been married; sex=Female"),
    ],
}


def flat(rep: dict, key: str, variant: str, criteria: str) -> list[dict]:
    rows = []
    beh = {b["condition"]: b for b in rep.get("green_choice", [])}
    for r in rep.get("inner", []):
        rows.append(dict(persona=key, variant=variant, criteria=criteria, status=rep["status"], n_train=rep["n_train"],
                         construct=r["construct"], d=r["d"], d_lo=r["d_lo"], d_hi=r["d_hi"],
                         confidence=r["confidence"], typical=r["typical_shrunk"],
                         green_n_grey=beh.get("grey_default", {}).get("n"), green_n_green=beh.get("green_default", {}).get("n")))
    if not rows:
        rows.append(dict(persona=key, variant=variant, criteria=criteria, status=rep["status"], n_train=rep["n_train"]))
    return rows


def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    people, green = load_people(), load_green()
    cfg = load_config()
    rows = []
    for key, variants in VARIANTS.items():
        base = cfg[key]
        rep = build(base["name"], parse_criteria(base["criteria"], people), people, green)
        rows += flat(rep, key, "ORIGINAL", base["criteria"])
        for label, crit in variants:
            rows += flat(build(f"{key}:{label}", parse_criteria(crit, people), people, green), key, label, crit)
    df = pd.DataFrame(rows)
    orig = df[df.variant == "ORIGINAL"].set_index(["persona", "construct"])
    var = df[(df.variant != "ORIGINAL") & (df.status == "ok")].copy()
    var["orig_d"] = [orig.loc[(p, c), "d"] for p, c in zip(var.persona, var.construct)]
    var["orig_conf"] = [orig.loc[(p, c), "confidence"] for p, c in zip(var.persona, var.construct)]
    var["same_sign"] = np.sign(var.d) == np.sign(var.orig_d)
    var["ci_excl_0"] = (var.d_lo > 0) | (var.d_hi < 0)
    var["abs_change_d"] = (var.d - var.orig_d).abs()
    summ = []
    for (p, c), g in var.groupby(["persona", "construct"]):
        oc = orig.loc[(p, c), "confidence"]
        if oc == "distinct":
            stable = bool((g.same_sign & g.ci_excl_0).all())
            rule = "sign kept and CI excludes 0 in every variant"
        else:
            stable = bool((~((g.d.abs() >= 0.2) & g.ci_excl_0)).all())
            rule = "no variant turns it into a distinct (|d|>=0.2, CI excl. 0) difference"
        summ.append(dict(persona=p, construct=c, original_confidence=oc, original_d=orig.loc[(p, c), "d"],
                         n_variants=len(g), sign_kept=int(g.same_sign.sum()), ci_excl_0=int(g.ci_excl_0.sum()),
                         d_min=g.d.min(), d_max=g.d.max(), max_abs_change=g.abs_change_d.max(),
                         stable=stable, stability_rule=rule))
    return df, pd.DataFrame(summ)


def cli_checks() -> list[dict]:
    """Exercise the CLI with newly specified criteria (outputs to reports/robustness/cli_examples)."""
    out = OUT.parent / "cli_examples"
    cases = [
        ("new_group_west_women_college", "region=West (WA, OR, ID, MT, WY, CA, NV, UT, CO, AZ, NM); sex=Female; "
                                         "education=College graduate/some postgrad|Postgraduate", [], 0, "ok"),
        ("new_group_single_hh_retired", "hh_size=1; employment=Retired", [], 0, None),
        ("new_group_tiny", "age_band=18-29; employment=Retired", [], 0, "INSUFFICIENT"),
        ("rejected_party", "party=Democrat", [], 2, None),
        ("rejected_ideology", "ideology=Liberal", [], 2, None),
        ("rejected_bad_level", "age_band=40-60", [], 2, None),
        ("sensitivity_party", "party=Democrat", ["--allow-party"], 0, "ok"),
    ]
    res = []
    for name, crit, extra, want_code, want_status in cases:
        p = subprocess.run([sys.executable, str(ROOT / "src/personas.py"), "build", "--name", name, "--criteria", crit,
                            "--out", str(out), *extra], cwd=ROOT, capture_output=True, text=True,
                           env={**__import__("os").environ, "PYTHONUTF8": "1"})
        status = (p.stdout.strip().splitlines() or [""])[-1]
        ok = p.returncode == want_code and (want_status is None or status.startswith(want_status))
        res.append(dict(case=name, criteria=crit, extra=" ".join(extra), exit_code=p.returncode, expected_exit=want_code,
                        last_line=status if p.returncode == 0 else p.stderr.strip()[:160], passed=ok))
    return res


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df, summ = run()
    df.round(4).to_csv(OUT / "variants_long.csv", index=False)
    summ.round(4).to_csv(OUT / "stability_summary.csv", index=False)
    cli = cli_checks()
    pd.DataFrame(cli).to_csv(OUT / "cli_checks.csv", index=False)

    L = ["# EXPLORATORY robustness: persona stability under one-criterion changes", "",
         "> Exploratory, **training split only** (built with the same generator as the personas). The original "
         "personas, their estimates and the holdout are untouched. Nothing here is used to re-tune them.", "",
         "## Variants and sample sizes", "", "| Persona | Variant | Criteria | n train | Green-choice n (grey / green default) | Status |",
         "|---|---|---|---|---|---|"]
    for (p, v), g in df.groupby(["persona", "variant"], sort=False):
        r = g.iloc[0]
        gn = "–" if pd.isna(r.get("green_n_grey")) else f"{int(r.green_n_grey)} / {int(r.green_n_green)}"
        flag = " ⚠ behaviour < 20/cell" if gn != "–" and min(int(r.green_n_grey), int(r.green_n_green)) < 20 else ""
        L.append(f"| {p} | {v} | `{r.criteria}` | {int(r.n_train)} | {gn}{flag} | {r.status} |")
    L += ["", "## Stability of each construct conclusion", "",
          "| Persona | Construct | Original (d, class) | d range across variants | Sign kept | CI excludes 0 | Stable? |",
          "|---|---|---|---|---|---|---|"]
    for _, s in summ.iterrows():
        L.append(f"| {s.persona} | {s.construct} | {s.original_d:+.2f}, {s.original_confidence} | "
                 f"{s.d_min:+.2f} to {s.d_max:+.2f} | {s.sign_kept}/{s.n_variants} | {s.ci_excl_0}/{s.n_variants} | "
                 f"{'**yes**' if s.stable else 'no'} |")
    L += ["", "*Stable* means: for an originally *distinct* construct, the sign is kept and the CI excludes 0 in "
          "every variant. For other constructs, no variant turns them into a distinct difference.", "",
          "## CLI with newly specified criteria", "", "| Case | Criteria | Exit (expected) | Result | Pass |",
          "|---|---|---|---|---|"]
    for c in cli:
        L.append(f"| {c['case']} | `{c['criteria']}` {c['extra']} | {c['exit_code']} ({c['expected_exit']}) | "
                 f"{c['last_line'][:90]} | {'✓' if c['passed'] else '✗'} |")
    (OUT / "persona_stability.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(summ[["persona", "construct", "original_confidence", "original_d", "d_min", "d_max", "sign_kept",
                "ci_excl_0", "n_variants", "stable"]].round(2).to_string(index=False))
    print(df.groupby(["persona", "variant"], sort=False).agg(n=("n_train", "first"), g1=("green_n_grey", "first"),
                                                            g2=("green_n_green", "first")).to_string())
    print(pd.DataFrame(cli)[["case", "exit_code", "expected_exit", "passed", "last_line"]].to_string(index=False))


if __name__ == "__main__":
    main()
