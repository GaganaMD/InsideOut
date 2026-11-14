"""Offline overnight experiments (pre-specified; no API calls; training participants only; no new holdout analysis).

Inputs: the pseudonymous bundle written by prepare_bundle.py (one parquet per study). Each TASK is independent,
deterministic (seeded) and writes one JSON result, so a batch can be checkpointed and resumed per task.

A  effect_recovery  (study x published GPT-4.1 spec)
   Human ATE = mean(y | treated) - mean(y | control) on the randomised human data. LLM ATE = the same contrast on the
   published simulated answers for the SAME participants under the SAME assigned condition. Reported raw and
   standardised by the pooled within-arm human SD. Uncertainty: paired participant bootstrap stratified by arm
   (human and LLM answers of a participant are resampled together, so their covariance is kept).
B  calibration      (study x spec)
   Individual matched comparison: bias, SD ratio (LLM/human; <1 = compressed heterogeneity), correlation, accuracy and
   Brier (binary) or MAE and exact-match (1-9 rating) against a constant human-mean baseline, total-variation distance
   between response distributions. Cell level: demographic cells (k>=5 in the full panel) with >= MIN_CELL training
   members; correlation and SD ratio of cell means. Participant bootstrap (individual) and cell cluster bootstrap (cell).
C  information_value (study)
   Repeated stratified 5-fold CV WITHIN TRAINING ONLY predicting the human outcome. Every model includes the randomised
   condition. M0 condition; M1 +Tier A; M2 +6 attitude scores; M3 +Tier A +attitudes; M4 +Tier A +published
   full-persona LLM answer; M5 +LLM answer only. Logistic (L2, C=1) for binary, ridge (alpha=1) for ratings; fixed, no
   tuning. Loss: Brier / squared error, averaged per participant over repeats, then paired participant bootstrap of
   model differences. Preprocessing is fitted inside each fold.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261114
from tasklist import SPECS, STUDIES, all_tasks  # noqa: F401
TIER_A = ["region", "sex", "age_band", "education", "race", "citizen", "marital", "income", "hh_size", "employment"]
MIN_CELL = 8


def load(data_dir: Path, study: str) -> pd.DataFrame:
    df = pd.read_parquet(Path(data_dir) / f"{study}.parquet")
    assert "pid" not in df.columns and "TWIN_ID" not in df.columns
    return df


def _ci(x) -> list[float]:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return [float(np.quantile(x, .025)), float(np.quantile(x, .975))] if len(x) else [np.nan, np.nan]


def _strat_boot(treat: np.ndarray, rng) -> np.ndarray:
    idx = []
    for a in (0, 1):
        ix = np.flatnonzero(treat == a)
        idx.append(rng.choice(ix, len(ix)))
    return np.concatenate(idx)


# ----------------------------------------------------------------------------- A
def effect_recovery(df: pd.DataFrame, spec: str, nb: int) -> dict:
    t, yh, yl = df.treat.to_numpy(), df.y_human.to_numpy(float), df[f"y_{spec}"].to_numpy(float)

    def stats(ix):
        tt, h, l = t[ix], yh[ix], yl[ix]
        ah = h[tt == 1].mean() - h[tt == 0].mean()
        al = l[tt == 1].mean() - l[tt == 0].mean()
        sd = np.sqrt(((tt == 1).sum() * h[tt == 1].var() + (tt == 0).sum() * h[tt == 0].var()) / len(tt))
        return ah, al, al - ah, al / ah if ah != 0 else np.nan, ah / sd, al / sd
    est = stats(np.arange(len(t)))
    rng = np.random.default_rng(SEED)
    B = np.array([stats(_strat_boot(t, rng)) for _ in range(nb)])
    names = ["human_ate", "llm_ate", "diff_llm_minus_human", "ratio_llm_over_human", "human_std_effect", "llm_std_effect"]
    out = {n: float(v) for n, v in zip(names, est)}
    out.update({f"{n}_ci": _ci(B[:, i]) for i, n in enumerate(names)})
    out.update(sign_agrees=bool(np.sign(est[0]) == np.sign(est[1])),
               boot_share_same_sign=float(np.mean(np.sign(B[:, 0]) == np.sign(B[:, 1]))),
               human_ci_excludes_0=bool(_ci(B[:, 0])[0] > 0 or _ci(B[:, 0])[1] < 0),
               llm_ci_excludes_0=bool(_ci(B[:, 1])[0] > 0 or _ci(B[:, 1])[1] < 0),
               arm_means={"human": [float(yh[t == 0].mean()), float(yh[t == 1].mean())],
                          "llm": [float(yl[t == 0].mean()), float(yl[t == 1].mean())]},
               n=int(len(t)), n_treated=int(t.sum()), bootstrap="paired participant bootstrap stratified by arm", nb=nb)
    return out


# ----------------------------------------------------------------------------- B
def _indiv(yh, yl, kind):
    r = np.corrcoef(yh, yl)[0, 1] if yl.std() > 0 and yh.std() > 0 else np.nan
    m = {"bias": yl.mean() - yh.mean(), "sd_ratio": yl.std() / yh.std() if yh.std() > 0 else np.nan, "corr": r}
    if kind == "binary":
        m.update(accuracy=np.mean((yl >= .5) == (yh == 1)), brier=np.mean((yh - yl) ** 2),
                 brier_constant_baseline=np.mean((yh - yh.mean()) ** 2))
    else:
        m.update(mae=np.mean(np.abs(yh - yl)), mae_constant_baseline=np.mean(np.abs(yh - yh.mean())),
                 exact_match=np.mean(np.round(yl) == yh))
    return m


def calibration(df: pd.DataFrame, spec: str, kind: str, nb: int) -> dict:
    yh, yl, t = df.y_human.to_numpy(float), df[f"y_{spec}"].to_numpy(float), df.treat.to_numpy()
    levels = [0, 1] if kind == "binary" else list(range(1, 10))
    ph = np.array([np.mean(yh == v) for v in levels])
    pl = np.array([np.mean(np.round(yl) == v) for v in levels])
    est = _indiv(yh, yl, kind)
    rng = np.random.default_rng(SEED)
    boots = [_indiv(yh[ix], yl[ix], kind) for ix in (_strat_boot(t, rng) for _ in range(nb))]
    out = {"individual": {k: float(v) for k, v in est.items()},
           "individual_ci": {k: _ci([b[k] for b in boots]) for k in est},
           "by_arm": {str(a): {k: float(v) for k, v in _indiv(yh[t == a], yl[t == a], kind).items()} for a in (0, 1)},
           "distribution": {"levels": levels, "human": ph.tolist(), "llm": pl.tolist(),
                            "total_variation": float(0.5 * np.abs(ph - pl).sum())}}
    g = df[df.cell != "OTHER"].groupby("cell")
    size = g.size()
    keep = size[size >= MIN_CELL].index
    cm = pd.DataFrame({"h": g.y_human.mean()[keep], "l": g[f"y_{spec}"].mean()[keep], "n": size[keep]})
    if len(cm) >= 3:
        def cstats(c):
            return (np.corrcoef(c.h, c.l)[0, 1] if c.l.std() > 0 and c.h.std() > 0 else np.nan,
                    c.l.std() / c.h.std() if c.h.std() > 0 else np.nan)
        cb = np.array([cstats(cm.iloc[rng.integers(0, len(cm), len(cm))]) for _ in range(nb)])
        r, s = cstats(cm)
        out["cell"] = {"n_cells": int(len(cm)), "n_people": int(cm.n.sum()), "min_cell": MIN_CELL,
                       "corr_cell_means": float(r), "corr_ci": _ci(cb[:, 0]),
                       "sd_ratio_cell_means": float(s), "sd_ratio_ci": _ci(cb[:, 1]),
                       "note": "cell means mix sampling noise (small cells) with true heterogeneity; human cell SD is inflated by noise"}
    out.update(n=int(len(df)), nb=nb)
    return out


# ----------------------------------------------------------------------------- C
MODELS = {"M0_condition": ([], False, None), "M1_tierA": (TIER_A, False, None), "M2_attitudes": ([], True, None),
          "M3_tierA_attitudes": (TIER_A, True, None), "M4_tierA_llm": (TIER_A, False, "full_persona_t07"),
          "M5_llm_only": ([], False, "full_persona_t07")}
CONTRASTS = [("M1_tierA", "M0_condition"), ("M2_attitudes", "M0_condition"), ("M3_tierA_attitudes", "M1_tierA"),
             ("M3_tierA_attitudes", "M2_attitudes"), ("M4_tierA_llm", "M1_tierA"), ("M2_attitudes", "M5_llm_only")]


def _pipe(cat, att, llm, cols, kind):
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    num = ["treat"] + ([c for c in cols if c.startswith("att_")] if att else []) + ([f"y_{llm}"] if llm else [])
    tr = [("num", StandardScaler(), num)] + ([("cat", OneHotEncoder(handle_unknown="ignore"), cat)] if cat else [])
    est = LogisticRegression(C=1.0, max_iter=2000) if kind == "binary" else Ridge(alpha=1.0)
    return make_pipeline(ColumnTransformer(tr), est)


def information_value(df: pd.DataFrame, kind: str, repeats: int, nb: int) -> dict:
    from sklearn.model_selection import StratifiedKFold
    y = df.y_human.to_numpy(float)
    strat = df.treat.astype(str) + "_" + (y if kind == "binary" else (y >= np.median(y)).astype(int)).astype(int).astype(str)
    loss = {m: np.zeros((repeats, len(df))) for m in MODELS}
    for r in range(repeats):
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED + r).split(df, strat):
            for m, (cat, att, llm) in MODELS.items():
                p = _pipe(cat, att, llm, df.columns, kind).fit(df.iloc[tr], y[tr])
                pred = p.predict_proba(df.iloc[te])[:, 1] if kind == "binary" else p.predict(df.iloc[te])
                loss[m][r, te] = (y[te] - pred) ** 2
    per = {m: v.mean(0) for m, v in loss.items()}                       # per-participant loss averaged over repeats
    base = float(np.mean((y - y.mean()) ** 2))
    rng = np.random.default_rng(SEED)
    idx = [rng.integers(0, len(y), len(y)) for _ in range(nb)]
    res = {"loss": "brier" if kind == "binary" else "squared_error", "constant_baseline_loss": base,
           "models": {m: {"mean_loss": float(v.mean()), "skill_vs_constant": float(1 - v.mean() / base),
                          "sd_over_repeats": float(loss[m].mean(1).std())} for m, v in per.items()},
           "contrasts": {}}
    for a, b in CONTRASTS:
        d = per[b] - per[a]                                             # positive = model a has LOWER loss (better)
        res["contrasts"][f"{a}_vs_{b}"] = {"loss_reduction": float(d.mean()), "ci": _ci([d[i].mean() for i in idx]),
                                           "share_of_baseline": float(d.mean() / base)}
    res.update(n=int(len(y)), repeats=repeats, folds=5, nb=nb)
    return res


# ----------------------------------------------------------------------------- dispatcher
def run_task(task: str, data_dir: Path, nb: int = 5000, repeats: int = 50) -> dict:
    exp, study, spec = task.split("|")
    df, kind = load(data_dir, study), STUDIES[study]
    if exp == "A":
        out = effect_recovery(df, spec, nb)
    elif exp == "B":
        out = calibration(df, spec, kind, nb)
    elif exp == "C":
        out = information_value(df, kind, repeats, min(nb, 2000))
    else:
        raise ValueError(task)
    return {"task": task, "experiment": exp, "study": study, "spec": spec, "outcome": kind, **out}


if __name__ == "__main__":                                              # local quick run: python experiments.py <bundle>
    import sys
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("bundle")
    for t in ["A|default_eric|demographics_t07", "B|targeting_fairness|full_persona_t07", "C|default_eric|cv"]:
        print(json.dumps(run_task(t, d, nb=200, repeats=2), default=float)[:600])
