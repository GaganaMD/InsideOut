"""Checks for the open-weight benchmark design (no network). Run: python -m pytest -q test_f2.py"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_prompts as bp  # noqa: E402

P = [json.loads(l) for l in (HERE / "prompts.jsonl").read_text(encoding="utf-8").splitlines()]


def test_answer_order_maps_letters_to_the_same_choice():
    for p in P:
        u = p["messages"][1]["content"]
        a_green = f"A: {bp.OPT['green']}" in u and f"B: {bp.OPT['grey']}" in u
        b_green = f"A: {bp.OPT['grey']}" in u and f"B: {bp.OPT['green']}" in u
        assert (p["order"] == "AB" and a_green and not b_green) or (p["order"] == "BA" and b_green and not a_green), p["id"]
    # analysis maps p_green to the letter of the green option in that order
    src = (HERE / "analyze.py").read_text(encoding="utf-8")
    assert 'pg = (r["pA"] if m["order"] == "AB" else r["pB"]) / r["mass"]' in src


def test_every_cell_condition_has_both_orders_and_identical_content_otherwise():
    by = {}
    for p in P:
        by.setdefault((p["fmt"], p["cond"], p["cell"], p["fold"]), []).append(p)
    for k, v in by.items():
        assert sorted(x["order"] for x in v) == ["AB", "BA"], k
        strip = lambda s: s.split("Question:")[0]
        assert strip(v[0]["messages"][1]["content"]) == strip(v[1]["messages"][1]["content"]), k


def test_profiles_are_out_of_sample_for_evaluated_fold():
    from common import load_people
    people = load_people(corrected=True)
    train = people[people.split == "train"]
    folds = pd.read_csv(HERE / "folds_local.csv").set_index("pid").fold
    prof = pd.read_csv(HERE / "profiles.csv")
    cells = sorted(prof.cell.unique())
    # recompute fold-0 profiles after CHANGING fold-0 people's scores: must not move (they are not used for fold 0)
    tampered = train.copy()
    f0 = folds.loc[tampered.pid].to_numpy() == 0
    for c in bp.CONSTRUCTS:
        tampered.loc[f0, c] = tampered.loc[f0, c].to_numpy()[::-1]
    re = bp.estimate_profiles(tampered, folds, cells)
    a = prof[prof.fold == 0].set_index("cell")[list(bp.CONSTRUCTS)].sort_index()
    b = re[re.fold == 0].set_index("cell")[list(bp.CONSTRUCTS)].sort_index()
    assert np.allclose(a.to_numpy(), b.to_numpy())                     # fold-0 profiles ignore fold-0 people
    a1 = prof[prof.fold == 1].set_index("cell")[list(bp.CONSTRUCTS)].sort_index()
    b1 = re[re.fold == 1].set_index("cell")[list(bp.CONSTRUCTS)].sort_index()
    assert not np.allclose(a1.to_numpy(), b1.to_numpy())               # ...but fold-1 profiles do use them


def test_profile_and_narrative_carry_identical_numbers():
    import re
    by = {(p["fmt"], p["cond"], p["order"], p["cell"], p["fold"]): p for p in P}
    for (fmt, cond, order, cell, fold), p in by.items():
        if fmt != "profile":
            continue
        n = by[("narrative", cond, order, cell, fold)]
        nums = lambda s: sorted(re.findall(r"[+-]\d\.\d\d", s))
        assert nums(p["messages"][1]["content"]) == nums(n["messages"][1]["content"])


def test_no_outcomes_or_ids_in_prompts():
    blob = json.dumps([p["messages"] for p in P]).lower()
    for w in ("pid", "twin", "chose", "y_human", "split"):
        assert w not in blob
