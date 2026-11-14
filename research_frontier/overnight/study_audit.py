"""Audit all 19 Mega-Study studies for the overnight experiment (no LLM calls).

For each study: download survey.qsf + response.csv (public GitHub mirror, Apache-2.0) into overnight/external/,
then record: rows, TWIN_ID coverage, overlap with OUR training split, Qualtrics randomizers in the survey flow
(BlockRandomizer / Randomizer elements with SubSet and branch counts), and which published LLM specifications exist.

    python research_frontier/overnight/study_audit.py
Writes overnight/results/study_audit.csv. Does not read any outcome of held-out participants (only IDs are counted).
"""
import json
import os
import time
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXT, OUT = HERE / "external", HERE / "results"
RAW = "https://raw.githubusercontent.com/TianyiPeng/Twin-2K-500-Mega-Study/main"
API_TREE = "https://api.github.com/repos/TianyiPeng/Twin-2K-500-Mega-Study/git/trees/main?recursive=1"


def get(url: str, dst: Path) -> Path:
    if dst.exists() and dst.stat().st_size > 0:
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-audit"})
            dst.write_bytes(urllib.request.urlopen(req, timeout=120).read())
            return dst
        except Exception:
            time.sleep(2 + 2 * i)
    raise RuntimeError(f"download failed: {url}")


def randomizers(qsf: dict) -> list[dict]:
    flow = next(e for e in qsf["SurveyElements"] if e["Element"] == "FL")["Payload"]
    found = []

    def walk(node, depth=0):
        for x in node.get("Flow", []) or []:
            if x.get("Type") in ("BlockRandomizer", "Randomizer"):
                kids = x.get("Flow", []) or []
                found.append(dict(type=x.get("Type"), subset=x.get("SubSet"), n_branches=len(kids),
                                  evenly=x.get("EvenPresentation"), depth=depth))
            walk(x, depth + 1)
    walk(flow)
    return found


def main() -> None:
    tree = json.loads(get(API_TREE, EXT / "tree.json").read_text(encoding="utf-8"))
    paths = [t["path"] for t in tree["tree"]]
    studies = sorted({p.split("/")[1] for p in paths if p.startswith(".dat/") and p.endswith("survey.qsf")})
    split = pd.read_csv(ROOT / "data/split.csv").set_index("pid").split
    rows = []
    for st in studies:
        qsf = json.loads(get(f"{RAW}/.dat/{st}/raw_data/survey.qsf", EXT / st / "survey.qsf").read_text(encoding="utf-8", errors="ignore"))
        resp = pd.read_csv(get(f"{RAW}/.dat/{st}/raw_data/response.csv", EXT / st / "response.csv"), low_memory=False)
        data = resp.iloc[2:]
        idcol = "TWIN_ID" if "TWIN_ID" in data.columns else None
        ids = pd.to_numeric(data[idcol], errors="coerce").dropna().astype(int) if idcol else pd.Series([], dtype=int)
        specs = sorted({p.split("/")[2] for p in paths if p.startswith(f"results/{st}/") and p.endswith("consolidated_llm_values.csv.gz")})
        rz = randomizers(qsf)
        do_cols = [c for c in data.columns if "_DO_" in c or c.startswith("FL_")]
        rows.append(dict(
            study=st, n_rows=len(data), has_twin_id=bool(idcol), n_unique_ids=int(ids.nunique()),
            n_train=int(ids.map(split).eq("train").sum()), n_test=int(ids.map(split).eq("test").sum()),
            n_randomizers=len(rz), randomizers=json.dumps(rz), n_display_order_cols=len(do_cols),
            n_specs=len(specs), has_demographics_only=any(s.startswith("demographics_only") for s in specs),
            has_empty=any(s.startswith("empty_persona") for s in specs),
            has_full_no_reasoning=any(s.startswith("full_persona_without_reasoning") for s in specs)))
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "study_audit.csv", index=False)
    pd.set_option("display.width", 250)
    print(df.drop(columns="randomizers").to_string(index=False))
    for r in rows:
        print(r["study"], r["randomizers"])


if __name__ == "__main__":
    main()
