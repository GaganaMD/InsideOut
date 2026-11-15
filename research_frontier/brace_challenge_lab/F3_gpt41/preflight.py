"""Pre-flight checks for the GPT-4.1 green_profiles experiment. NO network: payloads are captured from the real harness
Runner with a recording dry-run transport. Exit 0 only if every check passes.

    python research_frontier/brace_challenge_lab/F3_gpt41/preflight.py [--full]
"""
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OV = HERE.parents[1] / "overnight"
ROOT = HERE.parents[2]
sys.path[:0] = [str(OV), str(ROOT / "src")]
import pandas as pd  # noqa: E402
from harness import cli  # noqa: E402
from harness.client import Client, DryRunTransport  # noqa: E402
from harness.runner import RateLimiter, RunConfig, Runner  # noqa: E402
from harness.tasks_green_profiles import F2, OPT, build  # noqa: E402

FULL = "--full" in sys.argv
checks = {}


def parse(i: str):
    """task id = fmt|cond|order|<cell, which itself contains ' | '>|fold|sN"""
    fmt, cond, order, rest = i.split("|", 3)
    cell, fold, s = rest.rsplit("|", 2)
    return fmt, cond, order, cell, fold, s


class Rec(DryRunTransport):
    def __init__(self):
        super().__init__()
        self.payloads = []

    def send(self, p):
        self.payloads.append(json.loads(json.dumps(p)))
        return super().send(p)


tasks = build(pilot=not FULL)
cfg = RunConfig(model="openai/gpt-4.1", price_in_per_m=2.0, price_out_per_m=8.0, budget_usd=1.0 if not FULL else 5.0,
                temperature=0.0, max_workers=1, out_dir=Path(tempfile.mkdtemp()))
rec = Rec()
no_wait = RateLimiter(10 ** 6, sleep=lambda s: None)          # offline capture only: no network, no throttling
Runner(cfg, Client(rec), no_wait).run(cli.unique(tasks, cfg))
P = rec.payloads
ids = [t.task_id for t in cli.unique(tasks, cfg)]
checks["n_payloads"] = (len(P) == len(ids) == (264 if not FULL else 1556), len(P))

# 1. model / sampling configuration
cfgs = {(p["model"], p["temperature"], p["max_tokens"], json.dumps(p["response_format"]), json.dumps(p.get("usage"))) for p in P}
checks["model_config"] = (cfgs == {("openai/gpt-4.1", 0.0, 40, '{"type": "json_object"}', '{"include": true}')}, sorted(cfgs))
checks["payload_keys"] = (all(set(p) == {"model", "messages", "temperature", "max_tokens", "response_format", "usage"} for p in P), None)

# 2. no identifiers, outcomes or individual records
from common import load_people  # noqa: E402
blob = json.dumps([p["messages"] for p in P]).lower()
banned = [w for w in ("pid", "twin", "chose", "y_human", "split", "train", "test") if w in blob]
checks["no_banned_words"] = (not banned, banned)
people = load_people(corrected=True)
prof = pd.read_csv(F2 / "profiles.csv")
allowed_nums = {f"{v:+.2f}" for c in ("green", "social_desirability", "spendthrift", "crt", "dictator_give", "neuroticism") for v in prof[c]}
bad_nums = set()
for p in P:
    u = p["messages"][1]["content"]
    for n in re.findall(r"[+-]\d+\.\d{2}", u):
        if n not in allowed_nums:
            bad_nums.add(n)
checks["only_aggregate_profile_numbers"] = (not bad_nums, sorted(bad_nums)[:5])
k = people.assign(edu3=people.education.astype(str).map(__import__("harness.tasks", fromlist=["EDU3"]).EDU3))
kc = k[["age_band", "sex", "income", "edu3"]].astype(str).agg(" | ".join, axis=1).value_counts()
cells_used = {parse(i)[3] for i in ids if parse(i)[3] != "ALL"}
checks["cells_k_anonymous_ge5"] = (all(kc.get(c, 0) >= 5 for c in cells_used), len(cells_used))

# 3. option-order mapping and matched information
ok_order, ok_match = True, True
by = {}
for i, p in zip(ids, P):
    fmt, cond, order, cell, fold, s = parse(i)
    u = p["messages"][1]["content"]
    green_A = f"A: {OPT['green']}" in u and f"B: {OPT['grey']}" in u
    green_B = f"A: {OPT['grey']}" in u and f"B: {OPT['green']}" in u
    ok_order &= (order == "AB" and green_A) or (order == "BA" and green_B)
    by[(fmt, cond, order, cell, fold, s)] = u
for (fmt, cond, order, cell, fold, s), u in by.items():
    if fmt == "profile" and s == "s0":
        n = by[("narrative", cond, order, cell, fold, s)]
        ok_match &= sorted(re.findall(r"[+-]\d\.\d\d", u)) == sorted(re.findall(r"[+-]\d\.\d\d", n))
checks["order_mapping"] = (ok_order, None)
checks["profile_narrative_same_numbers"] = (ok_match, None)

# 4. cross-fitting: profile used for fold f was fit without fold-f people (tamper test from F2)
import subprocess  # noqa: E402
r = subprocess.run([sys.executable, "-m", "pytest", "-q", str(F2 / "test_f2.py")], capture_output=True, text=True,
                   env={**__import__("os").environ, "PYTHONPATH": f"{ROOT / 'src'};{OV}"})
checks["cross_fitting_and_design_tests"] = (r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[-200:])

# 5. caps
checks["pilot_cap_enforced"] = (cli.main(["plan", "--experiment", "green_profiles", "--pilot", "--budget", "1.01"]) == 2, None)
checks["total_cap_enforced"] = (cli.main(["plan", "--experiment", "green_profiles", "--budget", "5.01"]) == 2, None)

for name, (ok, info) in checks.items():
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {'' if info is None else info}")
sys.exit(0 if all(ok for ok, _ in checks.values()) else 1)
