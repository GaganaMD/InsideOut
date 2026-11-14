# 06 · LLM experiment roadmap (not executed; no API key requested or used)

## Would an LLM baseline improve the assignment?
- The brief suggests "an LLM guessing from basic facts alone" as one possible baseline.
- Peng et al. (arXiv:2509.19088) already ran demographics-only GPT-4.1 twins **on these same participants and Mega-Study outcomes**: correlation with humans r = 0.145, vs 0.197 with the full persona. Twin SDs are compressed on 154 of 164 outcomes.
- So an LLM baseline would mainly **confirm** our conclusion. Its value is (a) direct comparability on our metrics (Brier, R², calibration) and (b) answering the brief's suggestion explicitly.
- **Moderate value; not a reason to delay submission.**

## Step 0 (no API, no cost, recommended first): re-use the published Mega-Study LLM predictions
- The Mega-Study dataset card says `results.zip` contains LLM responses per study and *specification*, at `results/{study}/{specification}/consolidated_llm_values.csv`.
- Peng et al. report a demographics-only condition.
- **Feasibility unverified.** An attempt to list the 214 MB archive's contents by HTTP range requests failed because of repeated connection resets from Hugging Face on this machine. Downloading it fully and checking for a demographics-only `default_eric` specification is the first action.
- **If present:** score those predictions on **training participants only**, against our prevalence, demographic and green-values models (Brier, AUC, calibration). No participant data leave the machine.

## Step 1 (only if step 0 is unavailable): a minimal controlled experiment
- **Scope.**
  - Primary outcome: the hypothetical green-energy choice (`default_eric`).
  - Training participants only (n = 428); the frozen test split is excluded.
  - Secondary outcome: neuroticism (1–5) on a random 300 training participants.
- **Conditions (within participant).**
  - (1) empty persona: population prior;
  - (2) demographics-only (10 Tier A fields);
  - (3) demographics + measured green-values score;
  - (4) green values + default only.
  - The default condition is always given, because it is part of the scenario.
- **Prompt schema.** System message: neutral survey-simulation instruction. User message: the scenario text taken from the QSF, the condition's persona fields as `key: value` lines, and the instruction "Return JSON {"p_choose_green": number in [0,1]}". No participant ID and no free text.
- **Robustness.** 2 paraphrased templates; temperature 0. Plus 5 samples at temperature 0.7 on a 50-person subset to estimate within-model spread.
- **Models.** Chosen at run time from the OpenRouter catalogue:
  - one frontier model and one smaller or open-weight model;
  - prefer models whose training cutoff predates Twin-2K-500's public release (May 2025), to limit contamination.
  - Record the exact model IDs and dates.
- **Metrics.**
  - Brier, log loss, AUC, calibration slope and ECE: predicted probability vs actual choice.
  - Variance ratio (SD of predictions / SD of the human choice): flattening.
  - Group-level recovery: predicted vs actual choice rate by age band and by default arm.
  - Coefficient comparison: logistic regression of the predicted vs the actual outcome on demographics, which tests for stereotyping in the sense of Bisbee et al. 2024.
- **Baselines.** Prevalence; logistic demographics (M1D); green values + default (X1). Same participants, paired bootstrap.
- **Decision rule.** The demographics-only LLM is "better than statistics" if Brier ≤ the best demographic statistical model − 0.010, with a 95% CI excluding 0.
- **Call count.**

  | Outcome | Participants | Conditions | Templates | Models | Calls |
  |---|---|---|---|---|---|
  | Green choice | 428 | 4 | 2 | 2 | 6,848 |
  | Robustness samples | 50 | 4 | — | 2 (5 samples each) | 2,000 |
  | Neuroticism | 300 | 3 | 1 | 2 | 1,800 |
  | **Total** | | | | | **about 10,650** |

  About 450 input and 30 output tokens per call, so roughly 4.8M input and 0.3M output tokens.
- **Cost.** **Deliberately unpriced.** OpenRouter prices vary by model and change; they were not checked. Cost = Σ_models (input tokens × input price + output tokens × output price). Verify on the model pages before running.

## Safeguards (required before any API call)
1. **Authorisation.** You must explicitly approve sending participant-level records (demographics plus one score) to a third-party API. The brief describes the data as CC BY 4.0, but licence permission is not the same as consent to external processing. Confirm the dataset terms allow it.
2. **Minimisation.** Send only Tier A fields and one numeric score. Never send IDs, free text or the full persona. Batch prompts so that one prompt cannot be linked to a row.
3. **Retention.** Use OpenRouter provider routing that excludes providers which log or train on prompts, where that option is available; record the setting.
4. **Contamination check.** Ask each model to complete a verbatim persona fragment from the public dataset. If it reproduces it, flag possible memorisation and prefer an earlier-cutoff model.
5. **Holdout.** The frozen test split is never sent.
6. **Budget cap.** A hard limit on API spend, with a stop after any malformed-output rate above 2%.
