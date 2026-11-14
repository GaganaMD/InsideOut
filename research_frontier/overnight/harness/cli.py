"""Command line: plan (cost estimate) | dry-run (no network) | live (paid; triple opt-in).

    python -m harness.cli plan    --model openai/gpt-4.1-mini --samples 5
    python -m harness.cli dry-run --model openai/gpt-4.1-mini --samples 2
    python -m harness.cli live    --model openai/gpt-4.1-mini --samples 5 --budget 5 \
        --confirm "I have authorization to send k-anonymous demographic cells to OpenRouter"
Run from research_frontier/overnight/. Live mode also requires OPENROUTER_API_KEY in the environment.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from .client import Client, DryRunTransport, HttpTransport
from .prompts import TEMPLATE_HASH, render
from .runner import RunConfig, Runner
from .tasks import build

HERE = Path(__file__).resolve().parents[1]
CONFIRM = "I have authorization to send k-anonymous demographic cells to OpenRouter"


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
    ap.add_argument("mode", choices=["plan", "dry-run", "live"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--budget", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--rpm", type=int, default=60)
    ap.add_argument("--confirm", default="")
    a = ap.parse_args(argv)
    prices = json.loads((HERE / "pricing_snapshot.json").read_text())["models"]
    if a.model not in prices:
        print(f"model {a.model} not in pricing_snapshot.json; verify its price first", file=sys.stderr)
        return 2
    pr = prices[a.model]
    out = HERE / "runs" / ("live" if a.mode == "live" else "dry") / a.model.replace("/", "__")
    cfg = RunConfig(model=a.model, price_in_per_m=pr["in_per_m"], price_out_per_m=pr["out_per_m"], budget_usd=a.budget,
                    max_workers=a.workers, requests_per_minute=a.rpm, out_dir=out)
    tasks, _, _ = build(samples=a.samples)
    tasks = unique(tasks, cfg)
    est_in = sum(sum(len(m["content"]) for m in render(t.arm, t.profile, t.item)) / 3.5 for t in tasks)
    est = (est_in * pr["in_per_m"] + len(tasks) * cfg.max_tokens * pr["out_per_m"]) / 1e6
    print(f"template {TEMPLATE_HASH} | unique calls {len(tasks)} | est. tokens in {est_in:,.0f} | est. cost ${est:.4f} "
          f"(upper bound: {cfg.max_tokens} output tokens/call) | budget ${a.budget}")
    if a.mode == "plan":
        return 0
    if a.mode == "live":
        if a.confirm != CONFIRM or not os.environ.get("OPENROUTER_API_KEY"):
            print("live mode refused: requires --confirm with the exact authorization text and OPENROUTER_API_KEY",
                  file=sys.stderr)
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
