"""Integrity tests. Run after the pipeline: `python -m pytest -q tests`."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from common import TIER_A, load_green, load_people  # noqa: E402
from personas import CriteriaError, build, mask, parse_criteria  # noqa: E402

SPLIT_SHA = "8ef47da04a8d814d9a874a63310be9043f9c9f937e74679c15073bebfa5dbe5f"


@pytest.fixture(scope="module")
def people():
    return load_people()


def test_split_frozen():
    assert hashlib.sha256((ROOT / "data/split.csv").read_bytes()).hexdigest() == SPLIT_SHA


def test_split_sizes_and_disjoint(people):
    s = pd.read_csv(ROOT / "data/split.csv")
    assert s.pid.is_unique and len(s) == 2058
    assert (s.split == "train").sum() == 1442 and (s.split == "test").sum() == 616


def test_spendthrift_rescore_range_and_direction(people):
    assert people.spendthrift.between(4, 26).all()
    raw = pd.read_csv(ROOT / "data/raw/Twin-2K-500/question_catalog_and_human_response_csv/wave1_3_response.csv",
                      usecols=["pid", "QID31"]).merge(people[["pid", "spendthrift"]], on="pid")
    assert raw.QID31.corr(raw.spendthrift) > 0.5  # QID31: 1 = tightwad ... 11 = spendthrift


def test_green_coding():
    g = load_green()
    assert len(g) == 600 and g.pid.is_unique
    assert set(g.green_condition) == {"green_default", "grey_default"}
    assert g.chose_green.isin([0, 1]).all()


def test_whitelist_rejects_party_and_unknown(people):
    with pytest.raises(CriteriaError):
        parse_criteria("party=Republican", people)
    with pytest.raises(CriteriaError):
        parse_criteria("ideology=Liberal", people)
    with pytest.raises(CriteriaError):
        parse_criteria("age_band=70+", people)
    assert parse_criteria("party=Republican", people, allow_party=True) == {"party": ["Republican"]}


MIDWEST = "Midwest (ND, SD, NE, KS, MN, IA, MO, WI, IL, MI, IN, OH)"


def test_repeated_variable_contradiction_is_rejected(people):
    # regression: the last clause used to overwrite the first, silently profiling a different group
    with pytest.raises(CriteriaError, match="contradictory"):
        parse_criteria("sex=Male; sex=Female", people)
    with pytest.raises(CriteriaError, match="contradictory"):
        parse_criteria("age_band=18-29|30-49; age_band=65+", people)


def test_repeated_variable_consistent_is_intersected(people):
    assert parse_criteria("sex=Female; sex=Female", people) == {"sex": ["Female"]}
    crit = parse_criteria(f"age_band=18-29|30-49; region={MIDWEST}; age_band=30-49|50-64", people)
    assert crit == {"age_band": ["30-49"], "region": [MIDWEST]}
    assert parse_criteria("age_band=65+|65+", people) == {"age_band": ["65+"]}


def test_impossible_group_abstains_cleanly(people):
    crit = parse_criteria("age_band=18-29; employment=Retired; marital=Widowed", people)
    rep = build("impossible", crit, people, load_green())
    assert rep["n_train"] < 30 and rep["status"].startswith("INSUFFICIENT EVIDENCE")


def test_cli_rejects_duplicate_criteria_and_unsafe_names(tmp_path):
    import personas
    assert personas.main(["build", "--name", "x", "--criteria", "sex=Male; sex=Female", "--out", str(tmp_path)]) == 2
    assert personas.main(["build", "--name", "../escape", "--criteria", "sex=Male", "--out", str(tmp_path)]) == 2
    assert personas.main(["build", "--name", "a/b", "--criteria", "sex=Male", "--out", str(tmp_path)]) == 2
    assert not any(tmp_path.iterdir())


RANK = {"not distinguishable from population": 0, "weak difference": 1, "distinct": 2}
GROUPS = ["age_band=65+", "age_band=65+; income=Less than $30,000", "age_band=18-29; income=$100,000 or more",
          "sex=Female", "education=Associate's degree", "employment=Student", "marital=Widowed",
          "age_band=18-29; marital=Never been married", "region=Pacific (HI, AK)"]


@pytest.fixture(scope="module")
def corrected():
    return load_people(corrected=True), load_green(corrected=True)


def test_shrinkage_label_never_stronger_and_preregistered_label_unchanged(corrected):
    people, green = corrected
    for g in GROUPS:
        rep = build("t", parse_criteria(g, people), people, green)
        for r in rep.get("inner", []):
            raw_distinct = abs(r["d"]) >= 0.20 and (r["d_lo"] > 0 or r["d_hi"] < 0)
            assert (r["confidence"] == "distinct") == raw_distinct                      # pre-registered rule intact
            assert RANK[r["confidence_shrinkage_adjusted"]] <= RANK[r["confidence"]], (g, r["construct"])
            assert r["shrunk_ci_lo"] <= r["typical_shrunk"] <= r["shrunk_ci_hi"]
            if r["confidence_shrinkage_adjusted"] == "distinct":                          # adjusted label is coherent
                assert abs(r["shrunk_d"]) >= 0.20 and not (r["shrunk_ci_lo"] <= r["pop_mean"] <= r["shrunk_ci_hi"])


def test_small_group_crt_label_flagged_after_shrinkage(corrected):
    # stress-test case: 65+ with income < $30k, CRT raw-distinct but Typical falls outside its raw CI after shrinkage
    from personas import confidence_text
    people, green = corrected
    rep = build("t", parse_criteria("age_band=65+; income=Less than $30,000", people), people, green)
    crt = next(r for r in rep["inner"] if r["construct"] == "crt")
    if crt["confidence"] == "distinct":
        assert crt["confidence_shrinkage_adjusted"] != "distinct"
        assert "after shrinkage" in confidence_text(crt)


def test_median_side_shares_handle_ties(corrected):
    people, green = corrected
    rep = build("t", parse_criteria("age_band=65+; income=Less than $30,000", people), people, green)
    tr = people[people.split == "train"]
    for r in rep["inner"]:
        if r["share_opposite_side_of_pop_median"] != r["share_opposite_side_of_pop_median"]:   # NaN when d == 0
            continue
        x = people[(people.split == "train") & mask(people, parse_criteria("age_band=65+; income=Less than $30,000", people))][r["construct"]]
        med, side = tr[r["construct"]].median(), np.sign(r["raw_mean"] - r["pop_mean"])
        same = float(((x - med) * side > 0).mean())
        assert r["share_opposite_side_of_pop_median"] + r["share_at_pop_median"] + same == pytest.approx(1.0)
    dg = next(r for r in rep["inner"] if r["construct"] == "dictator_give")
    assert dg["share_at_pop_median"] > 0.3                                                # ties are real and now visible


def test_behaviour_floor_is_20_for_choice_and_say_do(corrected):
    from personas import MIN_N_BEHAVIOUR
    assert MIN_N_BEHAVIOUR == 20
    people, green = corrected
    for g in GROUPS:
        rep = build("t", parse_criteria(g, people), people, green)
        for b in rep.get("green_choice", []):
            assert (b["status"] == "ok") == (b["n"] >= 20)
        for s in rep.get("say_do_gap", []):
            assert (s["status"] == "ok") == (s["n_high_green"] >= 20), (g, s)


def test_tier_a_has_no_inner_layer():
    assert not {"party", "ideology", "religion", "religious_attendance"} & set(TIER_A)


def test_insufficient_evidence(people):
    rep = build("tiny", parse_criteria("age_band=18-29; employment=Retired", people), people, load_green())
    assert rep["status"].startswith("INSUFFICIENT EVIDENCE")


def test_persona_built_from_train_only(people):
    crit = parse_criteria("age_band=65+", people)
    rep = build("p", crit, people, load_green())
    tr = people[(people.split == "train") & mask(people, crit)]
    neu = next(r for r in rep["inner"] if r["construct"] == "neuroticism")
    assert rep["n_train"] == len(tr)
    assert neu["raw_mean"] == pytest.approx(tr.neuroticism.mean())


def test_holdout_first_run_recorded():
    f = ROOT / "results/holdout_first_run.json"
    assert f.exists() and json.load(open(f))["git_commit"]
