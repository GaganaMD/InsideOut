"""One command: download -> audit/split check -> predictability -> say-do -> P3 selection -> holdout -> personas -> tests.

    python run_all.py            # full pipeline (~5 min after the first download)
    python run_all.py --skip-download
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    ["src/download.py"],
    ["src/audit.py"],
    ["src/predictability.py"],
    ["src/saydo.py"],
    ["src/personas.py", "select-p3"],
    ["src/holdout.py"],
    ["src/personas.py", "build-config"],
    ["src/personas.py", "build", "--name", "sensitivity_party_republican", "--criteria", "party=Republican",
     "--allow-party", "--out", "reports/sensitivity"],
    ["src/exploratory_values.py"],  # EXPLORATORY follow-up; train split only; writes reports/exploratory/
    ["src/exploratory_redistribution.py"],  # EXPLORATORY follow-up #2; train only; reports/exploratory/redistribution/
    ["src/robust_demographics.py"],  # EXPLORATORY robustness; train only; reports/robustness/
    ["src/robust_personas.py"],  # EXPLORATORY robustness; train only; reports/robustness/
    ["src/final_audit.py"],  # final audit: scale verification + corrected-score reruns; reports/final_audit/
]


def main() -> int:
    env = {**os.environ, "PYTHONUTF8": "1"}
    steps = STEPS[1:] if "--skip-download" in sys.argv else STEPS
    for s in steps:
        print(f"\n=== {' '.join(s)}", flush=True)
        r = subprocess.run([sys.executable, *s], cwd=ROOT, env=env)
        if r.returncode:
            print(f"FAILED: {' '.join(s)}")
            return r.returncode
    print("\n=== tests")
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=ROOT, env=env).returncode


if __name__ == "__main__":
    sys.exit(main())
