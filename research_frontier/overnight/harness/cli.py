"""Command line: check-key | plan | dry-run | live. Dry-run/plan are the defaults; nothing is ever sent unless `live`.

    python -m harness.cli check-key                                   # key present? .env ignored/untracked? (no network)
    python -m harness.cli plan    --model openai/gpt-4.1 --pilot      # exact call count + cost estimate
    python -m harness.cli dry-run --model openai/gpt-4.1 --pilot      # full pipeline offline
    python -m harness.cli live    --model openai/gpt-4.1 --pilot --budget 1 \
        --confirm "I have authorization to send k-anonymous demographic cells to OpenRouter"
Run from research_frontier/overnight/. Live mode requires ALL of: the `live` subcommand, the exact --confirm text, and a
key in OPEN_ROUTER_KEY (loaded from the repository .env only at this point) or OPENROUTER_API_KEY. With --pilot the
budget may not exceed $1. The presence of a key never triggers a live call.
"""
import argparse
import json
import sys
from pathlib import Path

from . import credentials
from .client import Client, DryRunTransport, HttpTransport
from .prompts import TEMPLATE_HASH, render
from .runner import RunConfig, Runner
from .tasks import build, build_pilot

HERE = Path(__file__).resolve().parents[1]
CONFIRM = "I have authorization to send k-anonymous demographic cells to OpenRouter"
PILOT_BUDGET_CAP = 1.0


def unique(tasks, cfg):
    seen, out = set(), []
    for t in tasks:
        k = t.key(cfg)
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["check-key", "plan", "dry-run", "live"])
    ap.add_argument("--model", default="openai/gpt-4.1")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--pilot", action="store_true", help="80-call feasibility batch (default_eric); budget capped at $1")
    ap.add_argument("--budget", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--rpm", type=int, default=60)
    ap.add_argument("--confirm", default="")
    a = ap.parse_args(argv)

    if a.mode == "check-key":
        credentials.load_env_file()
        safe = credentials.dotenv_is_safe()
        print(json.dumps({"key_detected": credentials.key_present(), **{f"dotenv_{k}": v for k, v in safe.items()}}))
        return 0 if credentials.key_present() and safe["ignored"] and not safe["tracked"] else 4

    if a.pilot and a.budget > PILOT_BUDGET_CAP:
        print(f"pilot budget may not exceed ${PILOT_BUDGET_CAP}", file=sys.stderr)
        return 2
    prices = json.loads((HERE / "pricing_snapshot.json").read_text())["models"]
    if a.model not in prices:
        print(f"model {a.model} not in pricing_snapshot.json; verify its price first", file=sys.stderr)
        return 2
    pr = prices[a.model]
    tag = ("pilot__" if a.pilot else "") + a.model.replace("/", "__")
    out = HERE / "runs" / ("live" if a.mode == "live" else "dry") / tag
    cfg = RunConfig(model=a.model, price_in_per_m=pr["in_per_m"], price_out_per_m=pr["out_per_m"], budget_usd=a.budget,
                    max_workers=a.workers, requests_per_minute=a.rpm, out_dir=out)
    tasks = build_pilot()[0] if a.pilot else build(samples=a.samples)[0]
    tasks = unique(tasks, cfg)
    est_in = sum(sum(len(m["content"]) for m in render(t.arm, t.profile, t.item)) / 3.5 for t in tasks)
    est = (est_in * pr["in_per_m"] + len(tasks) * cfg.max_tokens * pr["out_per_m"]) / 1e6
    print(f"template {TEMPLATE_HASH} | model {a.model} | unique calls {len(tasks)} | est. input tokens {est_in:,.0f} | "
          f"est. cost ${est:.4f} (upper bound: {cfg.max_tokens} output tokens/call) | budget ${a.budget}")
    if a.mode == "plan":
        return 0
    if a.mode == "live":
        if a.confirm != CONFIRM:                                   # authorization first, before touching any secret
            print("live mode refused: --confirm must equal the exact authorization text", file=sys.stderr)
            return 3
        credentials.load_env_file()
        if not credentials.key_present():
            print("live mode refused: no API key (OPEN_ROUTER_KEY / OPENROUTER_API_KEY)", file=sys.stderr)
            return 3
        transport = HttpTransport()
    else:
        transport = DryRunTransport()
    res = Runner(cfg, Client(transport)).run(tasks)
    print(json.dumps(json.loads((out / "summary.json").read_text()), indent=1),
          f"\nresults: {sum(r is not None for r in res)}/{len(res)} -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
