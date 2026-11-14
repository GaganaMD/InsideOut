"""LOCAL. Build the pre-registered prompt set for the open-weight persona benchmark (no outcomes in any prompt).

Unit: demographic CELL = age_band x sex x income x edu3 (k >= 5 in the full 2,058 panel), default_eric scenario text
(public), both randomised default conditions, both answer orders (position-bias control).
Formats:  empty (no persona) | demo (cell fields only) | profile (cell fields + statistically estimated inner-layer
          profile as numbers) | narrative (cell fields + the SAME six numbers inside a verbal persona sketch).
Cross-fitting: all 1,442 TRAINING participants are split into 2 folds (seed 20261114). The profile used to predict
participants in fold f is a ridge regression (alpha fixed = 10, one-hot cell fields) of each corrected construct fit on
fold 1-f, standardised by fold 1-f mean/SD. No test-split participant is read.
Output: prompts.jsonl (id, model-facing messages, metadata) and profiles.csv (cell, fold, six estimated z-scores).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "research_frontier/overnight")]
from common import CONSTRUCTS, load_green, load_people  # noqa: E402
from harness.tasks import CELL_FIELDS, EDU3, LABELS, SCENARIOS  # noqa: E402

SEED = 20261114
ALPHA = 10.0
SYSTEM = ("You simulate how a person with the described characteristics would answer a survey question. "
          "Answer as that person would, not as an expert.")
QUESTION = "Which electricity supplier do you choose?"
OPT = {"green": "GreenGrid: renewable electricity, $39 per month", "grey": "Twon: standard electricity, $32 per month"}
NAMES = {"neuroticism": "neuroticism (emotional instability)", "social_desirability": "social desirability (concern with presenting oneself favourably)",
         "spendthrift": "spendthrift tendency (vs. tightwad)", "green": "green values (environmental concern)",
         "crt": "cognitive reflection (careful vs. intuitive reasoning)", "dictator_give": "generosity toward strangers"}
VERBAL = {"neuroticism": ("more anxious and emotionally reactive", "calmer and more emotionally stable"),
          "social_desirability": ("more concerned with presenting themselves favourably", "less concerned with presenting themselves favourably"),
          "spendthrift": ("more inclined to spend freely", "more frugal"),
          "green": ("more concerned about the environment", "less concerned about the environment"),
          "crt": ("more reflective when solving problems", "more intuitive when solving problems"),
          "dictator_give": ("more generous toward strangers", "less generous toward strangers")}


def cell_of(df: pd.DataFrame) -> pd.Series:
    d = df.assign(edu3=df.education.astype(str).map(EDU3))
    return d[CELL_FIELDS].astype(str).agg(" | ".join, axis=1)


def folds(people: pd.DataFrame) -> pd.Series:
    rng = np.random.default_rng(SEED)
    return pd.Series(rng.permutation(np.arange(len(people)) % 2), index=people.pid.to_numpy())


def estimate_profiles(train: pd.DataFrame, fold: pd.Series, cells: list[str]) -> pd.DataFrame:
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import OneHotEncoder
    rows = []
    q = pd.DataFrame([c.split(" | ") for c in cells], columns=CELL_FIELDS)
    for f in (0, 1):
        fit = train[fold.loc[train.pid].to_numpy() == 1 - f]
        X = fit.assign(edu3=fit.education.astype(str).map(EDU3))[CELL_FIELDS].astype(str)
        enc = OneHotEncoder(handle_unknown="ignore").fit(X)
        prof = {"cell": cells, "fold": f}
        for c in CONSTRUCTS:
            y = fit[c].to_numpy(float)
            z = (y - y.mean()) / y.std()
            prof[c] = Ridge(alpha=ALPHA).fit(enc.transform(X), z).predict(enc.transform(q))
        rows.append(pd.DataFrame(prof))
    return pd.concat(rows, ignore_index=True)


def person_block(cell: str) -> str:
    return "Person:\n" + "\n".join(f"- {LABELS[f]}: {v}" for f, v in zip(CELL_FIELDS, cell.split(" | ")))


def profile_block(p: pd.Series) -> str:
    lines = [f"- {NAMES[c]}: {p[c]:+.2f}" for c in CONSTRUCTS]
    return ("Estimated psychological profile of people with these characteristics (standard deviations from the US "
            "adult average; estimated statistically from demographics, not measured for this person):\n" + "\n".join(lines))


def narrative_block(cell: str, p: pd.Series) -> str:
    age, sex, inc, edu = cell.split(" | ")
    s = [f"Persona: a {sex.lower()} aged {age}, household income {inc}, {edu}. Statistically, people with this "
         "background tend to have the following tendencies (estimated from demographics, not measured for this person; "
         "numbers are standard deviations from the US adult average):"]
    for c in CONSTRUCTS:
        d = p[c]
        if abs(d) < 0.10:
            s.append(f"They are about average in {NAMES[c].split(' (')[0]} ({d:+.2f}).")
        else:
            mag = "slightly" if abs(d) < 0.30 else "moderately" if abs(d) < 0.60 else "considerably"
            s.append(f"They are {mag} {VERBAL[c][0 if d > 0 else 1]} than most people ({d:+.2f}).")
    return " ".join(s)


def messages(fmt: str, cond: str, order: str, cell: str | None, prof: pd.Series | None) -> list[dict]:
    a, b = ("green", "grey") if order == "AB" else ("grey", "green")
    parts = []
    if fmt in ("demo", "profile"):
        parts.append(person_block(cell))
    if fmt == "profile":
        parts.append(profile_block(prof))
    if fmt == "narrative":
        parts.append(narrative_block(cell, prof))
    parts += [f"Scenario:\n{SCENARIOS[cond]}", f"Question: {QUESTION}\nOptions:\nA: {OPT[a]}\nB: {OPT[b]}",
              "Answer with a single letter: A or B."]
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n\n".join(parts)}]


def main() -> None:
    people = load_people(corrected=True)
    k = cell_of(people).value_counts()
    train = people[people.split == "train"].copy()
    assert (train.split == "train").all() and len(train) == 1442
    fold = folds(train)
    g = load_green(corrected=True)
    g = g[g.split == "train"]
    g_cells = cell_of(g)
    cells = sorted(c for c in g_cells.unique() if k.get(c, 0) >= 5)
    prof = estimate_profiles(train, fold, cells)
    prof.to_csv(HERE / "profiles.csv", index=False)
    out = []
    for cond in ("green_default", "grey_default"):
        for order in ("AB", "BA"):
            out.append({"id": f"empty|{cond}|{order}|ALL|-", "fmt": "empty", "cond": cond, "order": order, "cell": "ALL",
                        "fold": -1, "messages": messages("empty", cond, order, None, None)})
            for c in cells:
                out.append({"id": f"demo|{cond}|{order}|{c}|-", "fmt": "demo", "cond": cond, "order": order, "cell": c,
                            "fold": -1, "messages": messages("demo", cond, order, c, None)})
                for f in (0, 1):
                    p = prof[(prof.cell == c) & (prof.fold == f)].iloc[0]
                    for fmt in ("profile", "narrative"):
                        out.append({"id": f"{fmt}|{cond}|{order}|{c}|{f}", "fmt": fmt, "cond": cond, "order": order,
                                    "cell": c, "fold": f, "messages": messages(fmt, cond, order, c, p)})
    with open(HERE / "prompts.jsonl", "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r) + "\n")
    pd.DataFrame({"pid": train.pid, "fold": fold.loc[train.pid].to_numpy()}).to_csv(HERE / "folds_local.csv", index=False)
    print(len(out), "prompts;", len(cells), "cells;", pd.Series([r["fmt"] for r in out]).value_counts().to_dict())


if __name__ == "__main__":
    main()
