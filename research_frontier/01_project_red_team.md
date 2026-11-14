# 01 · Independent red-team audit

This is an adversarial review of the submission at commit `6140750`.
- **No frozen artefact was changed.**
- New computations are training-only: `experiments/audit_interval_check.py` and `experiments/run_experiments.py`.
- Severity labels: **CRITICAL** invalidates a headline · **MAJOR** changes interpretation or confidence · **MINOR** wording or presentation · **VERIFIED** checked against the code, test or output named.

## A1 · Scientific validity

| Question | Assessment | Evidence |
|---|---|---|
| Targets reliable and correctly operationalised? | Mostly. Green values α 0.93, neuroticism 0.90, social desirability KR-20 0.81, spendthrift 0.81. **CRT KR-20 0.58** is weak, and **dictator giving is one 6-value item**. Three shipped scores were mis-scored and are corrected. | `reports/final_audit/reliability.csv`, `scale_verification.csv`, `tests/test_final_audit.py` |
| Does the research question match what the data can identify? | Partly. "Census facts → inner layer" is identified *within this online panel*. "→ actual decisions" is **not**: every outcome is a hypothetical survey choice. Census inference (reasoning from population marginals) is not tested at all; personas are built from individual records in the panel. | Audit: no incentives in any QSF |
| Group vs individual claims distinguished? | Mostly, with one imprecise caption (see A1-c below). | `README.md` Fig 1 caption |
| Intervals calibrated for their intended interpretation? | **No, for Figure 1** (MAJOR-2 below). Figure 3 is acceptable as approximate Wald intervals. | `experiments/results/audit_interval_widths.csv` |
| Shrinkage creating misleading point estimate / CI pairs? | Yes, for dictator giving. τ² = 0, so "Typical" equals the population mean for every group and can fall outside the raw-mean CI. This is documented as audit item M2. | Live review case 1 (women) |
| Cross-validation, preprocessing, selection, bootstrap valid? | Yes for leakage: preprocessing happens inside folds and tests flip held-out outcomes. **But every bootstrap is conditional on fitted models**: out-of-fold predictions are resampled, folds are not refit. | `tests/test_exploratory*.py`, `tests/test_robustness.py` |
| Green-energy evidence overstated? | Mildly. The causal default effect is fine (randomised, 300/300). Green values → choice is correlational. The Figure 2 caption understates the default's predictive value (MAJOR-1), and "measured attitude" partly includes stated purchasing items (MAJOR-4). | X1 and X2 below |
| Hypothetical choice confused with behaviour? | No. It is labelled consistently ("hypothetical", "not a purchase"). The external-validity cost is real, though (literature: hypothetical bias). | Memo, README, cards |
| Corrected and legacy scoring consistently distinguished? | Yes, in the memo, cards, README and figures; legacy values only appear in labelled evidence files and `results/`. One residual memo/figure tension: MINOR-1. | grep audit; `tests/test_final_audit.py::test_cli_*` |

### A1-a · Figure 1 intervals: estimand audit
- **What is computed** (`tools/make_figures.py::fig1`):
  - the ridge model is fitted **once** on the 1,442 training participants;
  - 2,000 bootstrap resamples of the 616 held-out participants are drawn;
  - R² is recomputed against the fixed training-set mean.
- **Estimand.** The out-of-sample R² *of this specific fitted model* in the population the held-out set represents. It is conditional on the training sample. It is **not** the expected R² of the method (ridge on Tier A at n ≈ 1,442) across re-fits.
- **Resampling unit.** Participants, which is correct, since there is one row per participant.
- **Missing component.** Refit variability. On training data only, bootstrapping the training sample, refitting, and scoring out-of-bag gives these interval widths (`audit_interval_widths.csv`):

  | Construct | Figure 1 interval width (model fixed) | Width with refitting (training out-of-bag) |
  |---|---|---|
  | Neuroticism | 0.102 | 0.101 |
  | Social desirability† | 0.079 | 0.093 |
  | Green values | 0.045 | 0.076 |
  | CRT† | **0.024** | **0.078** |

  The out-of-bag means are lower than the held-out point estimates, as expected: each bootstrap fit uses only about 63% unique participants.
- **Consequence.** For neuroticism the fixed-model interval is about right. For the weak constructs it understates total uncertainty by up to about 3×. CRT's held-out interval (0.009–0.033) *excludes zero*, but refit uncertainty easily includes zero (out-of-bag −0.06 to +0.02).
- **Recommended caption:** "Bars: 95% bootstrap intervals over held-out participants for the fitted model; they exclude model-refit uncertainty, which is comparable for neuroticism but about 2–3× larger for the weakest constructs."

### A1-b · Figure 3 intervals
- **What is computed.** Wald intervals for the d of training members and of held-out members, using the training population mean and SD as fixed references.
- **Known approximations:**
  - population-SD uncertainty is ignored, which is negligible at n = 1,442;
  - for the training d, persona members are included in the reference population. This attenuates d by roughly the persona's share, about 13–20% of the panel;
  - there is no multiplicity adjustment across 18 persona × construct cells.
- **Appropriate for descriptive use; acceptable.** The held-out intervals involve no fitted model, so the fixed-model issue doesn't arise.

### A1-c · Is "held-out R² = group-level signal" correct?
- **Not as worded.** Held-out R² is an **individual-level** metric: the proportional reduction in squared error when predicting each held-out *person*, compared with the population mean.
- **What is true:** the predictions are additive functions of coarse categories, so they behave like **group (cell) averages**. R² = 0.17 means group averages explain 17% of individual variation.
- **Recommended Figure 1 caption ending:** "R² is the share of individual-level variance predicted. Because the predictions are averages for demographic cells, R² = 0.17 means those cell averages differ meaningfully (65+ vs 18–29: d = −0.87) while still leaving 83% of person-to-person variation unexplained."

## A2 · Alternative explanations for the central negative result
The negative result: census facts predict values and choices poorly.

| Explanation | Supporting evidence | Contradicting evidence | Testable now? | Distinguishing experiment / what would change our view |
|---|---|---|---|---|
| Measurement error / reliability ceiling | CRT KR-20 0.58 and single-item dictator giving cap R² | Green values (α 0.93) and spendthrift (0.81) are reliable yet reach only 2.5% and 4.5% of reliable variance (`headline_challenge/scale_properties.csv`) | Done | Test–retest of the scales (not repeated in wave 4). If corrected R² for green values exceeded about 0.10, the claim would weaken |
| Underfitting | — | Ridge, OLS and boosting agree; tuning doesn't help (`model_families.csv`, robustness D3/D4) | Done | A larger n with nonlinear models beating ridge by > 0.03 R² |
| Overfitting | Full Tier A logistic with C = 1 has calibration slope 0.25–0.45; **X1: demographics make green-choice prediction *worse* (−0.012 Brier)** | Regularised models only reach the base rate | Done (X1) | Already informs the claim: at n = 428, demographics *harm* prediction |
| Interactions / nonlinearity | — | Boosting with interactions is worse than ridge | Done | — |
| Feature coarsening (4 age bands, 5 income bands) | Plausible, since age is the main signal | Cannot test: no finer data | **No** | Exact age and income. If R² for neuroticism rose above 0.25, "age-linked" would sharpen rather than reverse |
| Selection / imbalance | The Mega-Study skews older | Reweighting changes the green-values OR 2.54 → 2.56 (`headline_challenge/reweighting.json`) | Partly | A probability sample |
| Domain-specific vs general traits | Domain attitudes predict domain choices (green values OR ≈ 2.5; redistribution ΔR² +0.34) | — | Done | Consistent with the literature (Hu & Collier 2024: persona variables explain < 10%) |
| Heterogeneous predictability | P3's green effect is concentrated in men | No systematic subgroup test | Partly | Residual-variance by subgroup (not run: forking-path risk) |
| Metric choice | R² penalises constructs with low variance | Brier, AUC, MAE and R² all agree in direction | Done | — |
| Group vs individual confusion | Group gaps are large (d up to 0.87) while individual R² is low | — | Done | This is the *explanation*, not an alternative: both are true |

## A3 · Independent error search

| # | Severity | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| 1 | **MAJOR** | The README Figure 2 caption says the default "adds little prediction once green values are known". **Training-only X1 shows the default adds ΔBrier −0.014 (CI −0.025 to −0.003) beyond green values**, above the pre-set 0.010 threshold. The existing M3 vs M2 contrast was also −0.013 (CI −0.024 to −0.001), labelled "borderline". | `experiments/results/x1_x2_paired_contrasts.csv` (post-hoc contrast, labelled) | Reword: "the default adds a modest but detectable amount (ΔBrier ≈ −0.013) beyond green values" |
| 2 | **MAJOR** | Figure 1's intervals exclude refit uncertainty. CRT's "CI excluding 0" is an artefact of conditioning on one fitted model. | A1-a above | Caption wording; optionally show training CV intervals alongside |
| 3 | **MAJOR** | In the green-choice models, demographics are not neutral but **harmful** at n = 428. Green values + default *without* demographics beats M3 by −0.012 (CI −0.024 to −0.001). M3's calibration slope is 0.70 vs 0.99. | X1 | Strengthens the headline; the README could state that "demographics + attitude" underperforms "attitude alone" |
| 4 | **MAJOR** | Construct overlap: the green-values items about purchasing and cost (1, 3, 6) predict the choice better than the concern/identity items (2, 4, 5), by ΔBrier 0.015. The attitude-only items still beat default-only by −0.026 (meaningful). | X2 | Narrow "a measured attitude" to "a measured environmental disposition (including stated purchasing habits)" |
| 5 | MINOR | The memo says "CRT is not predictable (R² ≈ 0.01)" (training CV), while Figure 1 shows held-out CRT R² 0.021 with an interval excluding 0. Explained by #2, but a reader sees a contradiction. | Memo §1; `figures/data/fig1_heldout_r2.csv` | Fix via the #2 caption |
| 6 | MINOR | Figure 1 caption: "group-level signal" is imprecise. | A1-c | Replacement wording above |
| 7 | MINOR | The README figure numbering (reading order) differs from the file numbering. | README vs `figures/` | Rename or renumber when the README is next edited |
| 8 | MINOR | The Mermaid pipeline was validated locally (`tools/render_mermaid.py`, negative control) but **not on github.com**. | — | Check after the first push |
| 9 | MINOR | A subagent citation attached PMC2922931 to Soto et al. 2011; that record is Noftle & Fleeson 2010. It was not used in any deliverable (AI note omits volume/pages). | Verified during the polish pass | Keep omitted |
| 10 | MINOR | The CRT re-score counts the typo "eemily" (1 person) as wrong. | `src/common.py::rescore_sd_crt` | Negligible |
| V1 | VERIFIED | The split is balanced on non-stratified variables: maximum train–test share difference is 0.052 (race), ≤ 0.026 elsewhere. | This audit (crosstab of `data/split.csv`) | — |
| V2 | VERIFIED | Persona criteria are unchanged since the holdout script commit; only text changed in `config/personas.json`. | `reports/final_audit/integrity_checks.json` | — |
| V3 | VERIFIED | Figure 1 and Figure 3 point estimates equal the frozen or corrected result files. | Asserts in `tools/make_figures.py` | — |
| V4 | VERIFIED | Out-of-fold predictions re-used by X1 match participant order and folds. | Assert in `run_experiments.py` | — |
| V5 | VERIFIED | Persona traits are not mere composition (X3). All six robust traits keep 56–77% of their size after adjusting for the other census variables; adjusted CIs exclude 0. | `x3_composition_adjustment.csv` | — |

**No CRITICAL issue was found.**

## Five most consequential remaining weaknesses (ranked)
1. **No real behaviour.** Every "decision" is a hypothetical choice in a scenario that closely mirrors Pichert & Katsikopoulos (2008). The hypothetical-bias literature (List & Gallet 2001; Murphy et al. 2005) warns that levels transfer poorly.
2. **The population-inference gap.** Brace's use case is inferring the inner layer from *census marginals*. We only test individual-record prediction inside a non-representative online panel. No census or ACS linkage or reweighting was done.
3. **Uncertainty communication.** Fixed-model intervals in Figure 1; no multiplicity control across 18 persona cells; P3 came from a ~1,000-group search.
4. **Measurement fragility in the source data.** Three of six shipped scores were wrong. Two constructs (CRT, dictator giving) are too unreliable or coarse to support group comparisons.
5. **No LLM or expert baseline of our own.** The brief suggests one. The closest evidence, Peng et al. on the same participants (demographics-only twins r = 0.145), is external and not directly comparable to our metrics.
