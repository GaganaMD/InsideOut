"""LOCAL ONLY. Build and verify the minimal, pseudonymous data bundle for the offline overnight experiments.

Scope (fixed): default_eric (green vs grey default -> chose $39 renewable) and targeting_fairness (ad plan targeted to
women vs advertised broadly -> fairness 1 = not at all fair ... 9 = very fair). FROZEN TRAINING PARTICIPANTS ONLY.

targeting_fairness CONDITION CODING (verified against the survey file): the displayed scenario is chosen by the embedded
field `Segment` (display logic: Segment 2 -> QID1459 "they will advertise the snacks to women directly"; Segment 1 ->
QID1460 "they will advertise the snacks broadly to the general public"). The embedded `target` LABEL IS INVERTED relative
to the text shown (Segment 2 carries target="broad"). Treatment here = saw the women-targeted plan = Segment 2.

Verification performed before anything is written (each is an assert; any failure aborts):
  * split: every bundled participant has split == 'train' in data/split.csv; no test participant is read into the bundle
  * study builders: conditions are the two expected levels; outcomes are in their documented ranges
  * outcome coding: default_eric uses the submission's audited coding (src/common.load_green); the published human
    answers (consolidated_original_answers) reproduce our human outcome and condition for every training participant
  * participant alignment: the published LLM rows match on TWIN_ID, are unique, cover every training participant, and
    carry the SAME randomised condition as the human
Bundle (git-ignored, uploaded to Modal): per study one parquet with a random row id (NOT the TWIN_ID), condition,
human outcome, 4 published GPT-4.1 predictions, the 10 Tier A census variables, a coarsened k>=5 demographic cell and
6 derived scale scores (no item responses, no free text, no full profiles). The pid->row mapping is never written.

    python research_frontier/overnight/offline/prepare_bundle.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OV = HERE.parent
ROOT = OV.parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(OV))
sys.path.insert(0, str(ROOT / "research_frontier/experiments"))
from common import CONSTRUCTS, SEED, TIER_A, load_green, load_people  # noqa: E402
from harness.tasks import cells  # noqa: E402

BUNDLE = HERE / "bundle"
SPECS = {  # label -> (default_eric folder, targeting_fairness folder); all GPT-4.1 (Peng et al. 2025)
    "demographics_t07": ("demographics_only_2025-07-31", "demographics_only_2025-07-31"),
    "demographics_t0": ("demographics_only_temperature_zero_2025-08-18", "demographics_only_temperature_zero_2025-08-18"),
    "empty_t07": ("empty_persona_2025-07-22", "empty_persona_2025-07-22"),
    "full_persona_t07": ("full_persona_without_reasoning_2025-06-18", "full_persona_without_reasoning_2025-06-23"),
}
ATTITUDES = list(CONSTRUCTS)                      # 6 derived scale scores (corrected SD and CRT)
EXT_ERIC = ROOT / "research_frontier/experiments/external"
EXT_FAIR = OV / "external/published/targeting_fairness"


def qualtrics(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path, low_memory=False)
    d = d[pd.to_numeric(d.TWIN_ID, errors="coerce").notna()].copy()     # drops the 2 Qualtrics header rows
    d["pid"] = pd.to_numeric(d.TWIN_ID).astype(int)
    assert d.pid.is_unique, path
    return d


def fairness(d: pd.DataFrame) -> pd.DataFrame:
    y = pd.to_numeric(d.fair1, errors="coerce")
    seg = pd.to_numeric(d.Segment, errors="coerce")
    assert ((seg == 2) == (d.target.astype(str) == "broad")).all(), "Segment/target inversion no longer holds"
    return pd.DataFrame({"pid": d.pid, "cond": np.where(seg == 2, "targeted_women", "broad"), "y": y})


def build_eric(people: pd.DataFrame) -> pd.DataFrame:
    import llm_benchmark as lb
    lb.fetch()
    g = load_green(corrected=True)
    g = g[g.split == "train"].copy()
    out = pd.DataFrame({"pid": g.pid, "treat": g.green_default.astype(int), "y_human": g.chose_green.astype(float)})
    for label, (spec, _) in SPECS.items():
        llm = lb.chose_green(pd.read_csv(EXT_ERIC / f"{spec}__{lb.FILES[0]}", low_memory=False))
        hum = lb.chose_green(pd.read_csv(EXT_ERIC / f"{spec}__{lb.FILES[1]}", low_memory=False))
        assert llm.pid.is_unique and hum.pid.is_unique
        m = out.merge(llm.rename(columns={"cond": "c_llm", "y": "y_llm"}), on="pid", how="left") \
               .merge(hum.rename(columns={"cond": "c_hum", "y": "y_hum"}), on="pid", how="left")
        own = np.where(m.treat == 1, "green_default", "grey_default")
        assert (m.c_hum == own).all() and (m.y_hum == m.y_human).all(), f"eric human alignment {label}"
        assert (m.c_llm == own).all() and m.y_llm.isin([0, 1]).all(), f"eric LLM alignment {label}"
        out[f"y_{label}"] = m.y_llm.to_numpy(float)
    assert set(out.y_human.unique()) <= {0.0, 1.0} and out.treat.isin([0, 1]).all()
    return out


def build_fair(people: pd.DataFrame) -> pd.DataFrame:
    hum = fairness(qualtrics(OV / "external/targeting_fairness/response.csv"))
    hum = hum.merge(people[["pid", "split"]], on="pid", how="inner")
    assert hum.cond.isin(["broad", "targeted_women"]).all() and hum.y.between(1, 9).all() and hum.y.notna().all()
    hum = hum[hum.split == "train"].copy()
    out = pd.DataFrame({"pid": hum.pid, "treat": (hum.cond == "targeted_women").astype(int), "y_human": hum.y.astype(float)})
    for label, (_, spec) in SPECS.items():
        llm = fairness(qualtrics(EXT_FAIR / f"{spec}__consolidated_llm_values.csv.gz"))
        pub = fairness(qualtrics(EXT_FAIR / f"{spec}__consolidated_original_answers_values.csv.gz"))
        m = out.merge(llm.rename(columns={"cond": "c_llm", "y": "y_llm"}), on="pid", how="left") \
               .merge(pub.rename(columns={"cond": "c_pub", "y": "y_pub"}), on="pid", how="left")
        own = np.where(m.treat == 1, "targeted_women", "broad")
        assert (m.c_pub == own).all() and (m.y_pub == m.y_human).all(), f"fair human alignment {label}"
        assert (m.c_llm == own).all(), f"fair LLM condition alignment {label}"
        assert m.y_llm.notna().all() and m.y_llm.between(1, 9).all(), f"fair LLM range {label}"
        out[f"y_{label}"] = m.y_llm.to_numpy(float)
    return out


def finish(df: pd.DataFrame, people: pd.DataFrame, k_counts: pd.Series, rng) -> pd.DataFrame:
    split = pd.read_csv(ROOT / "data/split.csv").set_index("pid").split
    assert (split.loc[df.pid] == "train").all(), "non-training participant in bundle"
    p = people.set_index("pid").loc[df.pid]
    df = df.reset_index(drop=True)
    for c in TIER_A:
        df[c] = p[c].astype(str).to_numpy()
    cell = cells(p.reset_index()).to_numpy()
    df["cell"] = np.where(k_counts.reindex(cell).fillna(0).to_numpy() >= 5, cell, "OTHER")   # k>=5 in full panel
    for a in ATTITUDES:
        df[f"att_{a}"] = p[a].to_numpy(float)
    assert df[[f"att_{a}" for a in ATTITUDES]].notna().all().all()
    df.insert(0, "row", rng.permutation(len(df)))          # pseudonymous row id; TWIN_ID dropped below
    return df.drop(columns="pid").sort_values("row").reset_index(drop=True)


def main() -> None:
    people = load_people(corrected=True)
    k_counts = cells(people).value_counts()
    rng = np.random.default_rng(SEED)
    BUNDLE.mkdir(exist_ok=True)
    manifest = {"seed": SEED, "specs": SPECS, "attitudes": ATTITUDES, "tier_a": TIER_A, "studies": {}}
    for study, builder in (("default_eric", build_eric), ("targeting_fairness", build_fair)):
        df = finish(builder(people), people, k_counts, rng)
        path = BUNDLE / f"{study}.parquet"
        df.to_parquet(path, index=False)
        assert "pid" not in df.columns and "TWIN_ID" not in df.columns
        manifest["studies"][study] = {
            "n_train": int(len(df)), "n_treat": int(df.treat.sum()), "columns": list(df.columns),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size,
            "human_treat_mean": float(df[df.treat == 1].y_human.mean()),
            "human_control_mean": float(df[df.treat == 0].y_human.mean()),
            "cells_k5": int((df.cell != "OTHER").sum())}
        print(study, manifest["studies"][study]["n_train"], "rows ->", path.name)
    (HERE / "bundle_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(json.dumps({s: {k: v for k, v in m.items() if k != "columns"} for s, m in manifest["studies"].items()}, indent=1))


if __name__ == "__main__":
    main()
