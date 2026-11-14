"""APPROXIMATE re-run cost of the published GPT-4.1 specifications (no API call; local text lengths only).

The exact prompts Peng et al. sent are not public (persona text files are built by code that is not in the public
repository), so token counts are ESTIMATED from local proxies:
  full persona   ~ every Twin-2K-500 catalog question text + its options + the participant's answer labels (waves 1-4)
  demographics   ~ the 14 'Demographics' block questions + options + answer labels
  survey prompt  ~ upper proxy: all question text + choices in the study QSF; lower proxy: 1,200 chars (one scenario +
                   one question, as in the harness prompts)
Characters -> tokens at 4 chars/token (central) with a 3.5 chars/token conservative variant. Output: 50 tokens/call
(no-reasoning answers). Prices: overnight/pricing_snapshot.json.

    PYTHONUTF8=1 python research_frontier/brace_challenge_lab/F_llm_benchmark/cost_estimates.py
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CAT = ROOT / "data/raw/Twin-2K-500/question_catalog_and_human_response_csv"
OV = ROOT / "research_frontier/overnight"
OUT_TOK = 50


def qsf_chars(path: Path) -> int:
    q = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for e in q["SurveyElements"]:
        p = e.get("Payload")
        if isinstance(p, dict) and "QuestionText" in p:
            n += len(re.sub("<[^>]+>", "", p.get("QuestionText", "")))
            for c in (p.get("Choices") or {}).values() if isinstance(p.get("Choices"), dict) else []:
                n += len(re.sub("<[^>]+>", "", str(c.get("Display", ""))))
    return n


def main():
    cat = json.loads((CAT / "question_catalog.json").read_text(encoding="utf-8"))
    lab = pd.read_csv(CAT / "wave1_3_response_label.csv", low_memory=False)
    lab4 = pd.read_csv(CAT / "wave4_response_label.csv", low_memory=False)
    split = pd.read_csv(ROOT / "data/split.csv")
    train = set(split[split.split == "train"].pid)
    lab, lab4 = lab[lab.pid.isin(train)], lab4[lab4.pid.isin(train)]
    q_text = sum(len(q["QuestionText"]) + sum(len(str(o)) for o in (q.get("Options") or [])) for q in cat)
    demo = [q for q in cat if q["BlockName"] == "Demographics"]
    d_text = sum(len(q["QuestionText"]) + sum(len(str(o)) for o in (q.get("Options") or [])) for q in demo)
    d_cols = [c for q in demo for c in q.get("csv_columns", []) if c in lab.columns]
    ans_all = lab.drop(columns="pid").astype(str).apply(lambda r: r.str.len().sum(), axis=1).to_numpy() \
        + lab4.drop(columns="pid").astype(str).apply(lambda r: r.str.len().sum(), axis=1).median()
    ans_demo = lab[d_cols].astype(str).apply(lambda r: r.str.len().sum(), axis=1).to_numpy()
    full_chars = float(np.median(q_text + ans_all))
    demo_chars = float(np.median(d_text + ans_demo))
    prices = json.loads((OV / "pricing_snapshot.json").read_text())["models"]
    rows = []
    for study, qsf in (("default_eric", OV / "external/default_eric/survey.qsf"),
                       ("targeting_fairness", OV / "external/targeting_fairness/survey.qsf")):
        for survey_proxy, s_chars in (("qsf_upper", qsf_chars(qsf)), ("single_item_lower", 1200)):
          for spec, pchars in (("full_persona", full_chars), ("demographics_only", demo_chars), ("empty_persona", 0.0)):
            for cpt in (4.0, 3.5):
                tin = (pchars + s_chars + 600) / cpt          # +600 chars system instruction / headers
                for model in ("openai/gpt-4.1", "openai/gpt-4.1-mini"):
                    pr = prices[model]
                    usd = (tin * pr["in_per_m"] + OUT_TOK * pr["out_per_m"]) / 1e6
                    rows.append({"study": study, "survey_proxy": survey_proxy, "spec": spec, "chars_per_token": cpt, "model": model,
                                 "input_tokens_per_call": round(tin), "usd_per_participant": usd,
                                 "usd_per_1000_participants": usd * 1000})
    df = pd.DataFrame(rows)
    (HERE / "results").mkdir(exist_ok=True)
    df.to_csv(HERE / "results/cost_rerun_estimates.csv", index=False)
    meta = {"full_persona_chars_median": full_chars, "demographics_chars_median": demo_chars,
            "n_catalog_questions": len(cat), "n_demographic_questions": len(demo), "output_tokens_assumed": OUT_TOK}
    (HERE / "results/cost_rerun_meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))
    print(df[(df.chars_per_token == 4.0) & (df.model == "openai/gpt-4.1")].round(5).to_string(index=False))


if __name__ == "__main__":
    main()
