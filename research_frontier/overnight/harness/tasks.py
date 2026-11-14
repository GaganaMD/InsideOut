"""Build privacy-preserving, cell-level tasks for default_eric (TRAINING participants only).

Prompts never contain a participant ID, a participant's outcome or any free text. Profiles are demographic CELLS that
occur at least `k_min` times in the full public panel (k-anonymity); answers are mapped back to participants locally.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from .runner import Task  # noqa: E402

# Generalised Tier A used for the cell-level arm (coarsened so that cells are k-anonymous)
EDU3 = {"Less than high school": "no college degree", "High school graduate": "no college degree",
        "Some college, no degree": "no college degree", "Associate's degree": "no college degree",
        "College graduate/some postgrad": "college degree", "Postgraduate": "college degree"}
CELL_FIELDS = ["age_band", "sex", "income", "edu3"]
LABELS = {"age_band": "age", "sex": "sex", "income": "household income", "edu3": "education"}

# Scenario text: condition-specific versions are the survey's own wording (from the QSF item text);
# the neutral version is CONSTRUCTED for the condition-blind arm and is documented as such.
ITEM_BASE = {"question": "Which electricity supplier do you choose?",
             "options": {"A": "GreenGrid: renewable electricity, $39 per month", "B": "Twon: standard electricity, $32 per month"},
             "focal": "A"}
SCENARIOS = {
    "green_default": ("Imagine you have to relocate to another town. After you move into your new flat, you receive a letter "
                      "from the electric power supplier, GreenGrid. You are told that by moving into your new flat you became a "
                      "GreenGrid customer. GreenGrid sells clean electricity, generated from renewable energy sources. Your "
                      "monthly premium is $39. Some weeks later you find a flyer from the electric power supplier Twon: you can "
                      "easily switch, and Twon's low-priced tariff costs $32 per month."),
    "grey_default": ("Imagine you have to relocate to another town. After you move into your new flat, you receive a letter "
                     "from the electric power supplier, Twon. You are told that by moving into your new flat you became a Twon "
                     "customer. Twon offers low-priced electricity tariffs. Your monthly premium is $32. Some weeks later you "
                     "find a flyer from the electric power supplier GreenGrid: you can easily switch, and GreenGrid's clean, "
                     "renewable electricity costs $39 per month."),
    "neutral": ("Imagine you have to relocate to another town and must choose an electricity supplier for your new flat. "
                "GreenGrid sells clean electricity from renewable sources for $39 per month. Twon offers low-priced "
                "electricity for $32 per month."),
}


def cells(people: pd.DataFrame) -> pd.Series:
    p = people.assign(edu3=people.education.astype(str).map(EDU3))
    return p[CELL_FIELDS].astype(str).agg(" | ".join, axis=1)


def build(k_min: int = 5, samples: int = 1, arms=("empty", "tierA", "tierA_condition_blind")):
    from common import load_green, load_people
    panel = load_people()                                   # full public panel, for k-anonymity counts only
    k_counts = cells(panel).value_counts()
    g = load_green()
    g = g[g.split == "train"].copy()                        # training participants only
    assert (g.split == "train").all()
    g["cell"] = cells(g)
    g["k"] = g.cell.map(k_counts)
    tasks, mapping = [], []
    for arm in arms:
        for cond in ("green_default", "grey_default"):
            sub = g[g.green_condition == cond]
            scen = SCENARIOS["neutral" if arm == "tierA_condition_blind" else cond]
            item = {**ITEM_BASE, "scenario": scen, "scenario_neutral": SCENARIOS["neutral"]}
            groups = [("ALL", sub)] if arm == "empty" else list(sub.groupby("cell"))
            for cell, members in groups:
                if arm != "empty" and k_counts[cell] < k_min:
                    continue                                 # not k-anonymous: never sent; members fall back to 'empty'
                prof = {} if arm == "empty" else {"tier_a": dict(zip([LABELS[f] for f in CELL_FIELDS], cell.split(" | ")))}
                for s in range(samples):
                    tid = f"{arm}/{cond}/{cell}/s{s}"
                    tasks.append(Task(task_id=tid, arm=arm, profile=prof, item=item, sample=s))
                mapping += [(int(pid), arm, cond, cell) for pid in members.pid]
    assert all("pid" not in str(t.profile).lower() for t in tasks)
    return tasks, pd.DataFrame(mapping, columns=["pid", "arm", "cond", "cell"]), g[["pid", "cell", "k"]]


PILOT = {"n_cells": 10, "cell_samples": 3, "empty_samples": 10}   # 2x10 empty + 10 cells x 2 cond x 3 = 80 calls


def pilot_cells(g: pd.DataFrame, n_cells: int, k_min: int = 5) -> list[str]:
    """Largest training cells present in BOTH default conditions (deterministic: size desc, then name)."""
    both = g.groupby("cell").green_condition.nunique()
    sizes = g.groupby("cell").size()
    ok = [c for c in sizes.index if both[c] == 2 and g.loc[g.cell == c, "k"].iloc[0] >= k_min]
    return sorted(ok, key=lambda c: (-sizes[c], c))[:n_cells]


def build_pilot(n_cells: int = PILOT["n_cells"], cell_samples: int = PILOT["cell_samples"],
                empty_samples: int = PILOT["empty_samples"]):
    """Subset of the full design (same task keys, so pilot results are re-usable by a later full run)."""
    tasks, mapping, g = build(samples=max(cell_samples, empty_samples), arms=("empty", "tierA"))
    from common import load_green
    gg = load_green()
    gg = gg[gg.split == "train"].copy()
    gg["cell"], gg["k"] = cells(gg), g.set_index("pid").loc[gg.pid, "k"].to_numpy()
    keep_cells = set(pilot_cells(gg, n_cells))
    out = [t for t in tasks if (t.arm == "empty" and t.sample < empty_samples)
           or (t.arm == "tierA" and t.sample < cell_samples and t.task_id.split("/")[2] in keep_cells)]
    return out, sorted(keep_cells)
