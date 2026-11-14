"""EXPLORATORY follow-up #2: redistribution. Pre-specified in reports/exploratory/redistribution/PRESPEC.md.

Does an independently measured (Twin, ~5 months earlier) redistributive-policy attitude improve out-of-fold
prediction of a stated redistribution attitude (Mega-Study `preference_redistribution`) beyond Tier A demographics?
TRAIN split only. No randomised condition exists in this survey, so condition models are not applicable.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PROC, RAW_TWIN, ROOT, SEED, TIER_A, load_people  # noqa: E402

OUT = ROOT / "reports/exploratory/redistribution"
N_BOOT = 2000
MEANINGFUL_R2 = 0.05
CONSTRUCT_COLS = {"redist": ["QID287_4", "QID287_5", "QID287_10"], "ideology": ["QID22"], "equality": ["QID29_21"]}
MODELS = {
    "M0": [], "M1": [], "M2": ["redist"], "M2_ideology": ["ideology"], "M2_equality": ["equality"],
}
LABELS = {"M0": "Training-fold mean", "M1": "Tier A demographics", "M2": "Tier A + redistributive policy support",
          "M2_ideology": "Tier A + ideology (sensitivity)", "M2_equality": "Tier A + EQUALITY value (sensitivity)"}
CONTRASTS = [("M1", "M0"), ("M2", "M1"), ("M2_ideology", "M1"), ("M2_equality", "M1"), ("M2", "M2_ideology")]
OUTCOMES = {"govt_help": "GOVT_RESPONSIBILITY", "tax_willing": "HLTHTAX"}


def verify_items() -> None:
    cat = json.load(open(RAW_TWIN / "question_catalog_and_human_response_csv/question_catalog.json", encoding="utf-8"))
    cat = {q["QuestionID"]: q for q in (cat if isinstance(cat, list) else cat.values())}
    rows = dict(zip(cat["QID287"]["csv_columns"], cat["QID287"]["Rows"]))
    assert "Medicare for All" in rows["QID287_4"] and "public option" in rows["QID287_5"] and "2% tax" in rows["QID287_10"]
    assert cat["QID287"]["Columns"][0] == "Strongly oppose" and cat["QID287"]["Columns"][-1] == "Strongly support"
    assert cat["QID22"]["Options"] == ["Very conservative", "Conservative", "Moderate", "Liberal", "Very liberal"]
    eq = dict(zip(cat["QID29"]["csv_columns"], cat["QID29"]["Rows"]))
    assert eq["QID29_21"].startswith("EQUALITY")


def load(outcome: str) -> pd.DataFrame:
    """Train participants with a valid (non-'don't know') outcome; constructs from Twin waves 1-3."""
    verify_items()
    people = load_people()
    twin = pd.read_csv(RAW_TWIN / "question_catalog_and_human_response_csv/wave1_3_response.csv",
                       usecols=["pid", *sum(CONSTRUCT_COLS.values(), [])])
    c = pd.DataFrame({"pid": twin.pid, "redist": twin[CONSTRUCT_COLS["redist"]].mean(axis=1),
                      "ideology": twin.QID22.astype(float), "equality": twin.QID29_21.astype(float)})
    r = pd.read_parquet(PROC / "mega_preference_redistribution.parquet")
    r = r[(r.ATTENTION_CHECK == 3) & r[OUTCOMES[outcome]].between(1, 5)].copy()
    r["pid"] = r.pid.astype(int)
    r["y"] = 6 - r[OUTCOMES[outcome]]  # higher = more pro-redistribution / more willing
    df = r[["pid", "y"]].merge(people[["pid", "split", *TIER_A]], on="pid").merge(c, on="pid")
    df = df[df.split == "train"].sort_values("pid").reset_index(drop=True)
    assert df.pid.is_unique
    return df


def folds(y: np.ndarray, seed: int = SEED) -> np.ndarray:
    f = np.empty(len(y), dtype=int)
    for k, (_, te) in enumerate(StratifiedKFold(5, shuffle=True, random_state=seed).split(np.zeros(len(y)), y)):
        f[te] = k
    return f


def make_model(num: list[str], binary: bool = False):
    parts = [("oh", OneHotEncoder(handle_unknown="ignore"), TIER_A)]
    if num:
        parts.append(("num", make_pipeline(SimpleImputer(strategy="mean"), StandardScaler()), num))
    est = LogisticRegression(C=1.0, max_iter=2000) if binary else Ridge(alpha=1.0)
    return make_pipeline(ColumnTransformer(parts), est)


def oof(df: pd.DataFrame, fold: np.ndarray, binary: bool = False) -> pd.DataFrame:
    y = (df.y >= 4).astype(int).to_numpy() if binary else df.y.to_numpy(float)
    X = df[TIER_A].astype(str).join(df[["redist", "ideology", "equality"]])
    out = pd.DataFrame({"pid": df.pid, "y": y, "fold": fold})
    for name, num in MODELS.items():
        p = np.empty(len(df))
        for k in range(5):
            trn, tst = fold != k, fold == k
            if name == "M0":
                p[tst] = y[trn].mean()
            else:
                m = make_model(num, binary).fit(X[trn], y[trn])
                p[tst] = m.predict_proba(X[tst])[:, 1] if binary else m.predict(X[tst])
        out[name] = p
    return out


def cont_metrics(y, p, p0) -> dict:
    return dict(mae=float(np.abs(y - p).mean()), r2=float(1 - ((y - p) ** 2).sum() / ((y - p0) ** 2).sum()))


def bin_metrics(y, p) -> dict:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    auc = roc_auc_score(y, p) if np.unique(p).size > 1 and np.unique(y).size == 2 else np.nan
    return dict(brier=brier_score_loss(y, p), logloss=log_loss(y, p, labels=[0, 1]), auc=auc)


def boot(o: pd.DataFrame, a: str, b: str, fn, keys, rng) -> dict:
    y = o.y.to_numpy()
    args = lambda i, m: (y[i], o[m].to_numpy()[i]) + ((o.M0.to_numpy()[i],) if fn is cont_metrics else ())
    allidx = np.arange(len(y))
    point = {k: fn(*args(allidx, a))[k] - fn(*args(allidx, b))[k] for k in keys}
    draws = {k: [] for k in keys}
    for _ in range(N_BOOT):
        i = rng.integers(0, len(y), len(y))
        ma, mb = fn(*args(i, a)), fn(*args(i, b))
        for k in keys:
            draws[k].append(ma[k] - mb[k])
    res = {"contrast": f"{a} vs {b}"}
    for k in keys:
        d = np.array(draws[k], float)
        d = d[~np.isnan(d)]
        res.update({f"d_{k}": point[k], f"d_{k}_lo": np.quantile(d, .025), f"d_{k}_hi": np.quantile(d, .975)})
    return res


def verdict_r2(r: dict) -> str:
    if r["d_r2_lo"] > 0 and r["d_r2"] >= MEANINGFUL_R2:
        return "practically meaningful improvement"
    if r["d_r2_lo"] > 0:
        return "detectable but small improvement"
    if r["d_r2_hi"] < 0:
        return "worse"
    return "no detectable difference"


def cronbach_alpha(items: pd.DataFrame) -> float:
    k = items.shape[1]
    return float(k / (k - 1) * (1 - items.var(ddof=1).sum() / items.sum(axis=1).var(ddof=1)))


def run_outcome(outcome: str, rng) -> dict:
    df = load(outcome)
    fold = folds(df.y.to_numpy())
    o = oof(df, fold)
    o.to_csv(OUT / f"oof_{outcome}.csv", index=False)
    perf = {m: cont_metrics(o.y.to_numpy(), o[m].to_numpy(), o.M0.to_numpy()) for m in MODELS}
    comp = []
    for a, b in CONTRASTS:
        r = boot(o, a, b, cont_metrics, ["mae", "r2"], rng)
        r["verdict"] = verdict_r2(r)
        comp.append(r)
    rob = []
    for s in (1, 2, 3, 4, 5):
        os_ = oof(df, folds(df.y.to_numpy(), s))
        for a, b in CONTRASTS:
            ra = cont_metrics(os_.y.to_numpy(), os_[a].to_numpy(), os_.M0.to_numpy())["r2"]
            rb = cont_metrics(os_.y.to_numpy(), os_[b].to_numpy(), os_.M0.to_numpy())["r2"]
            rob.append(dict(fold_seed=s, contrast=f"{a} vs {b}", d_r2=ra - rb))
    eff = {k: dict(spearman=float(df[k].corr(df.y, method="spearman")), n_nonmissing=int(df[k].notna().sum()))
           for k in ("redist", "ideology", "equality")}
    return dict(n=len(df), y_dist=df.y.value_counts().sort_index().to_dict(), perf=perf, comp=comp,
                robust=pd.DataFrame(rob).groupby("contrast").d_r2.agg(["min", "median", "max"]).round(4).to_dict("index"),
                effect=eff, df=df, fold=fold)


def run_binary(df: pd.DataFrame, fold: np.ndarray, rng) -> dict:
    o = oof(df, fold, binary=True)
    o.to_csv(OUT / "oof_govt_help_binary.csv", index=False)
    perf = {m: bin_metrics(o.y.to_numpy(), o[m].to_numpy()) for m in MODELS}
    comp = [boot(o, a, b, bin_metrics, ["brier", "logloss", "auc"], rng) for a, b in [("M1", "M0"), ("M2", "M1")]]
    return dict(prevalence=float(o.y.mean()), perf=perf, comp=comp)


def fmt_ci(d, k, nd=3):
    return f"{d[f'd_{k}']:+.{nd}f} ({d[f'd_{k}_lo']:+.{nd}f}, {d[f'd_{k}_hi']:+.{nd}f})"


def write_report(res: dict, binr: dict, alpha: float, green: pd.DataFrame) -> None:
    L = ["# EXPLORATORY: Does a measured redistribution attitude beat demographics?", "",
         "> **Exploratory follow-up, not part of the confirmatory analysis.** It was pre-specified in `PRESPEC.md` "
         "(committed before any model was fitted) and uses the **training split only**. The outcome is a **stated "
         "attitude**: there is no choice, cost or randomised condition, so models with an experimental condition "
         "(M3, M1 + condition) are **not applicable**. Predictor and outcome come from different surveys about "
         "5 months apart, but they measure **adjacent constructs**.", "",
         f"Construct: redistributive policy support is the mean of support for Medicare for All, a public option and "
         f"a 2% wealth tax (Twin `QID287_4/5/10`, 1–5). Cronbach's α on train is {alpha:.2f}.", ""]
    for oc, r in res.items():
        title = {"govt_help": "Primary: government responsibility to help the poor (1–5, higher = more government)",
                 "tax_willing": "Secondary: willingness to pay higher taxes for health care (1–5, higher = more willing)"}[oc]
        L += [f"## {title}", "", f"n = {r['n']} train participants (\"don't know\" and the attention-check failure excluded). "
              f"Distribution: {r['y_dist']}.", "",
              "| Model | Features | OOF MAE | OOF R² |", "|---|---|---|---|"]
        for m, p in r["perf"].items():
            L.append(f"| {m} | {LABELS[m]} | {p['mae']:.3f} | {p['r2']:+.3f} |")
        L += ["", "| Contrast (A vs B) | ΔR² (95% CI) | ΔMAE (95% CI) | Verdict | ΔR² range over 5 other fold seeds |",
              "|---|---|---|---|---|"]
        for c in r["comp"]:
            rb = r["robust"][c["contrast"]]
            L.append(f"| {c['contrast']} | {fmt_ci(c, 'r2')} | {fmt_ci(c, 'mae')} | {c['verdict']} | "
                     f"{rb['min']:+.3f} to {rb['max']:+.3f} |")
        L += ["", "Effect sizes (Spearman ρ with the outcome, train): " + "; ".join(
            f"{k} {v['spearman']:+.2f} (n = {v['n_nonmissing']})" for k, v in r["effect"].items()), ""]
    L += ["## Comparability check: binary outcome (government should help = points 1–2)", "",
          f"Prevalence {binr['prevalence']:.2f}. Logistic regression, C = 1.0, same folds.", "",
          "| Model | Brier | Log loss | AUC |", "|---|---|---|---|"]
    for m, p in binr["perf"].items():
        auc = "–" if m == "M0" else f"{p['auc']:.3f}"
        L.append(f"| {m} | {p['brier']:.4f} | {p['logloss']:.4f} | {auc} |")
    L += ["", "| Contrast | ΔBrier (95% CI) | ΔAUC (95% CI) |", "|---|---|---|"]
    for c in binr["comp"]:
        auc = "–" if "M0" in c["contrast"] else fmt_ci(c, "auc")
        L.append(f"| {c['contrast']} | {fmt_ci(c, 'brier', 4)} | {auc} |")
    g = green.set_index("contrast")
    L += ["", "## Side by side with the green-energy follow-up", "",
          "| | Green energy (hypothetical costed choice, randomised default) | Redistribution (stated attitude, no condition) |",
          "|---|---|---|",
          f"| n (train) | 428 | {res['govt_help']['n']} |",
          f"| Demographics vs baseline, ΔBrier | {g.loc['M1 vs M0', 'brier_diff']:+.4f} "
          f"({g.loc['M1 vs M0', 'brier_lo']:+.4f}, {g.loc['M1 vs M0', 'brier_hi']:+.4f}) | {fmt_ci(binr['comp'][0], 'brier', 4)} |",
          f"| Measured attitude added, ΔBrier | {g.loc['M2 vs M1', 'brier_diff']:+.4f} "
          f"({g.loc['M2 vs M1', 'brier_lo']:+.4f}, {g.loc['M2 vs M1', 'brier_hi']:+.4f}) | {fmt_ci(binr['comp'][1], 'brier', 4)} |",
          f"| Measured attitude added, ΔAUC | {g.loc['M2 vs M1', 'auc_diff']:+.3f} | {binr['comp'][1]['d_auc']:+.3f} |",
          "| Experimental context | default adds ~0.01 Brier (borderline) | not applicable: no condition |", ""]
    (OUT / "redistribution_vs_demographics.md").write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    res = {oc: run_outcome(oc, rng) for oc in OUTCOMES}
    prim = res["govt_help"]
    alpha = cronbach_alpha(load("govt_help").merge(
        pd.read_csv(RAW_TWIN / "question_catalog_and_human_response_csv/wave1_3_response.csv",
                    usecols=["pid", *CONSTRUCT_COLS["redist"]]), on="pid")[CONSTRUCT_COLS["redist"]])
    binr = run_binary(prim["df"], prim["fold"], rng)
    green = pd.read_csv(ROOT / "reports/exploratory/paired_differences.csv")
    write_report(res, binr, alpha, green)
    summary = {oc: {k: v for k, v in r.items() if k not in ("df", "fold")} for oc, r in res.items()}
    summary["binary_govt_help"] = binr
    summary["cronbach_alpha_redist_train"] = alpha
    json.dump(summary, open(OUT / "results.json", "w"), indent=1, default=float)
    print(json.dumps({oc: {"perf": r["perf"], "comp": [{k: (round(v, 4) if isinstance(v, float) else v)
                                                         for k, v in c.items()} for c in r["comp"]]}
                      for oc, r in summary.items() if oc in OUTCOMES}, indent=1, default=float))
    print("alpha", round(alpha, 3), "binary", json.dumps(binr, default=float)[:800])


if __name__ == "__main__":
    main()
