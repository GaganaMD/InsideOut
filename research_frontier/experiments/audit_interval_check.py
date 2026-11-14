"""Audit check for Figure 1 intervals (TRAINING PARTICIPANTS ONLY; no held-out data are read).

Figure 1's 95% intervals resample held-out participants with the fitted model FIXED, so they describe uncertainty about
THIS frozen model's performance in this population, not the method's performance across re-fits. Here we size the
missing component on training data only: bootstrap the training sample, refit the same ridge pipeline, and score it on
the out-of-bag training participants (".632-style" OOB R2). The spread of OOB R2 includes refit variability.

    python research_frontier/experiments/audit_interval_check.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from common import SEED, TIER_A, load_people  # noqa: E402
from predictability import model  # noqa: E402

OUT = Path(__file__).resolve().parent / "results"
B = 200


def main() -> None:
    p = load_people(corrected=True)
    tr = p[p.split == "train"].reset_index(drop=True)
    assert (tr.split == "train").all()
    X = tr[TIER_A].astype(str)
    rng = np.random.default_rng(SEED)
    fig1 = pd.read_csv(ROOT / "figures/data/fig1_heldout_r2.csv").set_index("construct")
    rows = []
    for c in ["neuroticism", "social_desirability", "green", "crt"]:
        y = tr[c].to_numpy()
        r2s = []
        for _ in range(B):
            idx = rng.integers(0, len(y), len(y))
            oob = np.setdiff1d(np.arange(len(y)), idx)
            m = model(TIER_A).fit(X.iloc[idx], y[idx])
            pred, base = m.predict(X.iloc[oob]), y[idx].mean()
            r2s.append(1 - ((y[oob] - pred) ** 2).sum() / ((y[oob] - base) ** 2).sum())
        r2s = np.array(r2s)
        rows.append(dict(construct=c, oob_r2_mean=r2s.mean(), oob_lo=np.quantile(r2s, .025), oob_hi=np.quantile(r2s, .975),
                         oob_width=np.quantile(r2s, .975) - np.quantile(r2s, .025),
                         fig1_fixed_model_width=fig1.loc[c, "hi"] - fig1.loc[c, "lo"],
                         note="OOB refit interval (train only) vs Figure 1 fixed-model held-out interval"))
    d = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    d.round(4).to_csv(OUT / "audit_interval_widths.csv", index=False)
    print(d.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
