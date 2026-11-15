"""Tasks for the matched GPT-4.1 'green_profiles' experiment (pre-registered in
research_frontier/brace_challenge_lab/F3_gpt41/PREREGISTRATION.md).

Re-uses the FROZEN design of the open-weight benchmark (F2_modal_open_weight): the same 76 k-anonymous cells, the same
cross-fitted ridge profiles (profiles.csv, fit on the other training fold), and the same numeric / narrative renderers,
so the numeric and narrative formats carry identical numbers. Output elicitation is the harness's validated JSON
{"choice", "p"} with p = probability of option A; both answer orders are scored and averaged downstream.
Nothing outcome-related or individual-level is in any task.
"""
import sys
from pathlib import Path

import pandas as pd

from .runner import Task
from .tasks import ITEM_BASE, LABELS, SCENARIOS, CELL_FIELDS

F2 = Path(__file__).resolve().parents[2] / "brace_challenge_lab/F2_modal_open_weight"
OPT = {"green": "GreenGrid: renewable electricity, $39 per month", "grey": "Twon: standard electricity, $32 per month"}
FORMATS = ("empty", "demo", "profile", "narrative")
ARM = {"empty": "empty", "demo": "tierA", "profile": "tierA_profile", "narrative": "narrative"}
PILOT_CELLS, REPEATS_PILOT, REPEATS_FULL = 12, 20, 32


def _renderers():
    sys.path.insert(0, str(F2))
    import build_prompts as bp   # frozen F2 renderers (profile_block, narrative_block)
    return bp


def item(cond: str, order: str) -> dict:
    a, b = ("green", "grey") if order == "AB" else ("grey", "green")
    return {"question": ITEM_BASE["question"], "options": {"A": OPT[a], "B": OPT[b]}, "focal": "A",
            "scenario": SCENARIOS[cond], "scenario_neutral": SCENARIOS["neutral"]}


def build(pilot: bool) -> list[Task]:
    bp = _renderers()
    prof = pd.read_csv(F2 / "profiles.csv")
    cells = sorted(prof.cell.unique())
    if pilot:                                   # pre-registered: the 12 cells with most default_eric training members
        cells = _largest_cells(bp, PILOT_CELLS)
    out = []
    for cond in ("green_default", "grey_default"):
        for order in ("AB", "BA"):
            it = item(cond, order)
            out.append(Task(f"empty|{cond}|{order}|ALL|-|s0", "empty", {}, it))
            for c in cells:
                tier_a = dict(zip([LABELS[f] for f in CELL_FIELDS], c.split(" | ")))
                out.append(Task(f"demo|{cond}|{order}|{c}|-|s0", "tierA", {"tier_a": tier_a}, it))
                for f in (0, 1):
                    p = prof[(prof.cell == c) & (prof.fold == f)].iloc[0]
                    out.append(Task(f"profile|{cond}|{order}|{c}|{f}|s0", "tierA_profile",
                                    {"tier_a": tier_a, "text_block": bp.profile_block(p)}, it))
                    out.append(Task(f"narrative|{cond}|{order}|{c}|{f}|s0", "narrative",
                                    {"text_block": bp.narrative_block(c, p)}, it))
    reps = REPEATS_PILOT if pilot else REPEATS_FULL               # identical re-asks for consistency (sample=1)
    step = max(1, len(out) // reps)
    for t in out[::step][:reps]:
        out.append(Task(t.task_id[:-3] + "|s1", t.arm, t.profile, t.item, sample=1))
    return out


def _largest_cells(bp, k: int) -> list[str]:
    from common import load_green
    g = load_green(corrected=True)
    g = g[g.split == "train"]
    s = bp.cell_of(g).value_counts()
    prof_cells = set(pd.read_csv(F2 / "profiles.csv").cell)
    s = s[s.index.isin(prof_cells)]
    return sorted(s.index, key=lambda c: (-s[c], c))[:k]
