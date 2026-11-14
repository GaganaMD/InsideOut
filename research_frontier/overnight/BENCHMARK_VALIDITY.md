# BENCHMARK_VALIDITY: audit of the published GPT-4.1 `default_eric` comparison

**Sources:**
- `research_frontier/09_existing_llm_benchmark.md` (corrections appended to it);
- code: `overnight/benchmark_audit.py`; results: `overnight/results/benchmark_audit_*.csv`.

Training participants only (n = 428); paired participant bootstrap with 4,000 resamples.

| Check | Finding | Status |
|---|---|---|
| **What the LLM saw** | Configs on GitHub, read directly: GPT-4.1 for all three specifications.<br>• *Full persona:* `persona_text_dir: data/full_persona_text`, temperature 0.7. That is the complete Twin-2K-500 persona text, which includes the green-values items, the demographics with party/ideology/religion, and all of waves 1–4.<br>• *Empty:* `empty_persona_prompt: true`, temperature 0.7.<br>• *Demographics-only:* `data/personas_demographics_only_text`, temperature 0.7 and 0. **No public code builds that file, so the exact fields are unverified.** Peng et al. describe "14 demographic variables", and Twin's demographic block has 14 items including party, ideology and religion.<br>• Every specification sees the scenario, including the randomised default (the `survey_text` prompt). | Partly verified |
| **Target leakage** | Personas come from Twin waves (Jan–Feb 2025); `default_eric` was fielded on 2025-05-30, so no persona contains the outcome. Published-data contamination was not checked: GPT-4.1's training cutoff was not re-verified in this audit. | No leakage found |
| **Participant matching** | Exact on the anonymous `TWIN_ID`. All 428 training IDs match. The published human answers and conditions equal ours (asserted in `experiments/llm_benchmark.py`). | Verified |
| **Validity of out-of-fold comparison** | The LLM was not fitted to these data, so no cross-validation is needed for it. Our models use 5-fold out-of-fold predictions on the same people. The comparison is fair in fitting terms; it is unequal in information (see the first row). | Verified |
| **Accuracy uncertainty** | Demographics-only (T = 0) − empty: +0.000 (−0.063, +0.065). Full persona − our green values + default: +0.009 (−0.035, +0.056). Full persona − demographics-only: +0.098 (+0.054, +0.143). | 09 overstated "nothing" and "matches"; corrected |
| **Scoring hard choices** | The LLM gives one sampled choice per person. Accuracy and balanced accuracy are fair; Brier on a 0/1 prediction is not comparable with probabilistic models. | Documented |
| **Treatment-effect recovery** (randomised default: P(green \| green default) − P(green \| grey default)) | Humans **+0.217** (0.123, 0.307).<br>• Empty persona **+0.874**: exaggerated, difference +0.66 (+0.56, +0.76).<br>• Demographics-only T = 0.7: +0.111 (difference −0.11; −0.23, +0.02).<br>• Full persona **+0.084**: attenuated, difference −0.13 (−0.24, −0.03).<br>Valid only for the T = 0.7 draws; T = 0 and thresholded probabilities give *modal* answers, which exaggerate effects. | **New result** |

**Bottom line:**
- The individual-level conclusion is robust: demographics add no detectable accuracy, though with ±6-point uncertainty.
- The new finding is that **no published specification recovers the human default effect**. The persona-free twin is hyper-reactive to the default, while the full-profile twin under-reacts. That makes treatment-effect recovery the right primary target for the overnight experiment.
