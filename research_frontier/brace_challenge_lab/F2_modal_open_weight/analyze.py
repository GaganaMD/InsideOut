"""LOCAL. Score open-weight LLM persona predictions against human choices exactly as pre-registered (PREREGISTRATION.md).

    python analyze.py outputs/full__qwen25_7b.json [outputs/full__qwen3_4b.json ...]
Training participants only; human outcomes never leave this machine.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_prompts import CELL_FIELDS, SEED, cell_of  # noqa: E402
from common import load_green  # noqa: E402

NB = 2000
COND = ("green_default", "grey_default")


def humans() -> pd.DataFrame:
    g = load_green(corrected=True)
    g = g[g.split == "train"].copy()
    folds = pd.read_csv(HERE / "folds_local.csv").set_index("pid").fold
    g["cell"], g["fold"] = cell_of(g).to_numpy(), folds.loc[g.pid].to_numpy()
    cells = set(pd.read_csv(HERE / "profiles.csv").cell)
    g = g[g.cell.isin(cells)]
    return g[["pid", "cell", "fold", "green_condition", "chose_green", *CELL_FIELDS[:3], "education"]].rename(
        columns={"green_condition": "cond", "chose_green": "y"}).reset_index(drop=True)


def llm_table(path: Path) -> tuple[pd.DataFrame, dict]:
    out = json.loads(path.read_text(encoding="utf-8"))
    meta = {r["id"]: r for r in map(json.loads, (HERE / "prompts.jsonl").read_text(encoding="utf-8").splitlines())}
    rows = []
    for r in out["results"]:
        m = meta[r["id"]]
        pg = (r["pA"] if m["order"] == "AB" else r["pB"]) / r["mass"]
        rows.append({"fmt": m["fmt"], "cond": m["cond"], "order": m["order"], "cell": m["cell"], "fold": m["fold"],
                     "p_green": pg, "mass": r["mass"]})
    t = pd.DataFrame(rows)
    info = {k: out[k] for k in ("model_id", "revision", "license", "gpu", "load_s", "score_s", "n_prompts")}
    info.update(mean_mass=float(t.mass.mean()), share_mass_below_0_5=float((t.mass < 0.5).mean()),
                order_gap_mean_abs=float(t.pivot_table(index=["fmt", "cond", "cell", "fold"], columns="order",
                                                       values="p_green").diff(axis=1).abs().iloc[:, 1].mean()))
    return t.groupby(["fmt", "cond", "cell", "fold"], as_index=False).p_green.mean(), info


def baselines(h: pd.DataFrame) -> pd.DataFrame:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import OneHotEncoder
    h = h.copy()
    X = pd.DataFrame([c.split(" | ") for c in h.cell], columns=CELL_FIELDS).assign(cond=h.cond.to_numpy())
    for f in (0, 1):
        fit, te = (h.fold == 1 - f).to_numpy(), (h.fold == f).to_numpy()
        h.loc[te, "A_population"] = h[fit].groupby("cond").y.mean().reindex(h.loc[te, "cond"]).to_numpy()
        enc = OneHotEncoder(handle_unknown="ignore").fit(X[fit])
        lr = LogisticRegression(C=1.0, max_iter=2000).fit(enc.transform(X[fit]), h.y[fit])
        h.loc[te, "B_demographic_model"] = lr.predict_proba(enc.transform(X[te]))[:, 1]
    return h


def attach(h: pd.DataFrame, t: pd.DataFrame, tag: str) -> pd.DataFrame:
    h = h.copy()
    e = t[t.fmt == "empty"].set_index("cond").p_green
    h[f"{tag}:empty"] = e.reindex(h.cond).to_numpy()
    d = t[t.fmt == "demo"].set_index(["cell", "cond"]).p_green
    h[f"{tag}:demo"] = d.reindex(list(zip(h.cell, h.cond))).to_numpy()
    for fmt in ("profile", "narrative"):
        s = t[t.fmt == fmt].set_index(["cell", "cond", "fold"]).p_green
        h[f"{tag}:{fmt}"] = s.reindex(list(zip(h.cell, h.cond, h.fold))).to_numpy()
    return h


def counterfactual(h, t, tag, fmt):
    """Predicted P(green) for each participant under BOTH conditions (for the default-effect contrast)."""
    out = {}
    for cond in COND:
        hh = h.assign(cond=cond)
        out[cond] = attach(hh, t, tag)[f"{tag}:{fmt}"].to_numpy()
    return out[COND[0]] - out[COND[1]]


def calib(y, p):
    import statsmodels.api as sm
    p = np.clip(p, 1e-4, 1 - 1e-4)
    lp = np.log(p / (1 - p))
    if np.ptp(lp) < 1e-9:   # constant prediction (added 2026-11-15 for GPT-4.1 'empty'): slope undefined; was a crash
        return {"intercept": float("nan"), "slope": float("nan"), "note": "constant prediction; calibration undefined"}
    m = sm.GLM(y, sm.add_constant(lp), family=sm.families.Binomial()).fit()
    return {"intercept": float(m.params[0]), "slope": float(m.params[1])}


def analyse(paths: list[Path]) -> dict:
    h = baselines(humans())
    methods, tabs, infos = ["A_population", "B_demographic_model"], {}, {}
    for p in paths:
        t, info = llm_table(p)
        tag = info["model_id"].split("/")[-1]
        tabs[tag], infos[tag] = t, info
        h = attach(h, t, tag)
        methods += [f"{tag}:{f}" for f in ("empty", "demo", "profile", "narrative")]
    assert h[methods].notna().all().all()
    y = h.y.to_numpy(float)
    cells = h.cell.to_numpy()
    uc = np.unique(cells)
    idx_by_cell = {c: np.flatnonzero(cells == c) for c in uc}
    rng = np.random.default_rng(SEED)
    boots = []
    for _ in range(NB):
        pick = rng.choice(uc, len(uc))
        boots.append(np.concatenate([rng.choice(idx_by_cell[c], len(idx_by_cell[c])) for c in pick]))
    sq = {m: (y - h[m].to_numpy()) ** 2 for m in methods}

    def ci_diff(a, b):
        d = sq[a] - sq[b]
        bd = [d[ix].mean() for ix in boots]
        return {"diff": float(d.mean()), "ci": [float(np.quantile(bd, .025)), float(np.quantile(bd, .975))]}

    # human ATE (randomised) and predicted population-averaged contrasts, cluster bootstrap over cells
    tr = (h.cond == COND[0]).to_numpy()
    hum = y[tr].mean() - y[~tr].mean()
    hum_b = [y[ix][tr[ix]].mean() - y[ix][~tr[ix]].mean() for ix in boots]
    contrasts = {"human_ate": float(hum), "human_ci": [float(np.quantile(hum_b, .025)), float(np.quantile(hum_b, .975))]}
    res = {"n": int(len(h)), "n_cells": int(len(uc)), "models": infos, "methods": {}, "contrasts": {}}
    for m in methods:
        p = h[m].to_numpy()
        if m == "A_population":
            pc = np.full(len(h), np.nan)
        elif m == "B_demographic_model":
            pc = None
        else:
            tag, fmt = m.split(":")
            pc = counterfactual(h, tabs[tag], tag, fmt)
        r = {"brier": float(sq[m].mean()), "confidence_mean_abs_p_minus_half": float(np.mean(np.abs(p - .5))),
             "calibration": calib(y, p), "mean_pred": float(p.mean())}
        cm = h.assign(p=p).groupby(["cell", "cond"]).agg(p=("p", "mean"), ybar=("y", "mean"), n=("y", "size"))
        r["cell_mae_weighted"] = float(np.average(np.abs(cm.p - cm.ybar), weights=cm.n))
        r["cell_pred_sd_weighted"] = float(np.sqrt(np.average((cm.p - np.average(cm.p, weights=cm.n)) ** 2, weights=cm.n)))
        small = h.cell.map(h.cell.value_counts()).to_numpy() <= 3
        r["brier_small_cells_le3"] = float(sq[m][small].mean())
        r["n_small"] = int(small.sum())
        if pc is not None and not np.isnan(pc).all():
            est = float(pc.mean())
            bb = [pc[ix].mean() - (y[ix][tr[ix]].mean() - y[ix][~tr[ix]].mean()) for ix in boots]
            r["default_effect"] = {"predicted": est, "abs_error": abs(est - hum), "signed_error": est - hum,
                                   "signed_error_ci": [float(np.quantile(bb, .025)), float(np.quantile(bb, .975))]}
        if m.endswith(("profile", "narrative")):
            gz = pd.read_csv(HERE / "profiles.csv").set_index(["cell", "fold"]).green
            r["corr_with_green_z"] = float(np.corrcoef(p, gz.reindex(list(zip(h.cell, h.fold))).to_numpy())[0, 1])
        res["methods"][m] = r
    for m in methods[1:]:
        res["contrasts"][f"{m} - A_population"] = ci_diff(m, "A_population")
    for m in methods[2:]:
        res["contrasts"][f"{m} - B_demographic_model"] = ci_diff(m, "B_demographic_model")
    for tag in tabs:
        res["contrasts"][f"{tag}: profile - demo"] = ci_diff(f"{tag}:profile", f"{tag}:demo")
        res["contrasts"][f"{tag}: narrative - profile"] = ci_diff(f"{tag}:narrative", f"{tag}:profile")
        a, b = h[f"{tag}:narrative"].to_numpy(), h[f"{tag}:profile"].to_numpy()
        dc = np.abs(a - .5) - np.abs(b - .5)
        bd = [dc[ix].mean() for ix in boots]
        res["contrasts"][f"{tag}: narrative - profile (confidence)"] = {
            "diff": float(dc.mean()), "ci": [float(np.quantile(bd, .025)), float(np.quantile(bd, .975))]}
    res["human_default_effect"] = contrasts
    return res


if __name__ == "__main__":
    paths = [Path(p) for p in sys.argv[1:]]
    res = analyse(paths)
    (HERE / "results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "methods"}, indent=1)[:4000])
    for m, r in res["methods"].items():
        print(f"{m:38s} brier {r['brier']:.4f} conf {r['confidence_mean_abs_p_minus_half']:.3f} "
              f"cal {r['calibration']['intercept']:+.2f}/{r['calibration']['slope']:.2f} "
              f"effect {r.get('default_effect', {}).get('predicted', float('nan')):+.3f}")
