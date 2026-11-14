"""EXPLORATORY: published GPT-4.1 digital-twin predictions (Peng et al., arXiv:2509.19088) vs our statistical models
on the hypothetical green-energy choice (Mega-Study `default_eric`). TRAINING PARTICIPANTS ONLY.

Source: https://github.com/TianyiPeng/Twin-2K-500-Mega-Study (Apache-2.0), results/default_eric/<spec>/
  consolidated_llm_values.csv.gz              LLM-simulated answers (Qualtrics layout, one row per participant)
  consolidated_original_answers_values.csv.gz human answers (used only to check alignment with our data)
Files are downloaded to research_frontier/experiments/external/ (git-ignored). Matching uses the dataset's own
anonymous TWIN_ID. Held-out (test-split) participants are dropped BEFORE any outcome is compared.

    python research_frontier/experiments/llm_benchmark.py
"""
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import exploratory_values as ev  # noqa: E402
import run_experiments as rx  # noqa: E402
from common import SEED  # noqa: E402

EXT = Path(__file__).resolve().parent / "external"
OUT = Path(__file__).resolve().parent / "results"
BASE = "https://raw.githubusercontent.com/TianyiPeng/Twin-2K-500-Mega-Study/main/results/default_eric"
SPECS = {"LLM demographics-only (T=0.7)": "demographics_only_2025-07-31",
         "LLM demographics-only (T=0)": "demographics_only_temperature_zero_2025-08-18",
         "LLM empty persona (T=0.7)": "empty_persona_2025-07-22",
         "LLM full persona (no reasoning)": "full_persona_without_reasoning_2025-06-18"}
FILES = ["consolidated_llm_values.csv.gz", "consolidated_original_answers_values.csv.gz"]


def fetch() -> None:
    EXT.mkdir(parents=True, exist_ok=True)
    for spec in SPECS.values():
        for f in FILES:
            dst = EXT / f"{spec}__{f}"
            if not dst.exists():
                urllib.request.urlretrieve(f"{BASE}/{spec}/{f}", dst)


def chose_green(df: pd.DataFrame) -> pd.DataFrame:
    """Same coding as src/audit.py: OPTOUT 1 = stay GreenGrid; OPTIN 2 = switch to GreenGrid."""
    d = df.copy()
    d = d[pd.to_numeric(d["TWIN_ID"], errors="coerce").notna()]
    oo, oi = pd.to_numeric(d.OPTOUT_Green, errors="coerce"), pd.to_numeric(d.OPTIN_Green, errors="coerce")
    return pd.DataFrame({"pid": pd.to_numeric(d.TWIN_ID).astype(int),
                         "cond": np.where(oo.notna(), "green_default", np.where(oi.notna(), "grey_default", "missing")),
                         "y": np.where(oo.notna(), (oo == 1).astype(float), np.where(oi.notna(), (oi == 2).astype(float), np.nan))})


def metrics(y, p) -> dict:
    yhat = (p >= 0.5).astype(int)
    tpr = (yhat[y == 1] == 1).mean()
    tnr = (yhat[y == 0] == 0).mean()
    return dict(accuracy=float((yhat == y).mean()), balanced_accuracy=float((tpr + tnr) / 2),
                corr_with_choice=float(np.corrcoef(y, p)[0, 1]) if np.std(p) > 0 else np.nan,
                brier=float(np.mean((y - p) ** 2)), predicted_green_rate=float(p.mean()), sd_prediction=float(np.std(p)))


def main() -> None:
    fetch()
    train = ev.load_train()                                   # our training participants (n = 428), split asserted
    assert (train.split == "train").all()
    ours = train[["pid", "chose_green", "green_condition"]].rename(columns={"chose_green": "y_ours", "green_condition": "cond_ours"})
    preds = {}
    for name, spec in SPECS.items():
        llm = chose_green(pd.read_csv(EXT / f"{spec}__{FILES[0]}", low_memory=False))
        hum = chose_green(pd.read_csv(EXT / f"{spec}__{FILES[1]}", low_memory=False))
        m = ours.merge(llm.rename(columns={"y": "y_llm", "cond": "cond_llm"}), on="pid", how="left") \
                .merge(hum.rename(columns={"y": "y_hum", "cond": "cond_hum"}), on="pid", how="left")
        # alignment checks: their human answers and conditions must equal ours for every training participant
        assert m.y_hum.notna().all() and (m.y_hum == m.y_ours).all() and (m.cond_hum == m.cond_ours).all(), name
        assert (m.cond_llm == m.cond_ours).all(), name
        preds[name] = m.set_index("pid").loc[train.pid, "y_llm"].to_numpy(dtype=float)
    y = train.chose_green.to_numpy()
    assert not any(np.isnan(v).any() for v in preds.values())

    # our models: out-of-fold predictions on the same participants (training-only, already computed or recomputed)
    prior = pd.read_csv(ROOT / "reports/exploratory/oof_predictions.csv").set_index("pid").loc[train.pid]
    df = rx.train_green()
    fold = ev.folds(df.chose_green.to_numpy())
    assert (df.pid.to_numpy() == train.pid.to_numpy()).all()
    stats = {"Prevalence": prior.M0.to_numpy(), "Default only (logistic)": rx.oof(df, fold, ["green_default"]),
             "Demographics + default (M1D)": prior.M1D.to_numpy(),
             "Green values + default (no demographics)": rx.oof(df, fold, ["green", "green_default"]),
             "Demographics + green values + default (M3)": prior.M3.to_numpy()}
    rows = [dict(model=k, kind="LLM hard 0/1 (published)", **metrics(y, v)) for k, v in preds.items()]
    rows += [dict(model=k, kind="statistical probability (OOF)", **metrics(y, v)) for k, v in stats.items()]
    res = pd.DataFrame(rows)
    res["true_green_rate"] = y.mean()

    # paired bootstrap: accuracy difference, demographics-only LLM (T=0) vs our models
    rng = np.random.default_rng(SEED)
    a = (preds["LLM demographics-only (T=0)"] >= 0.5).astype(int) == y
    comp = []
    for k, v in stats.items():
        b = ((v >= 0.5).astype(int) == y)
        diffs = [np.mean(a[i]) - np.mean(b[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(2000))]
        comp.append(dict(contrast=f"LLM demographics-only (T=0) minus {k}", accuracy_diff=float(a.mean() - b.mean()),
                         lo=float(np.quantile(diffs, .025)), hi=float(np.quantile(diffs, .975))))
    comp = pd.DataFrame(comp)
    # group recovery: choice rate by default arm
    grp = pd.DataFrame({"cond": train.green_condition.to_numpy(), "human": y,
                        **{k: (v >= 0.5).astype(int) for k, v in {**preds, "Green values + default (no demographics)":
                                                                   stats["Green values + default (no demographics)"]}.items()}})
    grp = grp.groupby("cond").mean().T
    OUT.mkdir(parents=True, exist_ok=True)
    res.round(4).to_csv(OUT / "llm_benchmark_metrics.csv", index=False)
    comp.round(4).to_csv(OUT / "llm_benchmark_paired_accuracy.csv", index=False)
    grp.round(3).to_csv(OUT / "llm_benchmark_group_rates.csv")
    pd.set_option("display.width", 220)
    print(f"n training participants = {len(y)}")
    print(res.round(3).to_string(index=False)); print(comp.round(3).to_string(index=False)); print(grp.round(3).to_string())


if __name__ == "__main__":
    main()
