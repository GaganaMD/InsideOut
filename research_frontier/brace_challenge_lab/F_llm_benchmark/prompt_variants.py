"""C vs D vs narrative prompt variants (Workstream F). MODEL-AGNOSTIC. NO NETWORK. PREPARED, NOT RUN.

Three information formats, one fixed template, applied to k-anonymous demographic CELLS (never individuals):
  demo       : demographics only (4 coarsened census fields)                                  -> condition C
  demo_stat  : demographics + statistically ESTIMATED inner-layer profile, as numbers          -> condition D
  demo_narr  : demographics + narrative text carrying exactly the same numbers as demo_stat    -> condition D-narrative
Studies: default_eric (binary; probability elicitation p) and targeting_fairness (1-9 rating; probability over the
9 levels). The estimated profile of a cell is a model-based group mean (ridge on the 4 cell fields), fitted on
TRAINING participants who are NOT in the scored study sample (so no scored person's attitudes enter their own prompt),
with an 80% band = estimate +/- 1.2816 x residual SD and a population percentile. No IDs, outcomes, free text or
individual profiles are ever rendered.

    PYTHONUTF8=1 python research_frontier/brace_challenge_lab/F_llm_benchmark/prompt_variants.py            # dry-run
    PYTHONUTF8=1 python research_frontier/brace_challenge_lab/F_llm_benchmark/prompt_variants.py --examples # + prompts

Execution later (NOT from this file): see LLM_PERSONA_BENCHMARK_PLAN.md section 5. `VariantRunner` reuses the overnight
harness's budget/cache/ledger design with this module's renderer and parser; it is exercised here only with an
offline fake transport. The OpenRouter path is blocked (expired key); an open-weight path on Modal is handled in
F2_modal_open_weight/ (a DIFFERENT model family, never to be substituted for GPT-4.1 results).
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OV = ROOT / "research_frontier/overnight"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(OV))
from common import CONSTRUCTS, load_green, load_people  # noqa: E402
from harness.tasks import EDU3, ITEM_BASE, SCENARIOS, cells  # noqa: E402  (read-only reuse; harness unchanged)

K_MIN = 5
FORMATS = ["demo", "demo_stat", "demo_narr"]
DEFAULT_MODEL = "openai/gpt-4.1"          # fixed for the paid plan; F2 may pass its own model id (separate results)
TEMPERATURE, SAMPLES_PILOT, SAMPLES_FULL = 0.7, 3, 4
MAX_TOKENS = {"default_eric": 40, "targeting_fairness": 120}

SYSTEM = ("You simulate how a person with the described characteristics would answer a survey question. "
          "Answer as that person would, not as an expert. Respond with JSON only.")
USER_TEMPLATE = """{profile_block}Scenario:
{scenario}

Question: {question}
{answer_block}"""
ANSWER_BINARY = """Options:
A: {A}
B: {B}

Reply with exactly this JSON and nothing else: {{"choice": "<one of A | B>", "p": <your probability, 0-1, that this person picks option A>}}"""
ANSWER_RATING = """Answer on a scale from 1 (not at all fair) to 9 (very fair).

Reply with exactly this JSON and nothing else: {{"rating": <integer 1-9, this person's most likely answer>, "probs": [<9 probabilities for answers 1..9, summing to 1>]}}"""

FAIR_TEXT = ("A snack foods company has developed a new line of snacks. Initial testing showed that, due to the taste and "
             "texture profile of the snacks, the snacks are better suited to the preferences of their female customers. "
             "The company is developing a marketing plan to promote the snacks. ")
FAIR = {"targeted_women": FAIR_TEXT + "Because they believe the snacks are best suited to their female customers, they "
                          "will advertise the snacks to women directly.",
        "broad": FAIR_TEXT + "Even though they believe the snacks are best suited to their female customers, they will "
                 "advertise the snacks broadly to the general public."}   # survey QID1459 / QID1460 wording (QSF)
STUDY = {"default_eric": {"conds": ["green_default", "grey_default"], "kind": "binary"},
         "targeting_fairness": {"conds": ["targeted_women", "broad"], "kind": "rating"}}

# construct -> (prompt label, scale description, decimals)
LABELS = {
    "green": ("green (pro-environmental) values", "1-5 scale, higher = stronger pro-environmental values", 1),
    "neuroticism": ("neuroticism", "1-5 scale, higher = more anxious and emotionally reactive", 1),
    "social_desirability": ("social desirability", "0-13 scale, higher = stronger tendency to present oneself favourably", 0),
    "spendthrift": ("spending style", "4-26 scale, 4 = strong tightwad, 26 = strong spendthrift", 0),
    "crt": ("cognitive reflection", "0-4 correct answers on a reasoning test", 1),
    "dictator_give": ("generosity", "share of a hypothetical $5 given to a stranger, 0-100%", 0),
}
FIELD_LABELS = ["age", "sex", "household income", "education"]


def variant_hash() -> str:
    return hashlib.sha256(json.dumps([SYSTEM, USER_TEMPLATE, ANSWER_BINARY, ANSWER_RATING, LABELS, FORMATS],
                                     sort_keys=True).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------- data (local only)
def study_sample(study: str, people: pd.DataFrame) -> pd.DataFrame:
    """Training participants of the study with their randomised condition (outcomes are NOT loaded)."""
    if study == "default_eric":
        g = load_green(corrected=True)
        g = g[g.split == "train"]
        return pd.DataFrame({"pid": g.pid.astype(int), "cond": g.green_condition})
    d = pd.read_csv(OV / "external/targeting_fairness/response.csv", low_memory=False, usecols=["TWIN_ID", "Segment", "target"])
    d = d[pd.to_numeric(d.TWIN_ID, errors="coerce").notna()].copy()
    seg = pd.to_numeric(d.Segment, errors="coerce")
    assert ((seg == 2) == (d.target.astype(str) == "broad")).all(), "Segment/target inversion no longer holds"
    d = pd.DataFrame({"pid": pd.to_numeric(d.TWIN_ID).astype(int), "cond": np.where(seg == 2, "targeted_women", "broad")})
    d = d.merge(people[["pid", "split"]], on="pid")
    return d[d.split == "train"][["pid", "cond"]]


def estimated_profiles(people: pd.DataFrame, exclude_pids: set) -> tuple[pd.DataFrame, dict]:
    """Model-based cell means for the six constructs from training participants outside the scored sample."""
    from sklearn.linear_model import RidgeCV
    from sklearn.preprocessing import OneHotEncoder
    tr = people[(people.split == "train") & ~people.pid.isin(exclude_pids)].copy()
    tr["edu3"] = tr.education.astype(str).map(EDU3)
    allp = people.copy()
    allp["edu3"] = allp.education.astype(str).map(EDU3)
    f = ["age_band", "sex", "income", "edu3"]
    enc = OneHotEncoder(handle_unknown="ignore").fit(allp[f].astype(str))
    grid = allp[f].astype(str).drop_duplicates().reset_index(drop=True)
    grid["cell"] = grid[f].agg(" | ".join, axis=1)
    pop = tr                                    # reference distribution: profile-source people only
    meta = {"n_source": int(len(tr)), "constructs": {}}
    for c in LABELS:
        m = RidgeCV(alphas=np.logspace(-1, 3, 9)).fit(enc.transform(tr[f].astype(str)), tr[c].to_numpy(float))
        resid_sd = float(np.std(tr[c].to_numpy(float) - m.predict(enc.transform(tr[f].astype(str))), ddof=1))
        est = m.predict(enc.transform(grid[f]))
        lo_b, hi_b = CONSTRUCTS[c][2]
        grid[f"{c}_est"] = np.clip(est, lo_b, hi_b)
        grid[f"{c}_lo"] = np.clip(est - 1.2816 * resid_sd, lo_b, hi_b)
        grid[f"{c}_hi"] = np.clip(est + 1.2816 * resid_sd, lo_b, hi_b)
        grid[f"{c}_pct"] = [int(round(100 * np.mean(pop[c].to_numpy(float) < e))) for e in est]
        meta["constructs"][c] = {"alpha": float(m.alpha_), "resid_sd": resid_sd}
    return grid.set_index("cell"), meta


# ----------------------------------------------------------------------------- rendering
def ordinal(n: str) -> str:
    k = int(n)
    suf = "th" if 10 <= k % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
    return f"{k}{suf}"


def _fmt(x, d):
    return f"{x:.{d}f}" if d else f"{int(round(x))}"


def profile_numbers(row: pd.Series) -> dict:
    return {c: {"est": _fmt(row[f"{c}_est"], d), "lo": _fmt(row[f"{c}_lo"], d), "hi": _fmt(row[f"{c}_hi"], d),
                "pct": str(int(row[f"{c}_pct"]))} for c, (_, _, d) in LABELS.items()}


def profile_block(fmt: str, cell: str, prof: pd.DataFrame | None) -> str:
    vals = cell.split(" | ")
    lines = ["Person:"] + [f"- {k}: {v}" for k, v in zip(FIELD_LABELS, vals)]
    if fmt == "demo":
        return "\n".join(lines) + "\n\n"
    nums = profile_numbers(prof.loc[cell])
    if fmt == "demo_stat":
        lines += ["", "Estimated profile of people with these characteristics (a statistical estimate from a survey of US "
                      "adults, not this person's own answers). Typical value; percentile among US adults; range covering "
                      "80% of similar people:"]
        for c, (lab, scale, _) in LABELS.items():
            n = nums[c]
            lines.append(f"- {lab} ({scale}): {n['est']}; {ordinal(n['pct'])} percentile; {n['lo']} to {n['hi']}")
        return "\n".join(lines) + "\n\n"
    if fmt == "demo_narr":
        s = ["", "About people like this person (a statistical estimate from a survey of US adults, not this person's own "
                 "answers):"]
        sent = []
        for c, (lab, scale, _) in LABELS.items():
            n = nums[c]
            sent.append(f"On {lab} ({scale}) they typically score {n['est']}, around the {ordinal(n['pct'])} percentile of US "
                        f"adults, and 80% of similar people fall between {n['lo']} and {n['hi']}.")
        return "\n".join(lines + s + [" ".join(sent)]) + "\n\n"
    raise ValueError(fmt)


def render(study: str, fmt: str, cell: str, cond: str, prof: pd.DataFrame | None) -> list[dict]:
    if study == "default_eric":
        user = USER_TEMPLATE.format(profile_block=profile_block(fmt, cell, prof), scenario=SCENARIOS[cond],
                                    question=ITEM_BASE["question"], answer_block=ANSWER_BINARY.format(**ITEM_BASE["options"]))
    else:
        user = USER_TEMPLATE.format(profile_block=profile_block(fmt, cell, prof), scenario=FAIR[cond],
                                    question="How fair is this advertising plan?", answer_block=ANSWER_RATING.format())
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def numbers_in(text: str) -> list[str]:
    return sorted(re.findall(r"\d+(?:\.\d+)?", text))


# ----------------------------------------------------------------------------- output parsing
class InvalidOutput(ValueError):
    pass


def parse(text: str, kind: str) -> dict:
    t = (text or "").strip()
    m = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", t, re.S)
    t = m.group(1) if m else t
    try:
        o = json.loads(t)
    except Exception as e:
        raise InvalidOutput(f"bad json: {e}") from e
    if kind == "binary":
        if set(o) != {"choice", "p"} or o["choice"] not in ("A", "B") or isinstance(o["p"], bool) \
                or not isinstance(o["p"], (int, float)) or not 0 <= o["p"] <= 1:
            raise InvalidOutput("binary schema")
        return {"choice": o["choice"], "p": float(o["p"])}
    if set(o) != {"rating", "probs"} or not isinstance(o["rating"], int) or not 1 <= o["rating"] <= 9:
        raise InvalidOutput("rating schema")
    pr = o["probs"]
    if not (isinstance(pr, list) and len(pr) == 9 and all(isinstance(x, (int, float)) and 0 <= x <= 1 for x in pr)
            and abs(sum(pr) - 1) <= 0.02):
        raise InvalidOutput("probs must be 9 values in [0,1] summing to 1 (+/-0.02)")
    s = sum(pr)
    return {"rating": o["rating"], "probs": [x / s for x in pr], "expected": float(np.dot(np.arange(1, 10), pr) / s)}


# ----------------------------------------------------------------------------- task list, counts, cost
def build_tasks(samples: int, pilot_cells: int | None):
    people = load_people(corrected=True)
    k_counts = cells(people).value_counts()
    tasks, coverage = [], {}
    for study, cfg in STUDY.items():
        s = study_sample(study, people)
        prof, meta = estimated_profiles(people, set(s.pid))
        s["cell"] = cells(people.set_index("pid").loc[s.pid].reset_index()).to_numpy()
        ok = s[s.cell.map(k_counts).fillna(0) >= K_MIN]
        both = ok.groupby("cell").cond.nunique()
        sizes = ok.groupby("cell").size()
        keep = sorted([c for c in sizes.index if both[c] == 2], key=lambda c: (-sizes[c], c))
        if pilot_cells:
            keep = keep[:pilot_cells]
        coverage[study] = {"n_train_scored": int(len(s)), "n_in_k5_cells": int(len(ok)),
                           "n_in_sent_cells": int(s.cell.isin(keep).sum()), "n_cells_sent": len(keep),
                           "profile_source_n": meta["n_source"], "profile_model": meta["constructs"]}
        for fmt in FORMATS:
            for cond in cfg["conds"]:
                for cell in keep:
                    assert k_counts[cell] >= K_MIN
                    msgs = render(study, fmt, cell, cond, prof)
                    for smp in range(samples):
                        tasks.append({"study": study, "kind": cfg["kind"], "format": fmt, "cond": cond, "cell": cell,
                                      "sample": smp, "messages": msgs})
    return tasks, coverage


def cost(tasks, model: str) -> dict:
    pr = json.loads((OV / "pricing_snapshot.json").read_text())["models"][model]
    n_in = sum(sum(len(m["content"]) for m in t["messages"]) / 3.5 for t in tasks)   # harness's conservative ratio
    n_out = sum(MAX_TOKENS[t["study"]] for t in tasks)                                # upper bound: output cap
    return {"model": model, "calls": len(tasks), "input_tokens_est": int(n_in), "output_tokens_cap": n_out,
            "usd_upper_bound": round((n_in * pr["in_per_m"] + n_out * pr["out_per_m"]) / 1e6, 4),
            "price_snapshot": "overnight/pricing_snapshot.json (2026-11-14; re-verify before any paid run)"}


# ----------------------------------------------------------------------------- runner adapter (no live transport here)
class VariantRunner:
    """Budgeted, cached runner for variant tasks. Mirrors harness.runner.Runner (reserve-before-send budget, cache by
    key, invalid-rate stop, fatal-status stop) but uses this module's renderer/parser. Live transport is NOT wired here:
    a live run must go through an authorised entry point that applies the harness's triple opt-in."""

    def __init__(self, model, transport, budget_usd, out_dir: Path, temperature=TEMPERATURE):
        from harness.client import Client
        pr = json.loads((OV / "pricing_snapshot.json").read_text())["models"][model]
        self.model, self.client, self.budget, self.temp, self.pr = model, Client(transport), budget_usd, temperature, pr
        self.out = Path(out_dir)
        self.out.mkdir(parents=True, exist_ok=True)
        self.spent, self.calls, self.invalid, self.stopped = 0.0, 0, 0, ""

    def key(self, t):
        return hashlib.sha256(json.dumps([self.model, self.temp, variant_hash(), t["study"], t["format"], t["cond"],
                                          t["cell"], t["sample"]]).encode()).hexdigest()

    def run(self, tasks):
        cache_p = self.out / "cache.jsonl"
        cache = {json.loads(l)["key"] for l in cache_p.read_text().splitlines()} if cache_p.exists() else set()
        for t in tasks:
            k = self.key(t)
            if k in cache or self.stopped:
                continue
            est = (sum(len(m["content"]) for m in t["messages"]) / 3.5 * self.pr["in_per_m"]
                   + MAX_TOKENS[t["study"]] * self.pr["out_per_m"]) / 1e6
            if self.spent + est > self.budget:
                self.stopped = "budget"
                break
            try:
                r = self.client.chat(self.model, t["messages"], self.temp, MAX_TOKENS[t["study"]])
            except Exception as e:  # noqa: BLE001
                if getattr(e, "status", None) in (401, 402, 403):
                    self.stopped = f"fatal_http_{e.status}"
                continue
            u = r.get("usage", {})
            self.spent += (u.get("prompt_tokens", 0) * self.pr["in_per_m"] + u.get("completion_tokens", 0) * self.pr["out_per_m"]) / 1e6
            self.calls += 1
            try:
                res, ok = parse(r["choices"][0]["message"]["content"], t["kind"]), True
            except InvalidOutput as e:
                res, ok = {"error": str(e)}, False
                self.invalid += 1
                if self.calls >= 50 and self.invalid / self.calls > 0.02:
                    self.stopped = "invalid_rate"
            if ok:
                rec = {"key": k, **{x: t[x] for x in ("study", "format", "cond", "cell", "sample")}, "result": res,
                       "usage": u, "template": variant_hash(), "model": self.model, "dry_run": bool(r.get("dry_run"))}
                with open(cache_p, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec) + "\n")
                cache.add(k)
        return {"calls": self.calls, "invalid": self.invalid, "usd": self.spent, "stopped": self.stopped}


class FakeTransport:
    """Offline only: returns schema-valid placeholder answers (NOT model output) so the pipeline can be exercised."""

    def send(self, payload):
        user = payload["messages"][-1]["content"]
        txt = '{"choice": "A", "p": 0.5}' if '"choice"' in user else '{"rating": 5, "probs": [0.1,0.1,0.1,0.1,0.2,0.1,0.1,0.1,0.1]}'
        return {"choices": [{"message": {"content": txt}}],
                "usage": {"prompt_tokens": sum(len(m["content"]) for m in payload["messages"]) // 4, "completion_tokens": 20},
                "dry_run": True}


# ----------------------------------------------------------------------------- self-checks + dry run
def checks(tasks):
    for t in tasks:
        u = t["messages"][-1]["content"]
        assert "pid" not in u.lower() and "twin_id" not in u.lower()
    by = {}
    for t in tasks:
        by.setdefault((t["study"], t["cond"], t["cell"], t["sample"]), {})[t["format"]] = t["messages"][-1]["content"]
    for v in by.values():
        stat_nums, narr_nums = numbers_in(v["demo_stat"]), numbers_in(v["demo_narr"])
        # same information: identical multiset of numbers (header '80%' appears in both once per construct / header)
        a = [x for x in stat_nums if x != "80"]
        b = [x for x in narr_nums if x != "80"]
        assert a == b, "narrative and numeric formats must carry the same numbers"
    assert parse('{"choice": "B", "p": 0.2}', "binary")["p"] == 0.2
    assert parse('{"rating": 3, "probs": [0,0.5,0.5,0,0,0,0,0,0]}', "rating")["expected"] == 2.5
    for bad, kind in [('{"choice": "C", "p": 0.2}', "binary"), ('{"rating": 3, "probs": [1,1,0,0,0,0,0,0,0]}', "rating"),
                      ("not json", "binary")]:
        try:
            parse(bad, kind)
            raise AssertionError("parser accepted invalid output")
        except InvalidOutput:
            pass
    return len(by)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--examples", action="store_true")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    a = ap.parse_args(argv)
    out = {"variant_hash": variant_hash(), "model": a.model, "temperature": TEMPERATURE}
    for name, samples, pc in (("pilot", SAMPLES_PILOT, 6), ("full", SAMPLES_FULL, None)):
        tasks, cov = build_tasks(samples, pc)
        n_groups = checks(tasks)
        out[name] = {"samples_per_prompt": samples, "cells_per_study": pc or "all k>=5 cells present in both conditions",
                     "coverage": cov, "prompt_groups_checked": n_groups,
                     "by_study": {s: cost([t for t in tasks if t["study"] == s], a.model) for s in STUDY},
                     "total": cost(tasks, a.model)}
        if name == "pilot":
            vr = VariantRunner(a.model, FakeTransport(), budget_usd=1.0, out_dir=HERE / "runs_fake_offline")
            for f in (HERE / "runs_fake_offline").glob("*.jsonl"):
                f.unlink()
            out["pilot"]["fake_transport_pipeline_check"] = vr.run(tasks)
            ex = tasks
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/prompt_variants_dryrun.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: (v if k not in ("pilot", "full") else {kk: vv for kk, vv in v.items() if kk != "coverage"})
                      for k, v in out.items()}, indent=1, default=str))
    if a.examples:
        seen = set()
        for t in ex:
            key = (t["study"], t["format"])
            if key in seen or t["sample"]:
                continue
            seen.add(key)
            print(f"\n===== {t['study']} | {t['format']} | {t['cond']} | {t['cell']} =====")
            for m in t["messages"]:
                print(f"[{m['role']}]\n{m['content']}")


if __name__ == "__main__":
    main()
