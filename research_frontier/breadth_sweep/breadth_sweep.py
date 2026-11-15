"""EXPLORATORY breadth sweep. NOT part of the submission pipeline (run_all.py does not call this).

Added after the holdout was inspected. TRAIN split only. Reads nothing frozen for writing and changes no submitted file.
Run from the repository root:  python research_frontier/breadth_sweep/breadth_sweep.py

1. Tier A predictability of EVERY usable shipped score, with the same model as src/predictability.py (ridge on one-hot
   Tier A, 5x5 repeated CV, seed 20261114). Question: are the six pre-registered constructs typical of the dataset?
   Caveat: only the six pre-registered scores were re-derived from items, and three of those six were mis-scored as
   shipped. Every other row is an UNAUDITED shipped score and is indicative only.
2. The organ-donation choice in default_eric (the same participants' second hypothetical choice, not used in the
   submission): does Tier A add to the randomised default condition? Out-of-fold Brier, paired participant bootstrap.

Outputs (this folder): all_scores_r2.csv, organ_choice.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import RepeatedKFold, RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from common import PROC, SEED, TIER_A, load_people  # noqa: E402
from predictability import model  # noqa: E402

AUDITED = {"w1_score_GREEN", "w1_score_neuroticism", "w3_score_dictator_sender"}   # shipped score verified exact
REPLACED = {"w3_score_ST-TW": "spendthrift", "w2_score_socialdesirability": "social_desirability",
            "w1_crt2_score": "crt"}                                                # shipped score known defective


def cv_r2(X: pd.DataFrame, y: np.ndarray) -> tuple[float, float]:
    r2 = []
    for tr, te in RepeatedKFold(n_splits=5, n_repeats=5, random_state=SEED).split(X):
        pred = model(TIER_A).fit(X.iloc[tr], y[tr]).predict(X.iloc[te])
        r2.append(1 - ((y[te] - pred) ** 2).sum() / ((y[te] - y[tr].mean()) ** 2).sum())
    return float(np.mean(r2)), float(1.96 * np.std(r2, ddof=1) / np.sqrt(5))   # same heuristic CI as the frozen map


def all_scores(train: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in [c for c in pd.read_parquet(PROC / "scores.parquet").columns if c != "pid"]:
        if col in REPLACED:                      # use the corrected item-level score under its construct name
            y, status = train[REPLACED[col]], "re-scored from items (shipped score defective)"
        else:
            y = pd.to_numeric(train[col], errors="coerce")
            status = "verified against items" if col in AUDITED else "UNAUDITED shipped score"
        ok = y.notna() & np.isfinite(y)
        if ok.mean() < 0.95 or y[ok].abs().max() > 1e6:
            rows.append(dict(score=col, n=int(ok.sum()), cv_r2=np.nan, ci_half=np.nan, status="excluded: non-numeric codes"))
            continue
        r2, half = cv_r2(train.loc[ok, TIER_A].astype(str).reset_index(drop=True), y[ok].to_numpy(float))
        rows.append(dict(score=col, n=int(ok.sum()), cv_r2=r2, ci_half=half, status=status))
    return pd.DataFrame(rows).sort_values("cv_r2", ascending=False, na_position="last")


def organ(train: pd.DataFrame) -> dict:
    m = pd.read_parquet(PROC / "mega_default_eric.parquet")[["pid", "organ_condition", "organ_donor"]]
    m["pid"] = m.pid.astype(int)
    d = m.merge(train, on="pid").dropna(subset=["organ_donor"]).reset_index(drop=True)
    y = d.organ_donor.astype(float).astype(int).to_numpy()
    d["cond"] = d.organ_condition.astype(str)
    oof = {}
    for name, feats in (("condition_only", ["cond"]), ("condition_plus_tierA", ["cond", *TIER_A])):
        X, p = d[feats].astype(str), np.zeros(len(d))
        for tr, te in RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED).split(X, y):
            mm = make_pipeline(OneHotEncoder(handle_unknown="ignore"), LogisticRegressionCV(Cs=10, max_iter=5000))
            p[te] += mm.fit(X.iloc[tr], y[tr]).predict_proba(X.iloc[te])[:, 1] / 5
        oof[name] = p
    diff = (oof["condition_plus_tierA"] - y) ** 2 - (oof["condition_only"] - y) ** 2   # negative = Tier A helps
    b = np.random.default_rng(SEED).choice(diff, size=(2000, len(diff)), replace=True).mean(axis=1)
    rate = d.groupby("cond").organ_donor.agg(["mean", "size"])
    return dict(n=len(d), donor_rate_by_default={k: dict(rate=float(v["mean"]), n=int(v["size"])) for k, v in rate.iterrows()},
                brier={k: float(((v - y) ** 2).mean()) for k, v in oof.items()},
                brier_diff_tierA_minus_condition=dict(est=float(diff.mean()), lo=float(np.quantile(b, .025)),
                                                      hi=float(np.quantile(b, .975))),
                coding="organ_donor = 1 if the participant ends as a potential donor (OPTOUT_Organ == 1 or OPTIN_Organ == 2)")


def main() -> None:
    people = load_people(corrected=True)
    extra = pd.read_parquet(PROC / "scores.parquet")
    train = people[people.split == "train"].merge(extra, on="pid").reset_index(drop=True)
    t = all_scores(train)
    t.round(4).to_csv(HERE / "all_scores_r2.csv", index=False, lineterminator="\n")
    with open(HERE / "organ_choice.json", "w", newline="\n") as f:
        json.dump(organ(train), f, indent=1)
    u = t.dropna(subset=["cv_r2"])
    print(t.round(3).to_string(index=False))
    print(f"usable {len(u)}; R2>=0.10: {(u.cv_r2 >= .10).sum()}; median {u.cv_r2.median():.3f}; max {u.cv_r2.max():.3f}")


if __name__ == "__main__":
    main()
