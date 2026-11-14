# LLM persona benchmark: plan and pre-specification (Workstream F)

Status: **section 1 written before `benchmark_offline.py` was run** (metrics and models fixed in advance). Later
sections were added after the run and are labelled.

## 1. Pre-specification (fixed before running)

**Data.** The pseudonymous training-only bundles from `research_frontier/overnight/offline/prepare_bundle.py`
(default_eric n = 428; targeting_fairness n = 260; both asserted `split == "train"`; targeting_fairness treatment is
coded from `Segment`, not the inverted `target` label). No held-out participant is read. No API call is made.

**Models (conditions).** Statistical models are fitted with repeated stratified 5-fold CV inside the training
participants (20 repeats; strata = condition x outcome); a participant's prediction is the mean of its out-of-fold
predictions over repeats. Every model except A0 sees the randomised condition, because every LLM prompt does too.

| Code | Model | Information |
|---|---|---|
| A0 | Population average (fold mean) | nothing |
| A1 | Condition-only (fold arm means) | randomised condition |
| B10_fixed | Logistic L2 C=1 / ridge alpha=1, Tier A (10 vars) + condition (= Modal run model M1) | Tier A + condition |
| B10_tuned | same, penalty chosen by inner 5-fold CV | Tier A + condition |
| B4_tuned | 4 coarsened cell fields (age band, sex, income, 3-level education) + condition, inner-CV penalty | prompt-cell fields + condition |
| C_t0 / C_t07 | Published GPT-4.1 `demographics_only` (T 0 / T 0.7), hard answer | Peng et al. demographic persona + scenario |
| E | Published GPT-4.1 `full_persona_without_reasoning` (T 0.7), hard answer | full Twin-2K-500 profile + scenario |
| empty | Published GPT-4.1 `empty_persona` (T 0.7), hard answer (reference) | scenario only |
| *_recal | CV recalibration of a published hard answer: outcome regressed on the LLM answer inside training folds (logistic for binary, linear for rating). **Labelled: uses human outcomes, so it is a hybrid, not a pure LLM prediction.** | LLM answer + fold-fitted map |
| D | LLM + statistically estimated inner-layer profile | **NOT RUN** (no inference available) |

**Metrics (all on training participants).**
- Binary (default_eric): Brier; log loss (hard answers clipped to [0.01, 0.99], labelled); accuracy (p >= 0.5);
  5-bin ECE and logit calibration slope (probabilistic models only).
- Rating (targeting_fairness, 1-9): MAE and mean squared error.
- Group level: participant-weighted mean absolute error of predicted vs human cell means over coarsened demographic
  cells (k >= 5 in the full panel, >= 8 training members).
- Treatment-effect recovery: predicted mean (treated) - predicted mean (control) vs the human difference.
- Variance compression: SD(prediction) / SD(human outcome).
- Distributional fidelity: total variation between the human response distribution and the predicted one
  (binary: |mean p - human rate|; rating: point predictions rounded to 1-9; labelled as such).
- Small groups: single-level Tier A groups with 10 <= n < 40 in the study's training sample; mean |predicted group
  mean - human group mean|.
- Uncertainty: participant bootstrap (2,000 resamples, stratified by condition) for each metric and for paired
  differences vs A1 and vs A0. For published LLM rows the treatment-effect CIs are taken from the Modal run
  `overnight/results/modal_full-20261114` (10,000 resamples) and the point estimates are asserted to match.
- Cost: published runs cost us $0. The cost of re-running a specification is estimated from approximate token counts
  and `overnight/pricing_snapshot.json` (GPT-4.1 $2 / $8 per M tokens).

**Inner-layer constructs (wave-4 retest).** Run only if published LLM predictions for our six constructs exist and
can be matched by ID.

---
*Sections 2-7 were written after the offline run. Deviations from section 1, decided after seeing outputs and
therefore labelled: (a) bootstrap CIs are not reported for cell MAE, small-group MAE, TV and ECE, because the
percentile bootstrap of an absolute error of noisy means is biased upward (the point estimates fell below their own
intervals); (b) the calibration slope is not reported for A0 (near-constant prediction).*

## 2. Status of each condition

| Condition | Status | Source |
|---|---|---|
| A population average / condition-only | **RUN** | `benchmark_offline.py` |
| B census-demographic statistical model, CV within training | **RUN** (B10_fixed, B10_tuned, B4_tuned) | `benchmark_offline.py` |
| C LLM given census fields | **Proxy RUN** = published GPT-4.1 `demographics_only` (T 0, T 0.7). Our own information-matched C: **NOT_RUN** | published files, exact `TWIN_ID` match |
| D LLM + estimated inner-layer profile | **NOT_RUN**, prepared (`prompt_variants.py`, `PROMPT_VARIANTS.md`) | - |
| E LLM given measured profile | **Proxy RUN** = published GPT-4.1 `full_persona_without_reasoning` | published files |
| F published twins exactly matched | **RUN**: the C and E rows are F rows (all 428 / 260 training participants matched; human answers and conditions asserted equal in `prepare_bundle.py`) | - |
| Inner-layer constructs | **NOT_RUN**: no published predictions exist (section 3, item 5) | - |

Results: `MODEL_COMPARISON.csv`; interpretation: `CALIBRATION_AND_FAILURES.md`, `COST_BENEFIT.md`,
`CLIENT_RECOMMENDATIONS.md`.

**Exact blocker for C vs D.** OpenRouter path blocked (expired key); open-weight path on Modal handled in
`F2_modal_open_weight/` — a DIFFERENT model family, never to be substituted for GPT-4.1 results. No published
specification gives an LLM an *estimated* inner-layer profile, so D cannot be approximated from published files.
The published `demographics_only` run is not information-matched (section 3), so a future D run must be compared
with a C run made under the same template, model and cells, not with the published C.

## 3. Information mismatches (published specifications vs our conditions)

1. **Published `demographics_only` is not our Tier A, and its exact fields are unverifiable.** Config read directly
   (`results/<study>/demographics_only_2025-07-31/<study>_demographics_only.yaml`, downloaded to the git-ignored
   `external/configs/`): GPT-4.1, T 0.7, `persona_text_dir: data/personas_demographics_only_text`, header
   "## Persona Profile (This individual's past survey responses):". Those text files are not in the public
   GitHub repository, and the code that builds persona texts (`text_simulation/`, referenced by the `Snakefile`)
   is absent from the public tree (all 4,863 paths checked). `download_dataset.py` fetches only the full persona,
   persona summary and wave-split data. The Hugging Face Mega-Study dataset holds `results.zip` (214 MB; not
   downloaded). Twin-2K-500's `Demographics` block has 14 questions (QID11-QID24): region, sex, age, education,
   race, citizenship, marital status, **religion, religious attendance, party, political views**, income,
   household size, employment. Earlier repo notes report Peng et al. describing 14 demographic variables; if that
   is this block (likely, not verified), the LLM saw 4 identity variables that census-only Tier A excludes (Tier A
   is the other 10). Party alone triples the predictability of green values in our data (memo, section 2), so the
   C proxy has *more* information than B.
2. **Granularity.** Published personas give exact survey answers (e.g. age band and income as answered, 10+
   fields). Our B10 uses the 10 Tier A fields; B4 and the prepared prompts use 4 coarsened fields (k-anonymity).
3. **Full persona carries the measured inner layer.** `full_persona_text` is the whole Twin-2K-500 profile (~95,000
   characters median by our proxy; waves 1-4) including green-values, personality and generosity items. E measures
   the value of the person's own survey answers, not LLM inference from demographics. No target leakage:
   personas predate the Mega-Study (BENCHMARK_VALIDITY.md).
4. **Prompt and output.** Published runs used Peng et al.'s survey rendering and a long system instruction; ours use
   the harness system message and JSON probability elicitation. Published outputs are one hard answer per person,
   so they are not probabilities; the `_recal` rows are the fair probabilistic comparison and are labelled hybrid
   because the map from answer to probability is fitted on training-fold humans.
5. **No published LLM predictions of our inner-layer constructs.** Twin-2K-500 `LLM_simulation_results` (listed via
   the public Hugging Face API; not downloaded) contain wave-4 simulations, e.g. `Demographics Only - GPT4.1-mini`,
   `JSON Persona - GPT4.1`, `Persona Summary - GPT4.1-mini`. Wave 4 re-asks only heuristics-and-biases experiments,
   product pricing (QID9) and false-consensus items. None of green values, neuroticism, social desirability
   (QID27), spendthrift (QID31-34), CRT (QID52-55) or dictator giving appears in `wave4_response.csv`, so the
   inner-layer benchmark is impossible from published files.

## 4. C/D/narrative experiment, ready for execution

- **Question:** does an explicit, statistically estimated inner-layer profile (D) or the same numbers as prose
  (D-narr) improve on demographics alone (C), at matched template, model and cells?
- **Design detail, rendered prompts, privacy, counts and cost:** `PROMPT_VARIANTS.md` (template hash recorded).
- **Key design point:** the D profile is a deterministic function of the same 4 cell fields as C, built from
  training participants outside the scored sample. D adds no information about the individual; it tests whether
  spelling out the statistical consequences of demographics changes the LLM's predictions.
- **Model:** one fixed id per run (`openai/gpt-4.1`, for comparability with the published twins). Other model
  families (e.g. F2) are separate experiments, reported separately.
- **Units:** k >= 5 cells x condition x format, 3 (pilot) / 4 (full) samples at T 0.7; mean elicited `p` (binary) or
  mean expected rating and mean probability vector (fairness) per cell-condition, mapped locally to training
  participants.
- **Primary metrics (fixed now):** individual Brier (default_eric) / squared error (fairness) for D vs C and
  D-narr vs D, paired participant bootstrap with a cell-cluster bootstrap sensitivity; treatment-effect recovery
  vs the human ATE (+0.217; -1.284); SD ratio and TV (fairness TV on the elicited distribution). Secondary: ECE,
  calibration slope, cell MAE, comparison with B4_tuned (same 4 fields) and A1.
- **Decision rule:** D "helps" only if the D - C gain is >= 0.005 Brier (default_eric) or >= 0.10 squared error
  (fairness) with a 95% CI excluding 0; format matters only if |D-narr - D| exceeds the same margins. Any client
  use additionally requires beating B4_tuned and A1.
- **Power realism:** the offline run shows B4_tuned - A1 = +0.002 Brier (CI -0.005 to +0.008) on 428 people, so
  differences of ~0.005 are at the detection limit. The pilot is a feasibility test, not a validity result.

## 5. How it plugs into the existing harness (no harness change)

- `prompt_variants.py` reuses read-only `harness.tasks` (`cells`, `EDU3`, `SCENARIOS`, `ITEM_BASE`) and
  `harness.client.Client` (transports, retries, key redaction). It cannot use `harness.prompts.render` (fixed
  arms) or `harness.schema.parse_choice` (binary only), so it carries its own versioned template and a parser for
  binary and 9-level rating outputs.
- `VariantRunner` mirrors `harness.runner.Runner`: worst-case cost reserved before each call, hard budget stop,
  cache keyed by model, temperature, template hash, study, format, condition, cell and sample, stop on 401/402/403
  and on > 2% invalid outputs after 50 calls. Verified offline with a fake transport only.
- **Live wiring is deliberately absent.** Execution needs a new small CLI applying the same triple opt-in as
  `harness.cli live` (subcommand, exact confirmation sentence, key present; key loaded only after confirmation),
  `HttpTransport`, a $1 pilot cap, output to the git-ignored `overnight/runs/live/`. Owner confirmation that the
  estimated-profile arm is tier 1 is also required (`PROMPT_VARIANTS.md` section 3).
- Analysis reuses `benchmark_offline.metrics()` on the mapped prediction vectors.

## 6. Paid plan, budget and stop/go

1. **Pilot, $1 cap (upper-bound estimate $0.35):** 216 calls (6 cells x 2 conditions x 3 formats x 3 samples x 2
   studies).
   - **Stop** if valid-JSON rate < 98%, actual cost > 2x estimate, > 10% persistent errors, outputs degenerate
     (> 90% identical `p` or rating vectors; `choice` disagrees with `p` on > 20% of calls), or any cached prompt
     contains anything beyond cell fields, profile numbers and scenario.
   - **Go** to the full run only if every stop check passes and the owner approves the budget again. Agreement with
     humans is not a go criterion.
2. **Full, $5 total (upper-bound estimate $3.68, pilot calls reused from cache):** 2,328 calls. default_eric first;
   targeting_fairness only if default_eric spend is within estimate.
3. **Report** every arm and metric including nulls, template hash, served model id, date and actual spend.

## 7. Scripts

| File | Purpose | Network |
|---|---|---|
| `benchmark_offline.py` | Conditions A/B/C~/E~ on training bundles; writes `results/benchmark_offline.json` | none |
| `make_tables.py` | Builds `MODEL_COMPARISON.csv` (NOT_RUN rows with reasons) | none |
| `cost_estimates.py` | Approximate re-run cost of published specs from local text lengths | none |
| `prompt_variants.py` | Renders C/D/D-narr prompts, checks equal information, counts calls, prices, fake-transport pipeline check | none |
| `external/` (git-ignored) | Public Peng et al. configs, `download_dataset.py`, `Snakefile`, README; HF file listings | downloaded once from GitHub raw / HF API |

Run order: `benchmark_offline.py` (several minutes on a laptop CPU) -> `make_tables.py` -> `cost_estimates.py` ->
`prompt_variants.py --examples`. Note: B10_fixed Brier here (0.248) is the Brier of the repeat-averaged prediction;
the Modal run reports the mean Brier over repeats (0.252) for the same model, so they differ by construction.
