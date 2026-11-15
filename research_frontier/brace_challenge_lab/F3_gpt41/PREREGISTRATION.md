# Pre-registration: GPT-4.1 matched persona-format comparison (green-energy default study)

Written before any paid call. The pilot runs only if every pre-flight check in `preflight.py` passes. **Scaling to the full run needs a separate authorization.**

## Question
For GPT-4.1, three prompt formats are compared:
- census demographics only;
- demographics plus a statistically estimated psychological profile, as numbers;
- the same numbers written as a narrative persona.

Two questions:
1. Does the estimated profile add predictive value beyond demographics?
2. Does narrative framing change accuracy, calibration or confidence?

All three formats are judged against free statistical baselines: the population (condition) rate, and a demographic logistic model.

## Model
- **ID:** `openai/gpt-4.1` via OpenRouter.
- **Snapshot:** the catalogue's `canonical_slug` on 2026-11-15 was `openai/gpt-4.1-2025-04-14`, priced at $2 per million input tokens and $8 per million output tokens.
- **Version caveat:** the served model ID is recorded per call (`served_model`). Matching the name used by Peng et al. does **not** guarantee the same underlying version, so no claim is made that these results replicate their GPT-4.1 runs.
- **Sampling:** temperature 0, max 40 output tokens, JSON response format.
- **No logprobs:** the catalogue does not list logprobs for this route, so probabilities are elicited in the JSON instead.

## Design
This re-uses the frozen design of the open-weight benchmark: `F2_modal_open_weight/PREREGISTRATION.md`, prompts built by `build_prompts.py`, and profiles from `profiles.csv`.
- **Units:** 76 k-anonymous cells (age band × sex × income band × 3-level education, k ≥ 5 in the 2,058 panel). Together they cover 427 training participants of `default_eric`.
- **Conditions:** both randomised default conditions, each in both answer orders.
- **Profiles:** cross-fitted. The profile used for evaluation fold f is a ridge prediction from the cell fields, fit on fold 1 − f of the 1,442 training participants (tamper-tested in `test_f2.py`).
- **Matched information:** the numeric and narrative formats contain the same six numbers (tested).
- **Elicitation:** the harness's validated JSON, `{"choice": A|B, "p": P(option A)}`. Converted as P(green) = p when green is option A, otherwise 1 − p. The two orders are then averaged.
- **No-persona arm:** an empty-persona arm is included for reference.
- **What is sent:**
  - cell labels;
  - aggregate estimated z-scores;
  - public scenario text.

  No IDs, outcomes, individual scores or free text are sent. The pre-flight scans every payload.

## Pilot: feasibility only, with a $1 cap
- **Calls:** 264.
  - The 12 cells with the most `default_eric` training members, in all four formats, both folds, both conditions and both orders. That makes 244 calls including 4 empty-persona calls.
  - Plus 20 identical re-asks to measure consistency at temperature 0.
- **Estimated cost:** at most $0.31.
- **What it reports:**
  - validity;
  - actual cost and tokens;
  - served model;
  - re-ask consistency;
  - agreement between the choice field and p;
  - order sensitivity.

  **No accuracy claims are made from the pilot.**

**Go criteria for proposing the full run** (all must hold):
1. Valid JSON in at least 98% of calls.
2. Actual cost ≤ 2× the estimate and ≤ $1.
3. Re-ask mean |Δp| ≤ 0.10, and the same choice in at least 90% of re-asks.
4. Choice agrees with p (choice = A exactly when p ≥ 0.5) in at least 95% of calls.
5. p is not degenerate: SD > 0.05, and no single value takes more than 80% of calls.
6. The served model is a GPT-4.1 snapshot.

## Full run (not authorized yet)
- **Calls:** 1,556, the full F2 prompt set plus 32 re-asks. The pilot calls are cached and not paid again.
- **Estimated cost:** at most $1.82.
- **Total cap:** $5, enforced against the run's cache.

## Analysis (fixed now; identical to F2)
`F2_modal_open_weight/analyze.py`, unchanged, on the converted output (`analyze_gpt41.py`). It reports:
- **Brier score** of each participant's own cell × condition × fold probability. Differences are reported against A and B, plus profile − demo and narrative − profile.
- **Calibration** intercept and slope.
- **Default-effect recovery** against the human contrast on the same participants.
- **Confidence:** mean |p − 0.5|.
- **Stereotyping:** the correlation of predictions with the profile's green z-score.
- **Cell-level** MAE and SD, and results for small cells.

**Uncertainty:** paired cluster bootstrap over cells, 2,000 resamples, seed 20261114.

**Decision rules:**
- The LLM "adds value" only if its Brier score is below the demographic model's, with the 95% CI of the difference excluding 0.
- The profile helps if profile − demo < 0, with the CI excluding 0.
- Framing matters if the narrative − profile CI excludes 0, on Brier or on confidence.

**Individual-level fidelity is not claimed.**
