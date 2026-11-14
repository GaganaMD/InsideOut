"""Final-audit tests: scale re-derivation, shipped-bug reproduction, default path unchanged."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import final_audit as fa  # noqa: E402
from common import load_people  # noqa: E402


@pytest.fixture(scope="module")
def sv():
    return fa.scale_verification().set_index("construct")


def test_verified_scales_match_items_exactly(sv):
    for c in ["green", "neuroticism", "dictator_give"]:
        assert sv.loc[c, "exact_match"] == 1.0, c


def test_shipped_bugs_are_reproduced(sv):
    assert sv.loc["spendthrift", "bug_rule_exact_match"] == 1.0
    assert sv.loc["crt", "bug_rule_exact_match"] == 1.0
    assert sv.loc["social_desirability", "bug_rule_exact_match"] > 0.996  # 7 late pids scored 0 in shipped file


def test_default_path_is_the_frozen_original():
    p = load_people()
    s = pd.read_parquet(ROOT / "data/processed/scores.parquet").set_index("pid").loc[p.pid]
    assert np.allclose(p.social_desirability, s.w2_score_socialdesirability)
    assert np.allclose(p.crt, s.w1_crt2_score)


def test_corrected_path_changes_only_sd_and_crt():
    a, b = load_people(False), load_people(True)
    for c in ["green", "spendthrift", "dictator_give", "neuroticism"]:
        assert np.allclose(a[c], b[c])
    assert (a.social_desirability != b.social_desirability).sum() == 180
    assert (a.crt != b.crt).sum() == 450
    assert b.social_desirability.between(0, 13).all() and b.crt.between(0, 4).all()
