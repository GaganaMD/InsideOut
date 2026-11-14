"""EXPLORATORY follow-up (added after the holdout was inspected; not pre-registered).

Question: does a measured psychological value (GREEN) improve prediction of the hypothetical green-energy
choice beyond census-observable demographics?

Data: default_eric, TRAIN split only (the frozen test split is not read). Identical participants and identical
stratified 5-fold assignment for every model; all preprocessing (one-hot, standardisation) fitted inside each fold.

Feature timing:
  pre-decision person features  : Tier A demographics, GREEN (knowable about the person before any choice)
  choice-architecture condition : default (randomised; known only once the choice is presented, set by the designer)

Models (logistic regression, L2, C fixed at 1.0 — fixed in advance, no tuning):
  M0  training-fold prevalence
  M1  Tier A
  M1D Tier A + default
  M2  Tier A + GREEN
  M3  Tier A + GREEN + default
Key contrasts: M1-M0, M2-M1 (GREEN, no default), M3-M1D (GREEN holding default constant), M1D-M1 (default).

'Practically meaningful' threshold, set before running: Brier improvement >= 0.010 (about 4% of the
prevalence-baseline Brier) with a 95% bootstrap CI excluding 0. Smaller significant gains are 'detectable but small'.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import statsmodels.api as sm  # noqa: E402
from sklearn.compose import ColumnTransformer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score  # noqa: E402
from sklearn.model_selection import StratifiedKFold  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, SEED, TIER_A, load_green  # noqa: E402

OUT = ROOT / "reports/exploratory"
N_BOOT = 2000
MEANINGFUL_BRIER = 0.010
MODELS = {
    "M0": dict(cat=[], num=[], label="Prevalence baseline"),
    "M1": dict(cat=TIER_A, num=[], label="Tier A demographics"),
    "M1D": dict(cat=TIER_A, num=["green_default"], label="Tier A + default"),
    "M2": dict(cat=TIER_A, num=["green"], label="Tier A + GREEN"),
    "M3": dict(cat=TIER_A, num=["green", "green_default"], label="Tier A + GREEN + default"),
}
CONTRASTS = [("M1", "M0"), ("M2", "M1"), ("M1D", "M1"), ("M3", "M1D"), ("M3", "M2")]
FEATURE_TIMING = {"Tier A demographics": "pre-decision (person)", "GREEN": "pre-decision (person, measured by survey)",
                  "default": "choice architecture (known only when the choice is presented; set by the designer)"}


def load_train() -> pd.DataFrame:
    g = load_green()
    tr = g[g.split == "train"].sort_values("pid").reset_index(drop=True)
    assert (tr.split == "train").all()
    return tr


def folds(y: np.ndarray, seed: int = SEED) -> np.ndarray:
    f = np.empty(len(y), dtype=int)
    for k, (_, te) in enumerate(StratifiedKFold(5, shuffle=True, random_state=seed).split(np.zeros(len(y)), y)):
        f[te] = k
    return f


def make_model(spec: dict):
    parts = []
    if spec["cat"]:
        parts.append(("oh", OneHotEncoder(handle_unknown="ignore"), spec["cat"]))
    if spec["num"]:
        parts.append(("sc", StandardScaler(), spec["num"]))
    return make_pipeline(ColumnTransformer(parts), LogisticRegression(C=1.0, max_iter=2000))


def oof_predictions(df: pd.DataFrame, fold: np.ndarray) -> pd.DataFrame:
    """Out-of-fold P(chose_green) for every model; every transform is fitted on the training folds only."""
    y = df.chose_green.to_numpy()
    X = df[TIER_A].astype(str).join(df[["green", "green_default"]].astype(float))
    out = pd.DataFrame({"pid": df.pid, "y": y, "fold": fold})
    for name, spec in MODELS.items():
        p = np.empty(len(df))
        for k in range(5):
            trn, tst = fold != k, fold == k
            if name == "M0":
                p[tst] = y[trn].mean()
            else:
                p[tst] = make_model(spec).fit(X[trn], y[trn]).predict_proba(X[tst])[:, 1]
        out[name] = p
    return out


def metrics(y, p) -> dict:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    auc = roc_auc_score(y, p) if np.unique(p).size > 1 and np.unique(y).size == 2 else np.nan
    return dict(brier=brier_score_loss(y, p), logloss=log_loss(y, p, labels=[0, 1]), auc=auc)


def calibration(y, p) -> dict:
    """Calibration-in-the-large, logistic calibration slope, and 5-bin (quantile) ECE."""
    p = np.clip(p, 1e-6, 1 - 1e-6)
    lp = np.log(p / (1 - p))
    if np.std(lp) < 1e-9:  # constant predictor: slope undefined
        slope = np.nan
    else:
        slope = sm.Logit(y, sm.add_constant(lp)).fit(disp=0).params[1]
    citl = y.mean() - p.mean()
    bins = pd.qcut(p, 5, labels=False, duplicates="drop") if np.unique(p).size > 5 else np.zeros(len(p), int)
    t = pd.DataFrame({"y": y, "p": p, "b": bins}).groupby("b").agg(n=("y", "size"), obs=("y", "mean"), pred=("p", "mean"))
    ece = float((t.n * (t.obs - t.pred).abs()).sum() / len(y))
    return dict(calib_in_large=citl, calib_slope=slope, ece_5bin=ece, table=t.reset_index().to_dict("records"))


def paired_bootstrap(oof: pd.DataFrame, a: str, b: str, rng) -> dict:
    """Participant-level bootstrap of metric(a) - metric(b); negative Brier/logloss = a is better."""
    y = oof.y.to_numpy()
    pa, pb = oof[a].to_numpy(), oof[b].to_numpy()
    point = {k: metrics(y, pa)[k] - metrics(y, pb)[k] for k in ("brier", "logloss", "auc")}
    draws = {k: [] for k in point}
    n = len(y)
    for _ in range(N_BOOT):
        i = rng.integers(0, n, n)
        ma, mb = metrics(y[i], pa[i]), metrics(y[i], pb[i])
        for k in draws:
            draws[k].append(ma[k] - mb[k])
    res = {}
    for k, v in point.items():
        d = np.array(draws[k], dtype=float)
        d = d[~np.isnan(d)]
        res[k] = dict(diff=v, lo=float(np.quantile(d, .025)) if d.size else np.nan,
                      hi=float(np.quantile(d, .975)) if d.size else np.nan)
    br = res["brier"]
    if br["hi"] < 0 and -br["diff"] >= MEANINGFUL_BRIER:
        verdict = "practically meaningful improvement"
    elif br["hi"] < 0:
        verdict = "detectable but small improvement"
    elif br["lo"] > 0:
        verdict = "worse"
    else:
        verdict = "no detectable difference"
    return dict(contrast=f"{a} vs {b}", **{f"{k}_{s}": res[k][s] for k in res for s in ("diff", "lo", "hi")},
                verdict=verdict)


def fold_seed_robustness(df: pd.DataFrame, seeds=(1, 2, 3, 4, 5)) -> pd.DataFrame:
    rows = []
    for s in seeds:
        oof = oof_predictions(df, folds(df.chose_green.to_numpy(), seed=s))
        for a, b in CONTRASTS:
            rows.append(dict(fold_seed=s, contrast=f"{a} vs {b}",
                             brier_diff=metrics(oof.y, oof[a])["brier"] - metrics(oof.y, oof[b])["brier"]))
    return pd.DataFrame(rows)


def plot_calibration(oof: pd.DataFrame, cal: dict, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], color="#888", lw=1, ls="--", label="perfect calibration")
    colors = {"M1": "#4C72B0", "M1D": "#8172B2", "M2": "#55A868", "M3": "#C44E52"}
    for m, c in colors.items():
        t = pd.DataFrame(cal[m]["table"])
        ax.plot(t.pred, t.obs, marker="o", color=c, label=f"{m}: {MODELS[m]['label']}")
    ax.axhline(oof.y.mean(), color="#bbb", lw=1, label="M0 prevalence")
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="Mean predicted P(choose renewable)", ylabel="Observed share",
           title="Out-of-fold calibration (train, 5 quantile bins)")
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def write_report(df, oof, perf, comp, cal, rob, path: Path) -> None:
    L = ["# EXPLORATORY: do measured values beat demographics for predicting the green choice?", "",
         "> **Exploratory follow-up, not pre-registered.** It was added after the frozen holdout had been inspected. "
         "It uses the **training split only** (the test split is not read), and none of the original hypotheses, "
         "results or persona estimates were changed. The outcome is a **hypothetical** scenario choice "
         "($39/month renewable vs $32), not a purchase.", "",
         f"Data: `default_eric`, n = {len(df)} train participants ({int(df.chose_green.sum())} chose renewable). "
         "The same participants and the same stratified 5-fold split are used for every model. One-hot encoding "
         "and standardisation are fitted inside each training fold. The model is L2 logistic regression with C = 1.0, "
         "fixed in advance.", "",
         "**Feature timing:** Tier A demographics and GREEN are *pre-decision* facts about the person. The default "
         "is *choice architecture*: it is known only once the choice is presented, and it is set by whoever designs "
         "the offer, not by the person.", "",
         "## Out-of-fold performance", "",
         "| Model | Features | Brier | Log loss | AUC | Calibration-in-the-large | Calibration slope | ECE (5 bins) |",
         "|---|---|---|---|---|---|---|---|"]
    for m, r in perf.iterrows():
        L.append(f"| {m} | {MODELS[m]['label']} | {r.brier:.4f} | {r.logloss:.4f} | "
                 f"{'undefined' if np.isnan(r.auc) or m == 'M0' else f'{r.auc:.3f}'} | {r.calib_in_large:+.3f} | "
                 f"{'–' if np.isnan(r.calib_slope) else f'{r.calib_slope:.2f}'} | {r.ece_5bin:.3f} |")
    L += ["", "AUC is undefined for M0, which predicts a near-constant prevalence. A calibration slope below 1 "
          "means the predictions are too extreme; above 1, too timid.", "",
          f"## Paired differences (A − B; participant bootstrap, {N_BOOT} resamples; negative Brier or log loss = A better)", "",
          "| Contrast | ΔBrier (95% CI) | ΔLog loss (95% CI) | ΔAUC (95% CI) | Verdict |", "|---|---|---|---|---|"]
    for _, c in comp.iterrows():
        auc = "–" if np.isnan(c.auc_diff) or "M0" in c.contrast else f"{c.auc_diff:+.3f} ({c.auc_lo:+.3f}, {c.auc_hi:+.3f})"
        L.append(f"| {c.contrast} | {c.brier_diff:+.4f} ({c.brier_lo:+.4f}, {c.brier_hi:+.4f}) | "
                 f"{c.logloss_diff:+.4f} ({c.logloss_lo:+.4f}, {c.logloss_hi:+.4f}) | {auc} | {c.verdict} |")
    c = comp.set_index("contrast")
    L += ["", "## Reading", "",
          f"- **Demographics alone add no predictive value.** M1's Brier is {perf.loc['M1', 'brier']:.3f} vs "
          f"{perf.loc['M0', 'brier']:.3f} for prevalence, worse under every fold seed. Its calibration slope of "
          f"{perf.loc['M1', 'calib_slope']:.2f} shows over-fitted, too-extreme predictions: about 40 one-hot "
          f"columns on {len(df)} people.",
          f"- **One measured value carries the signal.** Adding GREEN to demographics improves Brier by "
          f"{-c.loc['M2 vs M1', 'brier_diff']:.3f} and AUC by {c.loc['M2 vs M1', 'auc_diff']:+.2f}. Holding the "
          f"default constant (M3 vs M1D), the gain is {-c.loc['M3 vs M1D', 'brier_diff']:.3f}. Both clear the "
          "pre-set threshold under all six fold assignments.",
          f"- **The randomised default adds a smaller, borderline amount** once GREEN is in the model "
          f"(ΔBrier {c.loc['M3 vs M2', 'brier_diff']:+.3f}).",
          f"- **Even the best model (M3) is modest:** AUC {perf.loc['M3', 'auc']:.2f}, Brier "
          f"{perf.loc['M3', 'brier']:.3f} vs {perf.loc['M0', 'brier']:.3f}. All models are over-extreme "
          "(calibration slope < 1). Recalibration or stronger regularisation would help, but was not tuned here.",
          "- **Caveats:** a single 428-person training split; a hypothetical outcome; C fixed rather than tuned. "
          "Unregularised or GREEN-only models were not run."]
    L += ["", f"*Practically meaningful* was fixed before running: a Brier improvement of at least {MEANINGFUL_BRIER} "
          "with a CI excluding 0.", "",
          "## Robustness to fold assignment (ΔBrier, 5 other fold seeds)", "",
          rob.groupby("contrast").brier_diff.agg(["min", "median", "max"]).round(4).to_markdown(), "",
          "![calibration](calibration_oof.png)", ""]
    path.write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_train()
    fold = folds(df.chose_green.to_numpy())
    oof = oof_predictions(df, fold)
    oof.to_csv(OUT / "oof_predictions.csv", index=False)
    perf, cal = {}, {}
    for m in MODELS:
        cal[m] = calibration(oof.y.to_numpy(), oof[m].to_numpy())
        perf[m] = {**metrics(oof.y, oof[m]), **{k: v for k, v in cal[m].items() if k != "table"}}
    perf = pd.DataFrame(perf).T
    perf.loc["M0", ["auc", "calib_slope"]] = np.nan  # near-constant predictor: AUC/slope not meaningful
    rng = np.random.default_rng(SEED)
    comp = pd.DataFrame([paired_bootstrap(oof, a, b, rng) for a, b in CONTRASTS])
    rob = fold_seed_robustness(df)
    med = rob.groupby("contrast").brier_diff.median()
    borderline = comp.verdict.eq("practically meaningful improvement") & (-comp.contrast.map(med) < MEANINGFUL_BRIER)
    comp.loc[borderline, "verdict"] = "borderline: meaningful in main run, below threshold in median of other fold seeds"
    perf.round(4).to_csv(OUT / "performance.csv")
    comp.round(5).to_csv(OUT / "paired_differences.csv", index=False)
    rob.round(5).to_csv(OUT / "fold_seed_robustness.csv", index=False)
    json.dump({m: c["table"] for m, c in cal.items()}, open(OUT / "calibration_tables.json", "w"), indent=1, default=float)
    json.dump({"n": len(df), "feature_timing": FEATURE_TIMING, "meaningful_brier": MEANINGFUL_BRIER,
               "fold_counts": pd.Series(fold).value_counts().sort_index().tolist()},
              open(OUT / "meta.json", "w"), indent=1)
    plot_calibration(oof, cal, OUT / "calibration_oof.png")
    write_report(df, oof, perf, comp, cal, rob, OUT / "values_vs_demographics.md")
    print(perf.round(4).to_string())
    print(comp.round(4).to_string(index=False))
    print(rob.groupby("contrast").brier_diff.agg(["min", "median", "max"]).round(4))


if __name__ == "__main__":
    main()
