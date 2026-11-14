"""EXPLORATORY research-frontier experiments (pre-specified in research_frontier/04_experiment_designs.md).

TRAINING PARTICIPANTS ONLY. No held-out participant is read for modelling (asserted below). Nothing in results/,
reports/ or figures/ is modified. Outputs: research_frontier/experiments/results/.

X1  Green-choice decomposition: prevalence vs default-only vs GREEN-only vs GREEN+default (no demographics),
    compared on the SAME participants and folds as the existing exploratory models (M1..M3).
X2  Construct-overlap check: do attitude-only GREEN items (concern/identity) predict the hypothetical choice, or only
    the items that already describe purchasing/cost-willingness?
X3  Persona composition adjustment: do persona differences survive adjusting for the other census variables?

    python research_frontier/experiments/run_experiments.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import exploratory_values as ev  # noqa: E402
from common import RAW_TWIN, SEED, TIER_A, load_people  # noqa: E402
from personas import load_config, mask, parse_criteria  # noqa: E402

OUT = Path(__file__).resolve().parent / "results"
NB = 2000
MEANINGFUL = 0.010  # same pre-set Brier threshold as the earlier exploratory work

GREEN_ITEMS = {  # QID235 rows, verified against question_catalog.json in verify_items()
    1: "products I use do not harm the environment", 2: "consider environmental impact of my actions",
    3: "purchase habits are affected by concern", 4: "concerned about wasting resources",
    5: "describe myself as environmentally responsible", 6: "willing to be inconvenienced",
}
ATTITUDE_ONLY = [2, 4, 5]      # concern / identity, no purchasing or cost content
BEHAVIOUR_COST = [1, 3, 6]     # product choice, purchase habits, willingness to bear a cost


def verify_items() -> None:
    cat = json.load(open(RAW_TWIN / "question_catalog_and_human_response_csv/question_catalog.json", encoding="utf-8"))
    cat = {q["QuestionID"]: q for q in (cat if isinstance(cat, list) else cat.values())}
    rows = dict(zip(cat["QID235"]["csv_columns"], cat["QID235"]["Rows"]))
    keys = {1: "do not harm", 2: "potential environmental impact", 3: "purchase habits", 4: "wasting the resources",
            5: "environmentally responsible", 6: "inconvenienced"}
    for i, k in keys.items():
        assert k in rows[f"QID235_{i}"], (i, rows[f"QID235_{i}"])


def train_green() -> pd.DataFrame:
    df = ev.load_train()
    assert (df.split == "train").all()
    items = pd.read_csv(RAW_TWIN / "question_catalog_and_human_response_csv/wave1_3_response.csv",
                        usecols=["pid", *[f"QID235_{i}" for i in range(1, 7)]])
    df = df.merge(items, on="pid", how="left")
    df["green_att"] = df[[f"QID235_{i}" for i in ATTITUDE_ONLY]].mean(axis=1)
    df["green_beh"] = df[[f"QID235_{i}" for i in BEHAVIOUR_COST]].mean(axis=1)
    assert np.allclose(df[[f"QID235_{i}" for i in range(1, 7)]].mean(axis=1), df.green)
    return df


def lr(num):
    return make_pipeline(ColumnTransformer([("sc", StandardScaler(), num)]), LogisticRegression(C=1.0, max_iter=2000))


def oof(df, fold, num) -> np.ndarray:
    y, X, p = df.chose_green.to_numpy(), df[num].astype(float), np.empty(len(df))
    for k in range(5):
        trn, tst = fold != k, fold == k
        p[tst] = lr(num).fit(X[trn], y[trn]).predict_proba(X[tst])[:, 1] if num else y[trn].mean()
    return p


def paired(y, a, b, rng) -> dict:
    br = lambda p, i: np.mean((y[i] - p[i]) ** 2)
    d0 = br(a, slice(None)) - br(b, slice(None))
    ds = []
    for _ in range(NB):
        i = rng.integers(0, len(y), len(y))
        ds.append(br(a, i) - br(b, i))
    lo, hi = np.quantile(ds, [.025, .975])
    return dict(d_brier=d0, lo=lo, hi=hi,
                verdict=("meaningful improvement" if hi < 0 and -d0 >= MEANINGFUL else "detectable but small" if hi < 0
                         else "worse" if lo > 0 else "no detectable difference"))


def x1_x2() -> dict:
    verify_items()
    df = train_green()
    fold = ev.folds(df.chose_green.to_numpy())
    prior = pd.read_csv(ROOT / "reports/exploratory/oof_predictions.csv")
    assert (prior.pid.to_numpy() == df.pid.to_numpy()).all() and (prior.fold.to_numpy() == fold).all()
    y = df.chose_green.to_numpy()
    preds = {
        "prevalence": oof(df, fold, []),
        "default only": oof(df, fold, ["green_default"]),
        "GREEN only": oof(df, fold, ["green"]),
        "GREEN + default": oof(df, fold, ["green", "green_default"]),
        "attitude items (2,4,5) + default": oof(df, fold, ["green_att", "green_default"]),
        "behaviour/cost items (1,3,6) + default": oof(df, fold, ["green_beh", "green_default"]),
        "M1D demographics + default (existing)": prior.M1D.to_numpy(),
        "M3 demographics + GREEN + default (existing)": prior.M3.to_numpy(),
    }
    assert np.allclose(preds["prevalence"], prior.M0)
    rng = np.random.default_rng(SEED)
    rows = []
    for name, p in preds.items():
        m, c = ev.metrics(y, p), ev.calibration(y, p)
        rows.append(dict(model=name, brier=m["brier"], logloss=m["logloss"], auc=m["auc"] if name != "prevalence" else np.nan,
                         calib_slope=c["calib_slope"] if name != "prevalence" else np.nan, ece=c["ece_5bin"]))
    perf = pd.DataFrame(rows)
    contrasts = [("default only", "prevalence"), ("GREEN only", "prevalence"), ("GREEN + default", "default only"),
                 ("GREEN + default", "M3 demographics + GREEN + default (existing)"),
                 ("default only", "M1D demographics + default (existing)"),
                 ("attitude items (2,4,5) + default", "default only"),
                 ("behaviour/cost items (1,3,6) + default", "default only"),
                 ("attitude items (2,4,5) + default", "behaviour/cost items (1,3,6) + default")]
    comp = pd.DataFrame([dict(contrast=f"{a} vs {b}", **paired(y, preds[a], preds[b], rng)) for a, b in contrasts])
    # descriptive: standardized logit slopes (full-sample, train) for the item subsets
    z = lambda s: (s - s.mean()) / s.std()
    slopes = {}
    for col in ["green", "green_att", "green_beh"]:
        f = smf.logit(f"chose_green ~ zz + green_default", df.assign(zz=z(df[col]))).fit(disp=0)
        ci = f.conf_int().loc["zz"]
        slopes[col] = dict(OR_per_SD=float(np.exp(f.params.zz)), lo=float(np.exp(ci[0])), hi=float(np.exp(ci[1])))
    alpha = lambda cols: float(len(cols) / (len(cols) - 1) * (1 - df[cols].var(ddof=1).sum() / df[cols].sum(axis=1).var(ddof=1)))
    rel = {"attitude_items_alpha": alpha([f"QID235_{i}" for i in ATTITUDE_ONLY]),
           "behaviour_items_alpha": alpha([f"QID235_{i}" for i in BEHAVIOUR_COST]),
           "corr_att_beh": float(df.green_att.corr(df.green_beh))}
    return dict(n=len(df), perf=perf, comp=comp, slopes=slopes, reliability=rel)


def x3() -> pd.DataFrame:
    p = load_people(corrected=True)
    tr = p[p.split == "train"].copy()
    assert (tr.split == "train").all()
    targets = {"P1": ["neuroticism", "social_desirability"], "P2": ["neuroticism", "social_desirability"],
               "P3": ["neuroticism", "green"]}
    rows = []
    for key, cfg in load_config().items():
        crit = parse_criteria(cfg["criteria"], p)
        tr["member"] = mask(tr, crit).astype(int)
        others = [v for v in TIER_A if v not in crit]
        for c in targets[key]:
            tr["yz"] = (tr[c] - tr[c].mean()) / tr[c].std(ddof=1)
            raw = smf.ols("yz ~ member", tr).fit(cov_type="HC3")
            adj = smf.ols("yz ~ member + " + " + ".join(f"C({v})" for v in others), tr).fit(cov_type="HC3")
            rows.append(dict(persona=key, construct=c, n_members=int(tr.member.sum()), adjusted_for=", ".join(others),
                             raw_diff=raw.params.member, raw_lo=raw.conf_int().loc["member", 0], raw_hi=raw.conf_int().loc["member", 1],
                             adj_diff=adj.params.member, adj_lo=adj.conf_int().loc["member", 0], adj_hi=adj.conf_int().loc["member", 1],
                             retained_share=adj.params.member / raw.params.member))
    d = pd.DataFrame(rows)
    d["verdict"] = np.where((d.adj_lo > 0) | (d.adj_hi < 0),
                            np.where(d.retained_share >= 0.5, "survives adjustment (>=50% retained, CI excl. 0)",
                                     "attenuated but CI excludes 0"), "not distinguishable after adjustment")
    return d


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    r = x1_x2()
    r["perf"].round(4).to_csv(OUT / "x1_x2_performance.csv", index=False)
    r["comp"].round(5).to_csv(OUT / "x1_x2_paired_contrasts.csv", index=False)
    json.dump({"n_train": r["n"], "slopes": r["slopes"], "reliability": r["reliability"]},
              open(OUT / "x2_slopes_reliability.json", "w"), indent=1)
    d3 = x3()
    d3.round(4).to_csv(OUT / "x3_composition_adjustment.csv", index=False)
    pd.set_option("display.width", 250)
    print(r["perf"].round(4).to_string(index=False)); print(r["comp"].round(4).to_string(index=False))
    print(json.dumps({"slopes": r["slopes"], "reliability": r["reliability"]}, indent=1))
    print(d3.drop(columns="adjusted_for").round(3).to_string(index=False))


if __name__ == "__main__":
    main()
