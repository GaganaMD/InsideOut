"""Turn results/benchmark_offline.json into MODEL_COMPARISON.csv (computed numbers only; non-run conditions = NOT_RUN).

    PYTHONUTF8=1 python research_frontier/brace_challenge_lab/F_llm_benchmark/make_tables.py
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
META = {
    "A0": ("A", "Population average (training-fold mean)", "nothing", "probability/mean (CV)"),
    "A1": ("A", "Condition-only (training-fold arm means)", "randomised condition", "probability/mean (CV)"),
    "B10_fixed": ("B", "Tier A (10 census vars) + condition; L2 C=1 / ridge alpha=1 (= Modal M1)", "Tier A + condition", "probability/mean (CV)"),
    "B10_tuned": ("B", "Tier A (10 census vars) + condition; inner-CV penalty", "Tier A + condition", "probability/mean (CV)"),
    "B4_tuned": ("B", "4 coarsened cell fields + condition; inner-CV penalty", "age band, sex, income, edu3 + condition", "probability/mean (CV)"),
    "C_t0": ("C~F", "Published GPT-4.1 demographics_only T=0 (exact TWIN_ID match)", "Peng et al. demographic persona (~14 items incl. party/ideology/religion; unverified) + scenario", "hard answer"),
    "C_t07": ("C~F", "Published GPT-4.1 demographics_only T=0.7 (exact TWIN_ID match)", "as C_t0", "hard answer (single draw)"),
    "E": ("E~F", "Published GPT-4.1 full_persona_without_reasoning T=0.7 (exact TWIN_ID match)", "full Twin-2K-500 profile (~500 answers, incl. attitude items) + scenario", "hard answer (single draw)"),
    "empty": ("ref", "Published GPT-4.1 empty_persona T=0.7 (exact TWIN_ID match)", "scenario only", "hard answer (single draw)"),
}
for k in ("C_t0", "C_t07", "E", "empty"):
    c, d, i, _ = META[k]
    META[f"{k}_recal"] = (c + "_recal", d + " -> CV recalibrated on training-fold humans (HYBRID, labelled)", i + " + fold-fitted map", "probability/mean (CV recalibration)")

NOT_RUN = [
    ("D", "LLM + statistically estimated inner-layer profile (numeric)", "4 cell fields + model-based group means of 6 constructs",
     "NOT_RUN: OpenRouter path blocked (expired key); no inference permitted in this workstream. Prepared in prompt_variants.py (format demo_stat)."),
    ("D_narr", "LLM + same estimated profile as narrative text", "identical numbers to D, prose form",
     "NOT_RUN: same blocker. Prepared in prompt_variants.py (format demo_narr)."),
    ("C_own", "LLM given the SAME 4 census cell fields as B4 (our template)", "4 cell fields + scenario",
     "NOT_RUN: same blocker. Prepared in prompt_variants.py (format demo) and harness tierA arm."),
    ("inner_layer", "LLM predictions of the six inner-layer constructs (wave-4 retest)", "-",
     "NOT_RUN: no published LLM predictions exist for these items. Twin-2K-500 LLM_simulation_results cover wave-4 items only (heuristics-and-biases, pricing); none of green values, neuroticism, social desirability, spendthrift, CRT or dictator giving is re-asked in wave 4."),
]


NO_CI = {"cell_mae", "small_group_mae", "tv", "ece"}


def m_sd_tiny(r):
    return r.get("sd_ratio") is not None and r["sd_ratio"] < 0.01


def fmt_ci(v):
    return v if isinstance(v, list) else [None, None]


def main():
    res = json.loads((HERE / "results/benchmark_offline.json").read_text())
    rows = []
    for r in res["rows"]:
        cond, desc, info, ptype = META[r["model"]]
        loss = "brier" if r["study"] == "default_eric" else "mse"
        out = {"study": r["study"], "condition": cond, "model_code": r["model"], "description": desc, "information": info,
               "prediction_type": ptype, "status": "RUN", "n": r["n"]}
        mets = (["brier", "logloss", "accuracy", "ece", "cal_slope"] if loss == "brier" else ["mae", "mse"]) + \
               [f"{loss}_gain_vs_A1", f"{loss}_gain_vs_A0", "ate_pred", "ate_diff", "sd_ratio", "tv", "cell_mae", "small_group_mae"]
        if loss == "mse":
            out.update({"brier": None})
        for m in mets:
            lo, hi = fmt_ci(r.get(f"{m}_ci"))
            if m in NO_CI:                     # |noisy quantity| metrics: percentile bootstrap is biased upward
                lo, hi = None, None
            key = m.replace(f"{loss}_gain", "loss_gain")
            out[key], out[f"{key}_lo"], out[f"{key}_hi"] = r.get(m), lo, hi
        if m_sd_tiny(r):
            out["cal_slope"] = out["cal_slope_lo"] = out["cal_slope_hi"] = None   # undefined for a near-constant prediction
        out.update(ate_human=r["ate_human"], n_cells=r["n_cells"], n_small_groups=r["n_small_groups"],
                   ate_ci_source=r["ate_source"])
        rows.append(out)
    for s in ("default_eric", "targeting_fairness"):
        for cond, desc, info, why in NOT_RUN:
            rows.append({"study": s, "condition": cond, "model_code": cond, "description": desc, "information": info,
                         "prediction_type": "-", "status": why})
    df = pd.DataFrame(rows)
    num = df.select_dtypes("number").columns
    df[num] = df[num].round(4)
    df.to_csv(HERE / "MODEL_COMPARISON.csv", index=False)
    print(df[["study", "model_code", "status", "brier", "accuracy", "mae", "mse", "loss_gain_vs_A1", "loss_gain_vs_A1_lo",
              "loss_gain_vs_A1_hi", "ate_pred", "ate_diff", "sd_ratio", "tv", "cell_mae", "small_group_mae"]].to_string(index=False))


if __name__ == "__main__":
    main()
