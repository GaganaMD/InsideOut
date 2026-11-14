"""Tests for the exploratory robustness analyses (src/robust_demographics.py, src/robust_personas.py)."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import exploratory_values as ev  # noqa: E402
import robust_demographics as rd  # noqa: E402
import robust_personas as rp  # noqa: E402
from common import load_people  # noqa: E402
from personas import load_config, parse_criteria  # noqa: E402


@pytest.fixture(scope="module")
def green_oof():
    df, y, fold = rd.datasets()["green"]
    return df, y, fold, rd.oof(df, y, fold)


def test_same_participants_and_folds_as_followup(green_oof):
    df, y, fold, o = green_oof
    assert np.array_equal(fold, ev.folds(ev.load_train().chose_green.to_numpy()))
    assert list(o.pid) == list(ev.load_train().pid) and (df.split == "train").all()
    assert o[list(rd.MODELS)].notna().all().all()


def test_no_leakage_demographic_models(green_oof):
    df, y, fold, o = green_oof
    y2 = y.copy()
    k0 = fold == 0
    y2[k0] = 1 - y2[k0]
    o2 = rd.oof(df, y2, fold)
    for m in rd.MODELS:
        assert np.allclose(o.loc[k0, m], o2.loc[k0, m]), m


def _diff(a: dict, b: dict) -> int:
    keys = set(a) | set(b)
    return sum(a.get(k) != b.get(k) for k in keys)


def test_each_variant_changes_exactly_one_criterion():
    people = load_people()
    cfg = load_config()
    for key, variants in rp.VARIANTS.items():
        base = parse_criteria(cfg[key]["criteria"], people)
        for label, crit in variants:
            assert _diff(base, parse_criteria(crit, people)) == 1, (key, label)


def test_stability_uses_train_only():
    df, _ = rp.run()
    people = load_people()
    tr = people[people.split == "train"]
    row = df[(df.persona == "P1") & (df.variant == "widen age: 50+")].iloc[0]
    assert row.n_train == int(tr.age_band.isin(["50-64", "65+"]).sum())


def test_cli_with_new_criteria():
    res = rp.cli_checks()
    assert all(r["passed"] for r in res), [r for r in res if not r["passed"]]


def test_originals_untouched():
    protected = ["data/split.csv", "hypotheses.md", "results", "reports/personas", "config",
                 "reports/exploratory/values_vs_demographics.md", "reports/exploratory/paired_differences.csv",
                 "reports/exploratory/redistribution/PRESPEC.md", "reports/exploratory/redistribution/results.json"]
    from _committed import mismatches
    bad = mismatches(protected)  # numeric tolerance; CRLF-insensitive (see tests/_committed.py)
    assert not bad, f"protected files differ from the committed versions: {bad}"
