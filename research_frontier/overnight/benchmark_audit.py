"""Audit of the published GPT-4.1 default_eric comparison (research_frontier/09). TRAINING PARTICIPANTS ONLY.

Adds what 09 lacked: paired CIs for every headline contrast, and recovery of the RANDOMISED default effect
(green-default rate minus grey-default rate) by each LLM specification vs humans.

    python research_frontier/overnight/benchmark_audit.py   (requires research_frontier/experiments/llm_benchmark.py fetch)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "research_frontier/experiments"))
import exploratory_values as ev  # noqa: E402
import llm_benchmark as lb  # noqa: E402
import run_experiments as rx  # noqa: E402
from common import SEED  # noqa: E402

NB = 4000


def load():
    lb.fetch()
    train = ev.load_train()
    assert (train.split == "train").all()
    pids, y = train.pid.to_numpy(), train.chose_green.to_numpy()
    cond = (train.green_condition == "green_default").to_numpy().astype(int)
    preds = {}
    for name, spec in lb.SPECS.items():
        llm = lb.chose_green(pd.read_csv(lb.EXT / f"{spec}__{lb.FILES[0]}", low_memory=False)).set_index("pid")
        preds[name] = llm.loc[pids, "y"].to_numpy(float)
    df = rx.train_green()
    fold = ev.folds(df.chose_green.to_numpy())
    preds["Green values + default (stat, OOF)"] = (rx.oof(df, fold, ["green", "green_default"]) >= .5).astype(float)
    preds["Default only (stat, OOF)"] = (rx.oof(df, fold, ["green_default"]) >= .5).astype(float)
    return y, cond, preds


def main() -> None:
    y, cond, P = load()
    rng = np.random.default_rng(SEED)
    idx = [rng.integers(0, len(y), len(y)) for _ in range(NB)]
    acc = lambda p, i: np.mean(p[i] == y[i])
    pairs = [("LLM demographics-only (T=0)", "LLM empty persona (T=0.7)"),
             ("LLM demographics-only (T=0.7)", "LLM empty persona (T=0.7)"),
             ("LLM demographics-only (T=0)", "Default only (stat, OOF)"),
             ("LLM full persona (no reasoning)", "Green values + default (stat, OOF)"),
             ("LLM full persona (no reasoning)", "LLM demographics-only (T=0)")]
    rows = []
    for a, b in pairs:
        d = [acc(P[a], i) - acc(P[b], i) for i in idx]
        rows.append(dict(contrast=f"{a} minus {b}", acc_diff=acc(P[a], slice(None)) - acc(P[b], slice(None)),
                         lo=np.quantile(d, .025), hi=np.quantile(d, .975)))
    acc_tab = pd.DataFrame(rows)

    # randomised default effect: P(green | green default) - P(green | grey default)
    ate = lambda v, i: v[i][cond[i] == 1].mean() - v[i][cond[i] == 0].mean()
    rows = []
    for name, v in {"Humans": y.astype(float), **P}.items():
        d = [ate(v, i) for i in idx]
        gap = [ate(v, i) - ate(y.astype(float), i) for i in idx]
        rows.append(dict(source=name, ate=ate(v, slice(None)), lo=np.quantile(d, .025), hi=np.quantile(d, .975),
                         minus_human=ate(v, slice(None)) - ate(y.astype(float), slice(None)),
                         diff_lo=np.quantile(gap, .025), diff_hi=np.quantile(gap, .975)))
    ate_tab = pd.DataFrame(rows)
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    acc_tab.round(4).to_csv(out / "benchmark_audit_accuracy_contrasts.csv", index=False)
    ate_tab.round(4).to_csv(out / "benchmark_audit_default_effect.csv", index=False)
    pd.set_option("display.width", 220)
    print(acc_tab.round(3).to_string(index=False)); print(ate_tab.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
