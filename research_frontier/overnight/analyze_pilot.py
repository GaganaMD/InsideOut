"""Analyse a harness run (cache.jsonl) against human data and the published GPT-4.1 predictions. No API calls.

    python research_frontier/overnight/analyze_pilot.py research_frontier/overnight/runs/<dry|live>/<run-tag>

ESTIMANDS (training participants only; default_eric green-energy choice)
  * Validity: valid / attempted calls (attempted = valid cached results + logged invalid outputs + logged errors).
  * Per (cell, condition): mean elicited p(green) over the stochastic samples (primary) and share of sampled choices = A.
  * Default contrast, CELL-STANDARDISED: sum_c w_c [m_c(green default) - m_c(grey default)] / sum_c w_c over cells queried
    in both conditions, where m is the model's mean p (model) or the observed green-choice share (humans). The SAME
    weights are used for model and humans, so the two contrasts describe the same population of cells.
      - participant weights w_c = number of training participants in cell c (primary: represents the training sample)
      - cell weights w_c = 1 (secondary: every demographic profile counts once)
  * Absolute error |model contrast - human contrast|, and signed difference.
  * Individual-level accuracy: each human in a queried cell is scored against the prediction for THEIR cell and THEIR
    randomised condition (valid matching: the mapping is local and exact). Brier on mean p; accuracy on majority choice.

RESAMPLING UNIT (justification)
  The model produces predictions per CELL, so cells (not people) are the independent units of model output; humans are
  nested in cells. A two-stage cluster bootstrap is used: resample cells with replacement, then within each drawn cell
  resample the LLM samples (stochastic variability) and the human participants per condition (sampling variability).
  This propagates between-cell heterogeneity, model sampling noise and human sampling noise jointly. For the empty
  persona (one pseudo-cell) stage 1 is degenerate and only stage 2 applies.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research_frontier/experiments"))
SEED, NB = 20261114, 2000
COND = ("green_default", "grey_default")


# ----------------------------------------------------------------------------- inputs
def load_run(run_dir: Path) -> tuple[pd.DataFrame, dict]:
    run_dir = Path(run_dir)
    rows = []
    cache = run_dir / "cache.jsonl"
    if cache.exists():
        for line in cache.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            arm, cond, cell, s = r["task_id"].split("/")
            rows.append(dict(arm=arm, cond=cond, cell=cell, sample=int(s[1:]), choice=r["result"]["choice"],
                             p=float(r["result"]["p"]), cost=r.get("cost_usd", 0.0), dry_run=r.get("dry_run", False)))
    ev = {"invalid": 0, "error": 0}
    log = run_dir / "events.jsonl"
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            e = json.loads(line).get("event")
            if e in ev:
                ev[e] += 1
    rec = pd.DataFrame(rows, columns=["arm", "cond", "cell", "sample", "choice", "p", "cost", "dry_run"])
    attempted = len(rec) + ev["invalid"] + ev["error"]
    validity = dict(attempted=attempted, valid=len(rec), invalid=ev["invalid"], errors=ev["error"],
                    valid_rate=len(rec) / attempted if attempted else np.nan, spend_usd=float(rec.cost.sum()),
                    dry_run=bool(rec.dry_run.any()) if len(rec) else None)
    return rec, validity


def load_humans() -> pd.DataFrame:
    """Training participants: pid, cell (same coarsening as the prompts), randomised condition, observed choice."""
    from common import load_green
    from harness.tasks import cells
    g = load_green()
    g = g[g.split == "train"].copy()
    assert (g.split == "train").all()
    return pd.DataFrame({"pid": g.pid.to_numpy(), "cell": cells(g).to_numpy(), "cond": g.green_condition.to_numpy(),
                         "y": g.chose_green.to_numpy().astype(float)})


# ----------------------------------------------------------------------------- estimators
def _contrast(model: dict, human: dict, cells_: list, weights: dict) -> tuple[float, float]:
    w = np.array([weights[c] for c in cells_], float)
    dm = np.array([np.mean(model[c][COND[0]]) - np.mean(model[c][COND[1]]) for c in cells_])
    dh = np.array([np.mean(human[c][COND[0]]) - np.mean(human[c][COND[1]]) for c in cells_])
    return float(w @ dm / w.sum()), float(w @ dh / w.sum())


def contrast(rec: pd.DataFrame, humans: pd.DataFrame, arm: str, weighting: str = "participant", value: str = "p",
             nb: int = NB, seed: int = SEED) -> dict:
    r = rec[rec.arm == arm]
    if arm == "empty":                                  # one pseudo-cell standing for everyone
        h = humans.assign(cell="ALL")
    else:
        h = humans
    model = {c: {k: g[value if value == "p" else "choice"].map(lambda x: x if value == "p" else float(x == "A")).to_numpy()
                 for k, g in grp.groupby("cond")} for c, grp in r.groupby("cell")}
    human = {c: {k: g.y.to_numpy() for k, g in grp.groupby("cond")} for c, grp in h.groupby("cell")}
    cells_ = sorted(c for c in model if all(k in model[c] for k in COND) and c in human and all(k in human[c] for k in COND))
    if not cells_:
        return {"arm": arm, "n_cells": 0}
    sizes = h.groupby("cell").size()
    weights = {c: float(sizes[c]) if weighting == "participant" else 1.0 for c in cells_}
    m_eff, h_eff = _contrast(model, human, cells_, weights)
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(nb):
        pick = [cells_[i] for i in rng.integers(0, len(cells_), len(cells_))] if len(cells_) > 1 else cells_
        bm, bh, bw, keys = {}, {}, {}, []
        for j, c in enumerate(pick):
            key = f"{c}#{j}"
            bm[key] = {k: rng.choice(model[c][k], len(model[c][k])) for k in COND}
            bh[key] = {k: rng.choice(human[c][k], len(human[c][k])) for k in COND}
            bw[key] = weights[c]
            keys.append(key)
        a, b = _contrast(bm, bh, keys, bw)
        draws.append((a, b, a - b))
    d = np.array(draws)
    q = lambda col: (float(np.quantile(d[:, col], .025)), float(np.quantile(d[:, col], .975)))
    return {"arm": arm, "weighting": weighting, "value": value, "n_cells": len(cells_),
            "n_participants": int(sum(len(human[c][k]) for c in cells_ for k in COND)),
            "model_rate_green_default": float(np.average([np.mean(model[c][COND[0]]) for c in cells_], weights=list(weights.values()))),
            "model_rate_grey_default": float(np.average([np.mean(model[c][COND[1]]) for c in cells_], weights=list(weights.values()))),
            "model_contrast": m_eff, "model_ci": q(0), "human_contrast": h_eff, "human_ci": q(1),
            "signed_diff": m_eff - h_eff, "diff_ci": q(2), "abs_error": abs(m_eff - h_eff),
            "resampling": "two-stage cluster bootstrap: cells, then LLM samples and humans within cell" if len(cells_) > 1
            else "within-cell bootstrap of LLM samples and humans (single pseudo-cell)"}


def individual(rec: pd.DataFrame, humans: pd.DataFrame, arm: str) -> dict:
    r = rec[rec.arm == arm]
    pred = r.groupby(["cell", "cond"]).agg(p=("p", "mean"), maj=("choice", lambda s: float((s == "A").mean() >= .5)))
    h = humans.assign(cell="ALL") if arm == "empty" else humans
    m = h.join(pred, on=["cell", "cond"], how="inner")         # only participants whose own cell+condition was queried
    if m.empty:
        return {"arm": arm, "n_matched": 0}
    return {"arm": arm, "n_matched": int(len(m)), "brier": float(np.mean((m.y - m.p) ** 2)),
            "brier_prevalence": float(np.mean((m.y - m.y.mean()) ** 2)), "accuracy_majority": float(np.mean(m.y == m.maj))}


# ----------------------------------------------------------------------------- published GPT-4.1 comparison
def published_records(pids_cells: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    """Published per-participant GPT-4.1 draws reshaped as pseudo-records (cell = participant's own cell)."""
    import llm_benchmark as lb
    lb.fetch()
    humans = load_humans()
    out = {}
    for name, spec in lb.SPECS.items():
        llm = lb.chose_green(pd.read_csv(lb.EXT / f"{spec}__{lb.FILES[0]}", low_memory=False)).rename(columns={"y": "yhat"})
        m = humans.merge(llm[["pid", "yhat"]], on="pid", how="inner")
        assert len(m) == len(humans)
        out[name] = pd.DataFrame({"arm": "published", "cond": m.cond, "cell": m.cell, "sample": 0,
                                  "choice": np.where(m.yhat == 1, "A", "B"), "p": m.yhat.astype(float)})
    return out


def analyse(run_dir: Path, nb: int = NB) -> dict:
    rec, validity = load_run(run_dir)
    humans = load_humans()
    res = {"validity": validity, "arms": {}}
    for arm in sorted(rec.arm.unique()):
        res["arms"][arm] = {"participant_weighted": contrast(rec, humans, arm, "participant", nb=nb),
                            "cell_weighted": contrast(rec, humans, arm, "cell", nb=nb),
                            "choice_share_participant_weighted": contrast(rec, humans, arm, "participant", "choice", nb=nb),
                            "individual": individual(rec, humans, arm)}
    queried = sorted(set(rec[rec.arm == "tierA"].cell)) if (rec.arm == "tierA").any() else []
    pub = {}
    for name, pr in published_records().items():
        sub = pr[pr.cell.isin(queried)] if queried else pr
        pub[name] = {"same_cells": contrast(sub.assign(arm="published"), humans, "published", "participant", nb=nb),
                     "all_training_single_cell": contrast(pr.assign(arm="empty", cell="ALL"), humans, "empty", "participant", nb=nb)}
    res["published_gpt41"] = pub
    return res


def main() -> None:
    run_dir = Path(sys.argv[1])
    res = analyse(run_dir)
    (run_dir / "analysis.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    v = res["validity"]
    print(f"validity: {v['valid']}/{v['attempted']} valid ({v['valid_rate']:.1%}); invalid {v['invalid']}, errors {v['errors']}; "
          f"spend ${v['spend_usd']:.4f}; dry_run={v['dry_run']}")
    for arm, a in res["arms"].items():
        c = a["participant_weighted"]
        if c.get("n_cells"):
            print(f"[{arm}] cells={c['n_cells']} people={c['n_participants']} model contrast {c['model_contrast']:+.3f} "
                  f"{tuple(round(x, 3) for x in c['model_ci'])} | human {c['human_contrast']:+.3f} "
                  f"{tuple(round(x, 3) for x in c['human_ci'])} | diff {c['signed_diff']:+.3f} {tuple(round(x, 3) for x in c['diff_ci'])}"
                  f" | individual {a['individual']}")
    for name, p in res["published_gpt41"].items():
        s, w = p["same_cells"], p["all_training_single_cell"]
        print(f"[published {name}] same cells: contrast {s.get('model_contrast', float('nan')):+.3f} (human {s.get('human_contrast', float('nan')):+.3f}); "
              f"all training: {w['model_contrast']:+.3f} (human {w['human_contrast']:+.3f})")
    print("wrote", run_dir / "analysis.json")


if __name__ == "__main__":
    main()
