"""Tests for the exploratory values-vs-demographics experiment (src/exploratory_values.py)."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import exploratory_values as ev  # noqa: E402


@pytest.fixture(scope="module")
def data():
    df = ev.load_train()
    fold = ev.folds(df.chose_green.to_numpy())
    return df, fold, ev.oof_predictions(df, fold)


def test_train_only(data):
    df, _, _ = data
    assert (df.split == "train").all() and len(df) == 428


def test_same_participants_and_folds_across_models(data):
    df, fold, oof = data
    assert list(oof.pid) == list(df.pid)
    assert set(ev.MODELS) <= set(oof.columns) and oof[list(ev.MODELS)].notna().all().all()
    assert np.array_equal(oof.fold.to_numpy(), fold)
    assert np.array_equal(ev.folds(df.chose_green.to_numpy()), fold)  # deterministic
    assert len(set(fold)) == 5 and np.bincount(fold).min() >= 85


def test_no_leakage_from_held_out_fold(data):
    """Flipping fold-0 outcomes must leave every model's fold-0 predictions unchanged."""
    df, fold, oof = data
    df2 = df.copy()
    k0 = fold == 0
    df2.loc[k0, "chose_green"] = 1 - df2.loc[k0, "chose_green"]
    oof2 = ev.oof_predictions(df2, fold)
    for m in ev.MODELS:
        assert np.allclose(oof.loc[k0, m], oof2.loc[k0, m]), m


def test_scaler_fitted_within_fold(data):
    """Shifting GREEN for fold-0 rows only must not change fold-0 predictions of a model refit without them,
    i.e. fold-0 feature values do not enter the scaler used for fold 0."""
    df, fold, _ = data
    k0 = fold == 0
    X = df[ev.TIER_A].astype(str).join(df[["green", "green_default"]].astype(float))
    y = df.chose_green.to_numpy()
    m_a = ev.make_model(ev.MODELS["M3"]).fit(X[~k0], y[~k0])
    X2 = X.copy()
    X2.loc[k0, "green"] += 100.0
    m_b = ev.make_model(ev.MODELS["M3"]).fit(X2[~k0], y[~k0])
    assert np.allclose(m_a.predict_proba(X[k0]), m_b.predict_proba(X[k0]))


def test_metrics_and_bootstrap_sign(data):
    _, _, oof = data
    r = ev.paired_bootstrap(oof, "M3", "M3", np.random.default_rng(0))
    assert r["brier_diff"] == 0 and r["verdict"] == "no detectable difference"
    m = ev.metrics(oof.y.to_numpy(), oof.M0.to_numpy())
    assert 0 < m["brier"] < 0.26


def test_originals_untouched():
    protected = ["data/split.csv", "hypotheses.md", "results", "reports/personas", "reports/memo.md", "config"]
    from _committed import mismatches
    bad = mismatches(protected)  # numeric tolerance; CRLF-insensitive (see tests/_committed.py)
    assert not bad, f"protected files differ from the committed versions: {bad}"
