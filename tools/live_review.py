"""Simulate the live review: five unseen persona requests through the CLI (with --corrected-scores).

Writes reports/final_audit/live_review/<case>.md|json and prints a summary table used in live_review_simulation.md.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/final_audit/live_review"
SOUTH = "South (TX, OK, AR, LA, KY, TN, MS, AL, WV, DC, MD, DE, VA, NC, SC, GA, FL)"
CASES = [
    ("1_broad_women", "sex=Female", "broad group, sufficient evidence"),
    ("2_multi_south_grads_30_49", f"region={SOUTH}; education=College graduate/some postgrad|Postgraduate; age_band=30-49",
     "several demographic constraints"),
    ("3_small_unemployed_50_64", "employment=Unemployed; age_band=50-64", "small group: uncertainty should widen"),
    ("4_empty_retired_18_29", "age_band=18-29; employment=Retired", "empty group: must return INSUFFICIENT EVIDENCE"),
    ("5_prohibited_ideology", "ideology=Very liberal", "prohibited (survey-only) variable: must be rejected"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, crit, purpose in CASES:
        cmd = [sys.executable, "src/personas.py", "build", "--name", name, "--criteria", crit, "--corrected-scores",
               "--out", str(OUT.relative_to(ROOT))]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env={**os.environ, "PYTHONUTF8": "1"})
        dt = time.time() - t0
        row = dict(case=name, purpose=purpose, criteria=crit, exit_code=p.returncode, seconds=round(dt, 1),
                   stdout_last=(p.stdout.strip().splitlines() or [""])[-1], stderr=p.stderr.strip()[-300:])
        j = OUT / f"{name}.json"
        if p.returncode == 0 and j.exists():
            rep = json.load(open(j, encoding="utf-8"))
            row.update(status=rep["status"], n_total=rep["n_total"], n_train=rep["n_train"], n_test=rep["n_test"])
            if rep["status"] == "ok":
                row["inner"] = [dict(construct=r["construct"], typical=round(r["typical_shrunk"], 2),
                                     ci=f"{r['mean_ci_lo']:.2f}–{r['mean_ci_hi']:.2f}", d=round(r["d"], 2),
                                     d_ci=f"{r['d_lo']:+.2f}, {r['d_hi']:+.2f}", ci_width=round(r["mean_ci_hi"] - r["mean_ci_lo"], 2),
                                     pop_mean=round(r["pop_mean"], 2), confidence=r["confidence"]) for r in rep["inner"]]
                row["green_choice"] = [dict(condition=b["condition"], n=b["n"], rate=b["rate"], pop=round(b["pop_rate"], 2),
                                            status=b["status"]) for b in rep["green_choice"]]
        rows.append(row)
    json.dump(rows, open(OUT / "summary.json", "w", encoding="utf-8"), indent=1, default=float)
    print(json.dumps(rows, indent=1, default=float))


if __name__ == "__main__":
    main()
