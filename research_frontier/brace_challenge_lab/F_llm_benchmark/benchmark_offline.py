"""OFFLINE LLM-persona benchmark (Workstream F). NO API CALLS. TRAINING PARTICIPANTS ONLY.

Compares, on the same participants and outcomes:
  A0 population average, A1 condition-only, B* census-demographic statistical models (repeated CV within training),
  published GPT-4.1 digital twins from Peng et al. (arXiv:2509.19088; Apache-2.0): demographics_only (~C),
  full_persona (~E), empty_persona (reference), raw hard answers and a labelled CV recalibration of them.
Inputs: the pseudonymous training-only bundles built and verified by research_frontier/overnight/offline/prepare_bundle.py
(targeting_fairness treatment coded from `Segment`). Published treatment-effect CIs are reused from
research_frontier/overnight/results/modal_full-20261114 and point estimates are asserted to match.

    PYTHONUTF8=1 python research_frontier/brace_challenge_lab/F_llm_benchmark/benchmark_offline.py
Writes MODEL_COMPARISON.csv and results/*.json next to this file.
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BUNDLE = ROOT / "research_frontier/overnight/offline/bundle"
MODAL = ROOT / "research_frontier/overnight/results/modal_full-20261114/results"
SEED = 20261114
import os
REPEATS, NB = int(os.environ.get("F_REPEATS", 20)), int(os.environ.get("F_NB", 2000))
TIER_A = ["region", "sex", "age_band", "education", "race", "citizen", "marital", "income", "hh_size", "employment"]
EDU3 = {"Less than high school": "no college", "High school graduate": "no college",
        "Some college, no degree": "no college", "Associate's degree": "no college",
        "College graduate/some postgrad": "college", "Postgraduate": "college"}
CELL4 = ["age_band", "sex", "income", "edu3"]
STUDIES = {"default_eric": "binary", "targeting_fairness": "rating"}
LLM = {"C_t0": "demographics_t0", "C_t07": "demographics_t07", "E": "full_persona_t07", "empty": "empty_t07"}
MIN_CELL, SMALL_LO, SMALL_HI = 8, 10, 40


# ----------------------------------------------------------------------------- statistical models (OOF)
def _pipe(cat, kind, tuned):
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LogisticRegression, LogisticRegressionCV, Ridge, RidgeCV
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    tr = [("num", StandardScaler(), ["treat"]), ("cat", OneHotEncoder(handle_unknown="ignore"), cat)]
    if kind == "binary":
        est = LogisticRegressionCV(Cs=np.logspace(-3, 1, 9), cv=5, scoring="neg_brier_score", max_iter=3000) if tuned \
            else LogisticRegression(C=1.0, max_iter=3000)
    else:
        est = RidgeCV(alphas=np.logspace(-1, 3.5, 12)) if tuned else Ridge(alpha=1.0)
    return make_pipeline(ColumnTransformer(tr), est)


def _recal(x_tr, y_tr, x_te, kind):
    """Map a published hard LLM answer to a calibrated prediction using training-fold humans only (labelled hybrid)."""
    if kind == "binary":
        # P(y=1 | LLM answer) with a +1/+2 (Laplace) prior per answer level
        out = np.empty(len(x_te))
        for v in (0.0, 1.0):
            m = x_tr == v
            out[x_te == v] = (y_tr[m].sum() + 1) / (m.sum() + 2)
        return out
    b = np.polyfit(x_tr, y_tr, 1)
    return np.polyval(b, x_te)


def oof_predictions(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    from sklearn.model_selection import StratifiedKFold
    y, t = df.y_human.to_numpy(float), df.treat.to_numpy()
    strat = df.treat.astype(str) + "_" + (y if kind == "binary" else (y >= np.median(y))).astype(int).astype(str)
    names = ["A0", "A1", "B10_fixed", "B10_tuned", "B4_tuned"] + [f"{k}_recal" for k in LLM]
    acc = {m: np.zeros((REPEATS, len(df))) for m in names}
    for r in range(REPEATS):
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED + r).split(df, strat):
            acc["A0"][r, te] = y[tr].mean()
            acc["A1"][r, te] = np.where(t[te] == 1, y[tr][t[tr] == 1].mean(), y[tr][t[tr] == 0].mean())
            for m, cat, tuned in (("B10_fixed", TIER_A, False), ("B10_tuned", TIER_A, True), ("B4_tuned", CELL4, True)):
                p = _pipe(cat, kind, tuned).fit(df.iloc[tr], y[tr])
                acc[m][r, te] = p.predict_proba(df.iloc[te])[:, 1] if kind == "binary" else p.predict(df.iloc[te])
            for k, spec in LLM.items():
                x = df[f"y_{spec}"].to_numpy(float)
                acc[f"{k}_recal"][r, te] = _recal(x[tr], y[tr], x[te], kind)
    out = pd.DataFrame({m: v.mean(0) for m, v in acc.items()})
    for k, spec in LLM.items():
        out[k] = df[f"y_{spec}"].to_numpy(float)
    return out


# ----------------------------------------------------------------------------- metrics
def _ece(y, p, bins=5):
    e = np.clip((p * bins).astype(int), 0, bins - 1)
    return float(sum(abs(y[e == b].mean() - p[e == b].mean()) * (e == b).mean() for b in range(bins) if (e == b).any()))


def _slope(y, p):
    import statsmodels.api as sm
    if np.unique(p).size < 3:
        return np.nan
    lp = np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4)))
    try:
        return float(sm.Logit(y, sm.add_constant(lp)).fit(disp=0).params[1])
    except Exception:
        return np.nan


def _group_err(df, p, y, by, lo, hi):
    errs, ns = [], []
    for col in by:
        for _, ix in df.groupby(col).indices.items():
            if lo <= len(ix) < hi:
                errs.append(abs(p[ix].mean() - y[ix].mean()))
                ns.append(len(ix))
    return (float(np.average(errs, weights=ns)) if by == ["cell"] else float(np.mean(errs))) if errs else np.nan, len(errs)


def metrics(df, y, p, t, kind, hard, small_groups=True):
    m = {"n": len(y), "bias": float(p.mean() - y.mean()),
         "ate_pred": float(p[t == 1].mean() - p[t == 0].mean()),
         "ate_human": float(y[t == 1].mean() - y[t == 0].mean())}
    m["ate_diff"] = m["ate_pred"] - m["ate_human"]
    m["sd_ratio"] = float(p.std() / y.std())
    if kind == "binary":
        pc = np.clip(p, .01, .99)
        m.update(brier=float(np.mean((y - p) ** 2)),
                 logloss=float(-np.mean(y * np.log(pc) + (1 - y) * np.log(1 - pc))),
                 accuracy=float(np.mean((p >= .5) == (y == 1))),
                 ece=np.nan if hard else _ece(y, p), cal_slope=np.nan if hard else _slope(y, p),
                 tv=float(abs(p.mean() - y.mean())))
    else:
        lv = np.arange(1, 10)
        ph = np.array([np.mean(y == v) for v in lv])
        pp = np.array([np.mean(np.clip(np.round(p), 1, 9) == v) for v in lv])
        m.update(mae=float(np.mean(np.abs(y - p))), mse=float(np.mean((y - p) ** 2)), tv=float(.5 * np.abs(ph - pp).sum()))
    g = df[df.cell != "OTHER"]
    gi = g.index.to_numpy()
    sub = g.reset_index(drop=True)
    m["cell_mae"], m["n_cells"] = _group_err(sub, p[gi], y[gi], ["cell"], MIN_CELL, 10 ** 9)
    if small_groups:
        m["small_group_mae"], m["n_small_groups"] = _group_err(df, p, y, TIER_A, SMALL_LO, SMALL_HI)
    return m


def strat_boot(t, rng):
    return np.concatenate([rng.choice(np.flatnonzero(t == a), (t == a).sum()) for a in (0, 1)])


# ----------------------------------------------------------------------------- main
def run_study(study: str, kind: str) -> tuple[list[dict], dict]:
    df = pd.read_parquet(BUNDLE / f"{study}.parquet")
    assert "pid" not in df.columns and "TWIN_ID" not in df.columns
    df["edu3"] = df.education.map(EDU3)
    assert df.edu3.notna().all()
    y, t = df.y_human.to_numpy(float), df.treat.to_numpy()
    P = oof_predictions(df, kind)
    hard = set(LLM)
    point = {m: metrics(df, y, P[m].to_numpy(), t, kind, m in hard) for m in P.columns}
    rng = np.random.default_rng(SEED)
    keys = ["brier", "logloss", "accuracy", "ece", "cal_slope"] if kind == "binary" else ["mae", "mse"]
    keys += ["ate_pred", "ate_diff", "sd_ratio", "tv", "cell_mae", "small_group_mae"]
    boot = {m: {k: [] for k in keys} for m in P.columns}
    loss = "brier" if kind == "binary" else "mse"
    diffs = {m: {"vs_A1": [], "vs_A0": []} for m in P.columns}
    for _ in range(NB):
        ix = strat_boot(t, rng)
        d = df.iloc[ix].reset_index(drop=True)
        mb = {m: metrics(d, y[ix], P[m].to_numpy()[ix], t[ix], kind, m in hard, small_groups=True) for m in P.columns}
        for m in P.columns:
            for k in keys:
                boot[m][k].append(mb[m].get(k, np.nan))
            diffs[m]["vs_A1"].append(mb["A1"][loss] - mb[m][loss])
            diffs[m]["vs_A0"].append(mb["A0"][loss] - mb[m][loss])
    ci = lambda v: [float(np.nanquantile(v, .025)), float(np.nanquantile(v, .975))] if np.isfinite(v).any() else [np.nan, np.nan]
    rows = []
    for m in P.columns:
        r = {"study": study, "model": m, **point[m]}
        for k in keys:
            r[f"{k}_ci"] = ci(np.asarray(boot[m][k], float))
        r[f"{loss}_gain_vs_A1"] = point["A1"][loss] - point[m][loss]
        r[f"{loss}_gain_vs_A1_ci"] = ci(np.asarray(diffs[m]["vs_A1"]))
        r[f"{loss}_gain_vs_A0"] = point["A0"][loss] - point[m][loss]
        r[f"{loss}_gain_vs_A0_ci"] = ci(np.asarray(diffs[m]["vs_A0"]))
        rows.append(r)
    # reuse Modal treatment-effect CIs for raw published rows (10,000 resamples); assert identical point estimates
    for r in rows:
        if r["model"] in LLM:
            a = json.loads((MODAL / f"A__{study}__{LLM[r['model']]}.json").read_text())
            assert abs(a["llm_ate"] - r["ate_pred"]) < 1e-9 and abs(a["human_ate"] - r["ate_human"]) < 1e-9
            r["ate_pred_ci"], r["ate_diff_ci"], r["ate_source"] = a["llm_ate_ci"], a["diff_llm_minus_human_ci"], "modal_full-20261114 (10k)"
            b = json.loads((MODAL / f"B__{study}__{LLM[r['model']]}.json").read_text())
            assert abs(b["individual"]["sd_ratio"] - r["sd_ratio"]) < 1e-9
            assert abs(b["distribution"]["total_variation"] - r["tv"]) < 1e-9
            r["sd_ratio_ci"] = b["individual_ci"]["sd_ratio"]
        else:
            r["ate_source"] = "this script (2k)"
    # paired: C vs E and C vs B (same loss)
    extra = {}
    pairs = [("E", "C_t0"), ("E_recal", "C_t0_recal"), ("C_t0_recal", "B10_tuned"), ("E_recal", "B10_tuned"),
             ("C_t0_recal", "A1"), ("B10_tuned", "A1"), ("B4_tuned", "A1"), ("C_t0_recal", "empty_recal")]
    for a, b in pairs:
        la = (y - P[a].to_numpy()) ** 2
        lb = (y - P[b].to_numpy()) ** 2
        d = lb - la                               # positive = a better
        bs = [d[strat_boot(t, rng)].mean() for _ in range(NB)]
        extra[f"{a}_minus_{b}_sqloss_gain"] = {"est": float(d.mean()), "ci": ci(np.asarray(bs))}
    return rows, extra


def main():
    all_rows, extras = [], {}
    for s, k in STUDIES.items():
        rows, ex = run_study(s, k)
        all_rows += rows
        extras[s] = ex
        print(s, "done")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/benchmark_offline.json").write_text(json.dumps({"rows": all_rows, "paired": extras}, indent=1, default=float))
    print(json.dumps(extras, indent=1, default=float))


if __name__ == "__main__":
    main()
