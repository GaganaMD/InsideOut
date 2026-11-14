"""Tests for the exploratory redistribution follow-up (src/exploratory_redistribution.py)."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import exploratory_redistribution as er  # noqa: E402


@pytest.fixture(scope="module")
def data():
    df = er.load("govt_help")
    fold = er.folds(df.y.to_numpy())
    return df, fold, er.oof(df, fold)


def test_item_mapping_verified():
    er.verify_items()  # raises if catalog wording/order differs from the pre-specification


def test_train_only_no_holdout_participants(data):
    df, _, _ = data
    split = pd.read_csv(ROOT / "data/split.csv")
    test_pids = set(split.pid[split.split == "test"])
    assert (df.split == "train").all() and not (set(df.pid) & test_pids)


def test_outcome_coding_and_exclusions(data):
    df, _, _ = data
    assert df.y.between(1, 5).all() and df.pid.is_unique
    raw = pd.read_parquet(ROOT / "data/processed/mega_preference_redistribution.parquet")
    m = raw.merge(df[["pid", "y"]], on="pid")
    assert (m.y == 6 - m.GOVT_RESPONSIBILITY).all()  # higher = more government responsibility
    assert (m.ATTENTION_CHECK == 3).all()


def test_predictors_exclude_outcome_survey_and_party():
    cols = set(er.TIER_A) | set(er.CONSTRUCT_COLS) | set(sum(er.CONSTRUCT_COLS.values(), []))
    forbidden = {"party", "PRES20_GSS", "VOTE20_GSS", "GOVT_RESPONSIBILITY", "HLTHTAX", "GETAHEAD", "FAIR"}
    assert not cols & forbidden


def test_same_participants_and_folds(data):
    df, fold, o = data
    assert list(o.pid) == list(df.pid) and np.array_equal(o.fold.to_numpy(), fold)
    assert o[list(er.MODELS)].notna().all().all() and len(set(fold)) == 5


def test_no_participant_level_leakage(data):
    """Changing held-out participants' outcomes must not change their own out-of-fold predictions."""
    df, fold, o = data
    df2 = df.copy()
    k0 = fold == 0
    df2.loc[k0, "y"] = 6 - df2.loc[k0, "y"]
    o2 = er.oof(df2, fold)
    for m in er.MODELS:
        assert np.allclose(o.loc[k0, m], o2.loc[k0, m]), m


def test_reproducible(data):
    df, fold, o = data
    assert np.array_equal(er.folds(df.y.to_numpy()), fold)
    pd.testing.assert_frame_equal(o, er.oof(df, fold))


def test_originals_untouched():
    protected = ["data/split.csv", "hypotheses.md", "results", "reports/personas", "reports/memo.md", "config",
                 "reports/exploratory/values_vs_demographics.md", "reports/exploratory/paired_differences.csv",
                 "reports/exploratory/redistribution/PRESPEC.md"]
    r = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *protected], cwd=ROOT)
    assert r.returncode == 0, "protected files differ from the committed versions"
