"""EXPLORATORY robustness #1: does the 'demographics add nothing' finding survive simpler / more regularised models?

Training split only. Same participants and the same 5 folds as the exploratory follow-ups:
  green      : default_eric hypothetical green choice (binary), folds from exploratory_values.folds
  redist_bin : 'government should help' (GOVT_RESPONSIBILITY points 1-2), folds from exploratory_redistribution.folds
Models (logistic; all preprocessing inside each fold):
  D0 population baseline (training-fold prevalence)
  D1 compact: age band + income + education, C = 1.0
  D2 full Tier A, C = 1.0                       (the model used in the follow-ups)
  D3 full Tier A, strongly regularised, C = 0.05 (fixed in advance)
  D4 full Tier A, C tuned by inner 5-fold CV on Brier inside each training fold
Verdict rule (fixed in advance): the negative finding is overturned only if some demographic model improves Brier
over D0 by >= 0.010 with a 95% participant-bootstrap CI excluding 0.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

sys.path.insert(0, str(Path(__file__).resolve().parent))
import exploratory_redistribution as er  # noqa: E402
import exploratory_values as ev  # noqa: E402
from common import ROOT, SEED, TIER_A  # noqa: E402

OUT = ROOT / "reports/robustness/demographic_complexity"
COMPACT = ["age_band", "income", "education"]
MEANINGFUL = 0.010
MODELS = {
    "D0": ("Population baseline", None),
    "D1": ("Compact: age + income + education (C=1)", lambda: _lr(COMPACT, LogisticRegression(C=1.0, max_iter=2000))),
    "D2": ("Full Tier A (C=1)", lambda: _lr(TIER_A, LogisticRegression(C=1.0, max_iter=2000))),
    "D3": ("Full Tier A, strong L2 (C=0.05)", lambda: _lr(TIER_A, LogisticRegression(C=0.05, max_iter=2000))),
    "D4": ("Full Tier A, C tuned by inner CV", lambda: _lr(TIER_A, LogisticRegressionCV(
        Cs=np.logspace(-3, 1, 15), cv=5, scoring="neg_brier_score", max_iter=2000))),
}


def _lr(cols, est):
    return make_pipeline(ColumnTransformer([("oh", OneHotEncoder(handle_unknown="ignore"), cols)]), est)


def datasets() -> dict:
    g = ev.load_train()
    r = er.load("govt_help")
    return {
        "green": (g, g.chose_green.to_numpy().astype(int), ev.folds(g.chose_green.to_numpy())),
        "redist_bin": (r, (r.y >= 4).astype(int).to_numpy(), er.folds(r.y.to_numpy())),
    }


def oof(df: pd.DataFrame, y: np.ndarray, fold: np.ndarray) -> pd.DataFrame:
    X = df[TIER_A].astype(str)
    out = pd.DataFrame({"pid": df.pid.to_numpy(), "y": y, "fold": fold})
    for name, (_, make) in MODELS.items():
        p = np.empty(len(y))
        for k in range(5):
            trn, tst = fold != k, fold == k
            p[tst] = y[trn].mean() if make is None else make().fit(X[trn], y[trn]).predict_proba(X[tst])[:, 1]
        out[name] = p
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    perf_rows, comp_rows = [], []
    for name, (df, y, fold) in datasets().items():
        o = oof(df, y, fold)
        o.to_csv(OUT / f"oof_{name}.csv", index=False)
        for m in MODELS:
            met = ev.metrics(o.y.to_numpy(), o[m].to_numpy())
            cal = ev.calibration(o.y.to_numpy(), o[m].to_numpy())
            perf_rows.append(dict(outcome=name, n=len(o), model=m, label=MODELS[m][0], brier=met["brier"],
                                  logloss=met["logloss"], auc=np.nan if m == "D0" else met["auc"],
                                  calib_in_large=cal["calib_in_large"],
                                  calib_slope=np.nan if m == "D0" else cal["calib_slope"], ece_5bin=cal["ece_5bin"]))
        for m in ["D1", "D2", "D3", "D4"]:
            r = ev.paired_bootstrap(o, m, "D0", rng)
            r["verdict"] = r["verdict"].replace("improvement", "improvement over baseline")
            comp_rows.append(dict(outcome=name, **r))
    perf, comp = pd.DataFrame(perf_rows), pd.DataFrame(comp_rows)
    perf.round(4).to_csv(OUT / "performance.csv", index=False)
    comp.round(5).to_csv(OUT / "paired_vs_baseline.csv", index=False)
    overturned = bool(((comp.brier_hi < 0) & (-comp.brier_diff >= MEANINGFUL)).any())
    json.dump({"negative_finding_overturned": overturned, "rule": "any model: dBrier <= -0.010 and CI excludes 0"},
              open(OUT / "verdict.json", "w"), indent=1)

    L = ["# EXPLORATORY robustness: demographic model complexity", "",
         "> Exploratory, training split only. Same participants and folds as the follow-ups; all preprocessing "
         "fitted inside each fold. The verdict rule was fixed in advance: the negative finding is overturned only "
         "if a demographic model improves Brier over the baseline by at least 0.010 with a CI excluding 0.", ""]
    for name, title in [("green", "Green energy: hypothetical $39 renewable choice (n = 428)"),
                        ("redist_bin", "Redistribution attitude, binary (n = 833)")]:
        L += [f"## {title}", "", "| Model | Brier | Log loss | AUC | Calibration-in-the-large | Calibration slope | ECE |",
              "|---|---|---|---|---|---|---|"]
        for _, r in perf[perf.outcome == name].iterrows():
            L.append(f"| {r.model}: {r.label} | {r.brier:.4f} | {r.logloss:.4f} | "
                     f"{'–' if np.isnan(r.auc) else f'{r.auc:.3f}'} | {r.calib_in_large:+.3f} | "
                     f"{'–' if np.isnan(r.calib_slope) else f'{r.calib_slope:.2f}'} | {r.ece_5bin:.3f} |")
        L += ["", "| Contrast | ΔBrier vs baseline (95% CI) | Verdict |", "|---|---|---|"]
        for _, c in comp[comp.outcome == name].iterrows():
            L.append(f"| {c.contrast} | {c.brier_diff:+.4f} ({c.brier_lo:+.4f}, {c.brier_hi:+.4f}) | {c.verdict} |")
        L.append("")
    L += [f"**Negative demographic finding overturned by any variant: {'YES' if overturned else 'NO'}.**", ""]
    (OUT / "demographic_complexity.md").write_text("\n".join(L), encoding="utf-8")
    print(perf.round(4).to_string(index=False))
    print(comp[["outcome", "contrast", "brier_diff", "brier_lo", "brier_hi", "auc_diff", "verdict"]].round(4).to_string(index=False))
    print("overturned:", overturned)


if __name__ == "__main__":
    main()
