"""A. Outer-layer predictability map (H1). Train split only.

For each construct: ridge on one-hot Tier A vs the population-mean baseline, 5-fold x 5-repeat outer CV with
inner CV for alpha. Reports CV R^2 (out-of-fold, relative to the training-fold mean), MAE for model and baseline,
fold-SE intervals, and a Tier A + party sensitivity row. Also writes age-band means (H1 directional checks).
"""
import json

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

from common import CONSTRUCTS, RESULTS, SEED, TIER_A, TIER_B, load_people

ALPHAS = np.logspace(-2, 3, 30)


def model(features):
    pre = ColumnTransformer([("oh", OneHotEncoder(handle_unknown="ignore"), features)])
    # Inner alpha selection by efficient leave-one-out (GCV) within each outer training fold.
    # Deviation from hypotheses.md (inner 5-fold): 5-fold inner CV made the drop-one analysis take >10 min.
    return make_pipeline(pre, RidgeCV(alphas=ALPHAS))


def cv_eval(df: pd.DataFrame, y: str, features: list[str]) -> dict:
    X = df[features].astype(str)
    yv = df[y].to_numpy()
    rows = []
    for k, (tr, te) in enumerate(RepeatedKFold(n_splits=5, n_repeats=5, random_state=SEED).split(X)):
        m = model(features).fit(X.iloc[tr], yv[tr])
        pred = m.predict(X.iloc[te])
        base = np.full(len(te), yv[tr].mean())
        sse, sst = ((yv[te] - pred) ** 2).sum(), ((yv[te] - base) ** 2).sum()
        rows.append(dict(r2=1 - sse / sst, mae=np.abs(yv[te] - pred).mean(),
                         mae_base=np.abs(yv[te] - base).mean(), alpha=m[-1].alpha_))
    f = pd.DataFrame(rows)
    se = lambda s: 1.96 * s.std(ddof=1) / np.sqrt(5)  # SE using effective n of one 5-fold pass (conservative-ish)
    gain = f.mae_base - f.mae
    return dict(n=len(df), cv_r2=f.r2.mean(), cv_r2_lo=f.r2.mean() - se(f.r2), cv_r2_hi=f.r2.mean() + se(f.r2),
                mae_model=f.mae.mean(), mae_baseline=f.mae_base.mean(),
                mae_gain_pct=100 * gain.mean() / f.mae_base.mean(),
                mae_gain_lo=gain.mean() - se(gain), mae_gain_hi=gain.mean() + se(gain),
                median_alpha=f.alpha.median())


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    df = load_people()
    tr = df[df.split == "train"].reset_index(drop=True)
    out = []
    for name in CONSTRUCTS:
        for label, feats in [("TierA", TIER_A), ("TierA+party", TIER_A + TIER_B)]:
            r = cv_eval(tr, name, feats)
            r.update(construct=name, features=label)
            out.append(r)
    res = pd.DataFrame(out)
    res["improves"] = (res.cv_r2_lo > 0) & (res.mae_gain_lo > 0)
    cols = ["construct", "features", "n", "cv_r2", "cv_r2_lo", "cv_r2_hi", "mae_model", "mae_baseline",
            "mae_gain_pct", "mae_gain_lo", "mae_gain_hi", "improves", "median_alpha"]
    res[cols].round(4).to_csv(RESULTS / "predictability_map.csv", index=False)

    # Which Tier A variables carry the signal: drop-one-variable loss in CV R^2 (TierA model)
    imp = []
    for name in CONSTRUCTS:
        full = res[(res.construct == name) & (res.features == "TierA")].cv_r2.item()
        for v in TIER_A:
            r = cv_eval(tr, name, [f for f in TIER_A if f != v])
            imp.append(dict(construct=name, dropped=v, r2_loss=full - r["cv_r2"]))
    pd.DataFrame(imp).round(4).to_csv(RESULTS / "predictability_dropone.csv", index=False)

    # H1 directional: age-band means with 95% CI (train)
    ag = []
    for name in CONSTRUCTS:
        for band, g in tr.groupby("age_band", observed=True):
            m, s, n = g[name].mean(), g[name].std(ddof=1), len(g)
            ag.append(dict(construct=name, age_band=band, n=n, mean=m, lo=m - 1.96 * s / np.sqrt(n),
                           hi=m + 1.96 * s / np.sqrt(n)))
    pd.DataFrame(ag).round(3).to_csv(RESULTS / "age_band_means.csv", index=False)
    print(res[cols].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
