# 09 · Existing LLM digital-twin benchmark: published GPT-4.1 predictions vs our models

**Status: EXPLORATORY, training participants only (n = 428). Held-out participants are dropped before any outcome is compared.**
Run: `python research_frontier/experiments/llm_benchmark.py`. It downloads about 240 KB into `experiments/external/` (git-ignored) and writes to `experiments/results/llm_benchmark_*.csv`.

## The questions, answered
| # | Question | Answer (verified) |
|---|---|---|
| 1 | Are participant-level LLM predictions public? | **Yes.** GitHub `TianyiPeng/Twin-2K-500-Mega-Study` (Apache-2.0, public; checked through the GitHub API) has `results/<study>/<specification>/consolidated_llm_values.csv.gz`, one simulated answer row per participant. The Hugging Face `results.zip` (214 MB) holds the same material according to its card; it was not downloaded because the connection kept resetting |
| 2 | Same participants and target? | **Yes, for `default_eric`.** All 428 of our training participants appear. Their stored human answers and default conditions equal ours exactly (asserted for each specification) |
| 3 | Matchable by legitimate IDs? | **Yes.** Rows carry the dataset's anonymous `TWIN_ID`, so no re-identification is involved |
| 4 | What information did the LLM get? | Per `configs/default_eric/*.yaml`: GPT-4.1. Temperature 0.7 for `demographics_only_2025-07-31`, `empty_persona_2025-07-22` and `full_persona_without_reasoning_2025-06-18`; temperature 0 for `demographics_only_temperature_zero_2025-08-18`. The demographics-only persona text is read from `data/personas_demographics_only_text`, **whose construction code is not in the public repository**. Peng et al. describe it as 14 demographic variables. Twin's demographic block has 14 items, including **party, ideology, religion and religious attendance**, which our census-only Tier A excludes. **Unverified, but likely: the LLM had *more* information than our demographic models** |
| 5 | Are our constructs or outcomes represented? | The green-energy choice (`OPTOUT_Green` / `OPTIN_Green`): **yes**. Our six psychological scales: **no**. They are Twin-2K-500 inputs, not Mega-Study prediction targets |
| 6 | Is a direct comparison valid? | **Partly.** The outcome, coding and participants match. Differences: (a) the LLM outputs a **hard 0/1 answer**, not a probability, so Brier is unfair to it. We therefore compare accuracy, balanced accuracy and correlation with the choice. (b) Information sets differ (point 4). (c) The LLM was never fitted to these data, while our models use 5-fold out-of-fold training predictions. (d) The temperature-0.7 runs are one stochastic draw each |
| 7 | Licensing and privacy | Code and results: Apache-2.0. The data are a public, de-identified research release. Nothing left this machine: the predictions were downloaded and no participant data were sent anywhere |

## Results (training participants, n = 428; true green rate 0.472)
| Model | Information | Accuracy | Balanced accuracy | r with choice | Green rate: green / grey default |
|---|---|---|---|---|---|
| Humans (actual) | — | — | — | — | 0.58 / 0.36 |
| Prevalence | none | 0.528 | 0.500 | — | — |
| Default only (logistic) | default arm | 0.607 | 0.609 | 0.21 | — |
| Demographics + default (M1D) | Tier A + default | 0.558 | 0.556 | 0.18 | — |
| **GPT-4.1 empty persona** | default arm only | 0.591 | 0.592 | 0.18 | **0.94 / 0.06** |
| **GPT-4.1 demographics-only, T = 0** | ~14 demographics + default | 0.591 | 0.594 | 0.19 | 0.61 / 0.47 |
| GPT-4.1 demographics-only, T = 0.7 | same | 0.579 | 0.581 | 0.16 | 0.58 / 0.47 |
| Green values + default (no demographics) | 6-item scale + default | **0.680** | 0.679 | **0.43** | 0.67 / 0.24 |
| Demographics + green values + default (M3) | Tier A + scale + default | 0.659 | 0.658 | 0.39 | — |
| **GPT-4.1 full persona** | ~500 survey answers + default | **0.689** | 0.687 | 0.38 | 0.48 / 0.40 |

**Paired bootstrap accuracy differences** (GPT-4.1 demographics-only T = 0 minus ours; 2,000 participant resamples):
- vs prevalence: +0.063 (−0.005, +0.131)
- vs default-only: −0.016 (−0.077, +0.042)
- vs M1D: +0.033 (−0.030, +0.093)
- **vs green values + default: −0.089 (−0.145, −0.033)**
- vs M3: −0.068 (−0.121, −0.014)

## What this shows
1. **Demographics add nothing in the LLM either.** Demographics-only GPT-4.1 equals the empty-persona GPT-4.1 (both 0.591) and does no better than knowing the default arm alone (0.607). This replicates our central negative result with an independent method, likely given *more* demographic information than ours.
2. **One measured disposition matches a full ~500-item profile.** Our two-variable green values + default model (0.680, r = 0.43) is as accurate as GPT-4.1 given the participant's full survey history (0.689, r = 0.38). That full profile includes the same green-values items.
3. **The empty-persona LLM is hyper-rational about defaults.** It predicts 94% green under a green default and 6% under a grey default, against 58% and 36% for real people: the "hyper-rationality / flattening" distortion Peng et al. describe.

## Caveats
- Accuracy for hard predictions vs thresholded probabilities is only roughly comparable.
- The exact demographic fields the LLM received are unverified.
- The temperature-0.7 runs are single draws.
- This is exploratory and post-holdout.

## Next steps
1. Confirm the demographics-only persona fields by downloading the Mega-Study `results.zip` or `data/personas_demographics_only_text`, if published.
2. Extend the benchmark to the other 18 Mega-Study studies, with Tier A logistic or ridge models fitted on training participants. That would compare per outcome against Peng et al.'s r = 0.145.
3. If you approve an API run: obtain LLM *probabilities* (log-probabilities or repeated sampling) so Brier and calibration can be compared (`06_llm_experiment_roadmap.md`).

---

## Audit corrections (added by `overnight/BENCHMARK_VALIDITY.md`; uncertainty from `overnight/benchmark_audit.py`)
1. **"Demographics add nothing in the LLM either"** → **"No detectable difference at this n."** Demographics-only GPT-4.1 (T = 0) minus empty persona: accuracy +0.000 (95% CI −0.063 to +0.065). Differences up to about ±6 points cannot be excluded.
2. **"One measured disposition matches a full ~500-item profile"** → **"Comparable within ±5 points."** Full persona minus green values + default: +0.009 (−0.035 to +0.056). The full persona *does* beat demographics-only: +0.098 (+0.054 to +0.143).
3. **Group-rate table.** The statistical rows were *thresholded* probabilities. Those exaggerate condition differences (default-only thresholded gives 1.00 vs 0.00), so they are not comparable with the LLM rows, which are random draws at T = 0.7. Only the T = 0.7 LLM rows estimate choice rates. Treatment-effect recovery is now reported properly in `overnight/benchmark_audit.py`.
4. **Randomised default effect** (humans +0.217, CI 0.123–0.307), new:
   - empty persona +0.874: **exaggerated**, difference +0.66 (CI excludes 0);
   - demographics-only (T = 0.7) +0.111: difference −0.11 (CI −0.23 to +0.02);
   - full persona +0.084: **attenuated**, difference −0.13 (CI −0.24 to −0.03).
5. Information access is unchanged: the demographics-only fields remain unverified (the construction code is not public).
