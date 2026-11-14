# Live review simulation: 30 questions

> **Update after commit `0852b63` / `5eddaf6` (2026-11-15).** Several defects quoted below as live have since been fixed in the submission. Each fix is logged in `reports/final_audit/post_review_corrections.md`:
> - the repeated-criteria bug: `sex=Male; sex=Female` now exits 2 with "contradictory";
> - the %/raw-unit CI tables;
> - "concentrated in men";
> - "is self-presentation";
> - "every age band";
> - the "top third" label;
> - "nearly all" of SD's R².
>
> The strong answer is now: "We found it in an internal audit, fixed it without changing any estimate, and logged it." The 10-person behaviour-cell rule in the CLI, the raw-d vs shrunk-value labels, and the tie-blind "% other side" column are **still open**.

**Purpose.** Rehearsal for the 90-minute Brace review. Each question gives: **Q** (as a sharp interviewer would put it), **Strong answer must** (what has to be covered), **Evidence** (file and exact number), **Weak answer** (and why it fails), **Follow-up**.

**Ground rules for every answer**
- Say whether a number is frozen confirmatory (`results/`), corrected scoring (`reports/final_audit/corrected_scores/`), or exploratory and training-only (`research_frontier/…`, `reports/exploratory/`).
- When a question is about a known defect (marked **[DEFECT]**), state the defect first and plainly, then the corrected claim. Don't defend the original wording.
- Never cite the open-weight (Qwen/Modal) benchmark in `F2_modal_open_weight/`. It is unfinished.
- Abbreviations: SD = social desirability; d = standardised difference from the training population; MAE = mean absolute error.

---

## Part 1: Human insight and behavioural explanation (10)

### H1. "Three personas from census data are really one age gradient. Where is the human insight?"
- **Strong answer must:** concede that it is largely true and say exactly how much. Neuroticism is the one robust trait, and it is age plus income. Then give the insight that remains: what census data *cannot* see (values) and what does move choices (the default and green values).
- **Evidence:**
  - P3's neuroticism and SD carry **no** within-age marital signal. Within 18–29, never-married vs partnered: neuroticism −0.01 (−0.26, +0.25); SD −0.03 (−0.30, +0.23). Source: `A_mechanisms/PERSONA_MECHANISMS.md`, P3 adjustment table.
  - P2's lower SD is entirely age: within 18–49, low income gives −0.01 (−0.16, +0.14).
  - P2's neuroticism splits about half and half: age mix +0.23 (0.16–0.30), income within age +0.24 (0.15–0.33).
  - The memo already says so: "Three personas from census data are closer to two" (`reports/memo.md` §5).
- **Weak answer:** "Each persona has its own distinct psychology." This is contradicted by the repo's own mechanism checks, and Brace will have read the memo.
- **Follow-up:** "Then which persona would you actually ship to a client, and what would its card say?" (Answer: an age-based temperament/self-presentation description, plus an explicit "values unknown" box.)

### H2. "Why are older people calmer? Do people mellow with age?"
- **Strong answer must:** separate prediction (held-out, solid) from cause (not identified). Name the four candidate explanations: maturation, cohort, survivorship/panel selection, and response style. Say which ones the data can rule out.
- **Evidence:**
  - P1 neuroticism: train d −0.43 → held-out −0.58, MAE gain +13.2% (`reports/personas/P1_adults_65plus.md`).
  - Survives Tier A adjustment: −0.41 (−0.57, −0.26). Decline is linear across bands: −0.30 per band, departure from linearity p = 0.70.
  - Acquiescence explains at most about 0.1 SD: forward-keyed −0.55 vs reverse-keyed −0.32, and all 8 items are negative (`PERSONA_MECHANISMS.md`).
  - Age, cohort and survival are perfectly confounded in one cross-section (`A_mechanisms/CAUSAL_LIMITATIONS.md` §1).
- **Weak answer:** "Yes, maturity reduces neuroticism (Roberts et al.)." That makes a causal claim from cross-sectional data, and Roberts et al. (2006) is longitudinal evidence about *other* samples.
- **Follow-up:** "What one dataset would settle it?" (Repeated measures of the same people several years apart, i.e. a cohort-sequential design.)

### H3. **[DEFECT]** "Your memo says part of the 65+ calm is self-presentation. How do you know it's not just that calm people answer the SD scale that way?"
- **Strong answer must:** say "we don't know; the memo overclaims." The SD adjustment gives an *upper bound* on the style share, not an estimate. SD scales carry real personality variance.
- **Evidence:**
  - Memo §2: "Part of the older group's 'calm' profile is self-presentation", based on −0.50 → −0.31 after SD adjustment.
  - The correct wording is in `CAUSAL_LIMITATIONS.md` §2 item 2: "up to about a third of the gap is shared with SD; whether that share is style or substance is not identified".
  - External: McCrae & Costa (1983), doi:10.1037/0022-006X.51.6.882 (abstract-level), on SD scales as substance.
  - SD correlates −0.44 with neuroticism (`reports/final_audit/headline_challenge.md`).
- **Weak answer:** "Controlling for SD shrinks the gap, so it's self-presentation." This treats a covariate adjustment as identification of mechanism.
- **Follow-up:** "What measurement would separate style from substance?" (Informant reports or behavioural measures of affect.)

### H4. **[DEFECT]** "'Low income goes with higher neuroticism within every age band.' Every band?"
- **Strong answer must:** no. It holds below 65. At 65+ the direction holds but the CI includes 0, and the gradient shrinks with age. The causal direction is unknown (strain → distress, distress → lower earnings, or health driving both).
- **Evidence:**
  - Train, low income minus other, by band: 18–29 +0.37 (0.16–0.56); 30–49 +0.39 (0.20–0.56); 50–64 +0.23 (0.04–0.41); **65+ +0.15 (−0.11, +0.42)** (`PERSONA_MECHANISMS.md`, P2).
  - Memo §2 has the overclaim. The pooled +0.30 SD (0.20–0.40) is fine as an age-adjusted average.
- **Weak answer:** quoting the pooled +0.30 as if it applied to every band.
- **Follow-up:** "Why might it fade at 65+?" (Retirement income is less tied to current earnings, and the cell is small, n = 194 for the whole band. Speculative: say so.)

### H5. **[DEFECT]** "You say P3's green gap is concentrated in young never-married men. Show me the interaction test."
- **Strong answer must:** there was no interaction test, and the interaction is null. The apparent male concentration comes from comparing against the whole population, where young men are already less green. Within 18–29 the marital gap is present in both sexes, and is if anything larger in women.
- **Evidence** (`PERSONA_MECHANISMS.md`, P3 composition; `CAUSAL_LIMITATIONS.md` §2 item 1):
  - P3 × male interaction: −0.14 (−0.45, +0.16).
  - Within 18–29, never-married vs partnered: men −0.41 (−0.77, −0.06), n = 111 vs 27; women **−0.59 (−0.91, −0.28)**, n = 86 vs 48; interaction +0.18 (−0.31, +0.66).
  - Young men overall: −0.31 z; young women: +0.09 z.
- **Weak answer:** "Men d −0.40 is significant and women −0.12 isn't." That is the classic difference-in-significance error.
- **Follow-up:** "So what *is* male-specific?" (The general youth deficit in green values, not the marital gap.)

### H6. "So young single people are less green because they're single?"
- **Strong answer must:** no causal claim. Name what marital status is a proxy for (education, student status, sex mix), the reverse direction (green, settled people partner earlier), the small comparison group, and the search that produced P3.
- **Evidence:**
  - Within-age gap −0.58 → −0.39 with Tier A adjustment → −0.31 (CI just includes 0) with employment.
  - The comparison group is n = 75 partnered 18–29s, of whom 60% hold a BA vs 33% in P3 (`PERSONA_MECHANISMS.md`).
  - Party doesn't explain it (−0.46).
  - External evidence leans against a partnering effect: Zoch & Kapelle (2025), doi:10.1007/s11111-025-00490-x (`ALTERNATIVE_EXPLANATIONS.md`).
  - P3 was chosen from about 1,000 candidate groups (P3 card).
  - Individual-level gain is **+0.7%** (`reports/personas/P3_young_never_married.md`).
- **Weak answer:** a life-course story ("partnering creates a stake in the future"). The card itself labels this speculation and dropped it.
- **Follow-up:** "If it's mostly education, why not define the persona by education?" (Because the pre-registered rule chose it. Re-defining after the fact is forking.)

### H7. **[DEFECT]** "Half of the greenest people refuse the green tariff. So green attitudes are cheap talk?"
- **Strong answer must:** reject the framing, with numbers:
  - "top third" is actually the top 41% (ties at ≥ 4.0);
  - the 47% depends on the cut-off;
  - no GREEN item mentions paying more;
  - the "do" is hypothetical and unincentivised;
  - "a stable feature of the population" overclaims from n = 87 and n = 46.
  The supported finding is that green values strongly predict the costed choice, and the default moves even the greenest.
- **Evidence** (`C_saydo/SAY_DO_GAP_REASSESSMENT.md` §7a):
  - Decline under the grey default: 51% above the median, 47% at ≥ 4.0 (41% of the sample), 40% top 20%, 29% top 10%, 25% at GREEN = 5 (n = 16).
  - The frozen cut is `tr.green >= tr.green.quantile(2/3)` (`src/saydo.py` line 97).
  - Train 47% (37–58) vs test 50% (36–64).
  - Reliability correction still leaves about 34–42% declining (α 0.93).
  - OR per SD of GREEN: 2.95 (1.96–4.43) (`results/saydo.json`).
- **Weak answer:** "The say–do gap replicates at ~50%, so attitudes don't translate." This repeats every overclaim at once.
- **Follow-up:** "Then what would you call it?" ("Most green-valued respondents don't accept a +$7/month (+22%) premium plus a switch in a hypothetical scenario.")

### H8. "The default moved choices by 25 points. Why? And does it work on people who are already green?"
- **Strong answer must:** the effect is causal (randomised) but the mechanism is untested: endorsement, effort and reference dependence are all possible. It works among the greenest too. Whether attitudes matter more under switching (H4) is inconclusive. Name the contamination risk: everyone also saw an organ-donor default.
- **Evidence** (`SAY_DO_GAP_REASSESSMENT.md` §4, §2, "Supported finding"):
  - Default +24.7 points (16.3–33.1) unadjusted; +22.7 (13.3–31.9) Tier A-adjusted.
  - Among the top group (GREEN ≥ 4, n = 176): **+25.8 (10.2–39.5)**, 53% → 79%.
  - H4 interaction OR 0.77 (0.39–1.43).
  - Order × default OR 1.76, p = 0.19 (low power).
- **Weak answer:** "Defaults work because of inertia" (stated as fact), or "the default barely matters", misreading the memo §6 "borderline ~0.01" Brier increment, which is a predictive increment, not the causal effect.
- **Follow-up:** "Design the study that identifies the mechanism." (Active-choice arm, effort-equalised arm, disclaimer arm; `research_frontier/07_decision_memo.md` §7.)

### H9. "Your P2 'budget-constrained idealist' story failed. What does that tell you about how you generate insight?"
- **Strong answer must:** own it. A coherent story was built from a 33-person cell. Pre-registration plus the holdout caught it. The general lesson is the minimum cell rule and not narrating persona behaviour rates.
- **Evidence:**
  - P2 grey-default rate: 27% train (n = 33) → 47% test (n = 19) (`reports/personas/P2_under50_income_below_50k.md`).
  - H5 green × income OR 0.84 (0.52–1.35). The income main effect goes the wrong way on test: OR 2.0 (0.95–4.2) (`reports/memo.md` §2).
  - Training-only, out-of-fold: adding P1/P2/P3 membership to the condition makes choice prediction *worse*, ΔBrier **+0.0036 (+0.0017, +0.0055)** (`D_review/cli_outputs/helper_choice.txt`; run for this rehearsal).
- **Weak answer:** "It's a small-sample fluke; the story is still plausible." That keeps the narrative and drops the evidence.
- **Follow-up:** "How would you stop an analyst at Brace from doing the same thing?" (Cell minimum of at least 40 per condition, a hierarchical model, and no behavioural line on cards without a holdout check.)

### H10. "Give me one insight a client couldn't get from a demographic dashboard."
- **Strong answer must:** measuring one domain attitude beats any amount of demographic slicing for this choice. An LLM given demographics doesn't fix that either.
- **Evidence:**
  - Training-only, out-of-fold, adding green values to the condition: ΔBrier **−0.0353 (−0.0512, −0.0202)**; adding Tier A: **+0.0144 (+0.0013, +0.0275)**, i.e. worse (`helper_choice.txt`, this rehearsal).
  - Consistent with `reports/exploratory/values_vs_demographics.md`: M3 vs M1D −0.035; M1 vs M0 +0.011 (−0.004, +0.026).
  - The 6-item scale plus default matches the GPT-4.1 full-persona twin: accuracy 0.680 vs 0.689; difference +0.009 (−0.035, +0.056) (`research_frontier/09_existing_llm_benchmark.md`, audit corrections).
- **Weak answer:** "Older people are calmer." True, but low-value for a decision.
- **Follow-up:** "Does that hold for real purchases?" (Unknown. Every outcome is hypothetical.)

---

## Part 2: Statistical validity, uncertainty, held-out evaluation (10)

### S1. "Neuroticism R² 0.17 held out. Is that big or small?"
- **Strong answer must:** at group level it is meaningful; at individual level it is small. 83% of variance is unexplained. Give the overlap statistic.
- **Evidence:**
  - Held-out R² 0.171 (`results/holdout_predictability.csv`).
  - 65+ vs 18–29: d −0.87, yet a random 65+ person is *more* neurotic than a random 18–29-year-old 25% of the time (`reports/final_audit/headline_challenge.md` §3).
  - Persona MAE gains 9–14% (`reports/memo.md` §1.3).
- **Weak answer:** "17% is good for social science." It doesn't answer what a client can do with it.
- **Follow-up:** "So should a client target individuals by age to reach anxious people?" (No. Three in four of the targeted would be no more neurotic than the median.)

### S2. "Are your confidence intervals honest?"
- **Strong answer must:** name the three weaknesses.
  1. Held-out R² intervals condition on the fitted model and are about 2–3× too narrow for green values and CRT.
  2. The repeated-CV fold-SE is a heuristic.
  3. There is no multiplicity control across 18 persona cells.
  Then say that CRT's held-out 0.02 is not a robust positive.
- **Evidence:**
  - README Figure 1 caption (refitting uncertainty 2–3× larger for green values and CRT).
  - `reports/final_audit/statistical_audit.md` Minor: "a heuristic, not an exact standard error".
  - `research_frontier/07_decision_memo.md` §2 item 3.
  - Corrected CRT CV R² 0.006 (−0.001 to 0.013).
- **Weak answer:** "They're 95% bootstrap CIs." True, but it doesn't say what they condition on.
- **Follow-up:** "Recompute one with refitting." (Training-only refit bootstrap. Never touch the test split again.)

### S3. **[DEFECT]** "Your evidence table says '+11.6% (+0.137, +0.640)'. A percentage with that CI?"
- **Strong answer must:** it's a units bug. The point estimate is a percentage; the CI is in absolute MAE units. "CI excludes 0" conclusions are unaffected because the sign is the same in both units. Give the correct reading.
- **Evidence:**
  - `reports/personas/P1_adults_65plus_evidence.md` line 49: MAE 3.45 vs 3.05 (exact values in `results/holdout_personas.csv`: 3.446 − 3.0476 = 0.398, which lies inside 0.137–0.640).
  - The same mix appears in `statistical_audit.md` ("+9.3% (CI 0.07–0.50)") and is documented in `CAUSAL_LIMITATIONS.md` §2 item 4.
- **Weak answer:** trying to interpret 0.137–0.640 as a percentage range.
- **Follow-up:** "What's the CI in percent?" (About 0.137/3.446 to 0.640/3.446, i.e. roughly 4% to 19%. Say it's back-of-envelope.)

### S4. "You looked at the holdout and then changed the scoring. Isn't the corrected holdout a second look?"
- **Strong answer must:** yes, it is a second *scoring* of the same frozen predictions. No model, criterion or threshold changed. The holdout was run once, and tests enforce byte-identity of the originals. Both versions are reported side by side, and the corrections made claims *weaker* (two CRT claims withdrawn).
- **Evidence:**
  - Holdout commit `8104628`; `results/holdout_first_run.json`; persona criteria unchanged (`statistical_audit.md` Verified item 2).
  - Original → corrected: P1 SD d +0.42 → +0.39; P1 CRT −0.18 → −0.06, withdrawn.
  - H1 (CRT predictable) was falsified and reported as such.
- **Weak answer:** "The holdout was untouched." Not quite: it was re-scored.
- **Follow-up:** "Would you have reported the correction if it had strengthened your claims?" (Yes. The SD correction did slightly strengthen R², 0.067 → 0.077, and it is reported.)

### S5. "P3 was found by searching about 1,000 groups. Winner's curse?"
- **Strong answer must:** the group-level shift did replicate (held-out −0.40, bigger than train −0.27). But it is fragile across redefinitions (3 of 6), useless for individual prediction (+0.7%), and the search inflates the training estimate.
- **Evidence:**
  - P3 card (green −0.27 → −0.40; +1% error cut; 3 of 6 redefinitions).
  - Nested training-only replication of "distinct" labels in this rehearsal: held-out d is a median **0.46×** the training d for groups of 20–29 and **0.79×** for 200+ (`D_review/cli_outputs/helper_minn.txt`).
- **Weak answer:** "It replicated, so it's real." Replicating as a group mean is not the same as being robust or useful.
- **Follow-up:** "What's the right multiplicity correction?" (A hierarchical model over all candidate groups, or simply report the selection, as the card does.)

### S6. "H6c: 80% intervals covered 70–90% in 15 of 18 cells. So the spreads are calibrated?"
- **Strong answer must:** only informative for green values, neuroticism and spendthrift. On CRT (5 values) and dictator giving (6 values) coverage is inflated by ties.
- **Evidence:**
  - `statistical_audit.md` M3: CRT p10–p90 spans 0–4, so coverage is 100% by construction.
  - P3 evidence: CRT coverage 86%/100%; SD 99%/100%.
  - In 8 unseen groups, continuous-construct coverage was 0.67–0.89 (`B_unseen/PERSONA_STRESS_TEST.md` §3).
- **Weak answer:** "15/18 within range, H6c supported."
- **Follow-up:** "What would you report instead?" (PIT histograms or coverage on continuous constructs only.)

### S7. "Why does your 'Typical' value sit outside its own confidence interval, next to a 'distinct' label?"
- **Strong answer must:** two different estimands are on the page. "Typical" is the shrunken mean; the CI and label come from the raw mean. When shrinkage is heavy, the label overstates. The shrink weight isn't shown in markdown. For dictator giving, τ² = 0, so Typical always equals the population mean.
- **Evidence:**
  - Unseen group G08 (65+, income < $30k): CRT `2.40 | 1.57–2.38 | … −0.39 … distinct`, w = 0.04 (`PERSONA_STRESS_TEST.md` §4.2).
  - `statistical_audit.md` M2.
  - Proposed fix (label on the shrunken estimate) checked training-only: 3 of 3 kept labels replicated vs 5 of 8 under the current rule. Too few to prove anything.
- **Weak answer:** "The footnote explains it." It explains it, but doesn't prevent the misreading.
- **Follow-up:** "Fix it in one line." (Require |Typical − pop|/SD ≥ 0.20 as well, and print w.)

### S8. "Persona behaviour on the holdout: how many people per cell?"
- **Strong answer must:** 6–19 for P2/P3. Rates swing ±20 points. Persona Brier scores tied or lost. No behavioural forecast survives.
- **Evidence:**
  - P3 test cells: 7 and 6 (`reports/personas/P3_young_never_married_evidence.md`).
  - P2 grey default: 19 on test.
  - Memo §1.3: "Behavioural predictions from personas did not beat the population rate".
- **Weak answer:** quoting the P1 green-default 55% as a persona finding.
- **Follow-up:** "What n would you need?" (For ±10 points at p ≈ 0.5, about 96 per cell (1.96²·0.25/0.1²), i.e. about 200 per persona across two arms.)

### S9. "Mega-Study participants are older than the panel. Doesn't that bias your choice results?"
- **Strong answer must:** they differ in age but not in green values. Reweighting to the panel's age mix leaves the green-values OR unchanged. Then flag a small inconsistency in the memo.
- **Evidence:**
  - 65+: 21% vs 10%; green values d +0.01; OR 2.54 → 2.56; default OR 3.31 → 3.65 (`headline_challenge.md` §1).
  - **Inconsistency found in this review:** the memo says "22% are 65+ vs 10%" (`reports/memo.md` line 104), while the P1 card and the headline challenge say 21%.
- **Weak answer:** "Randomisation protects us." It protects the default effect, not representativeness.
- **Follow-up:** "And representativeness of the whole panel to the US?" (Not addressed. There is no ACS weighting.)

### S10. "Your memo says age gives 'nearly all' of social desirability's R². Check that."
- **Strong answer must:** it's about 60%, not nearly all. And adding sex and income to age actually *lowers* CV R². The full model reaches 0.062 only by adding race and marital status. *(Defect found in this review.)*
- **Evidence:**
  - `reports/final_audit/headline_challenge/nested.csv`: SD age only 0.0376; full Tier A 0.0624 (0.0376/0.0624 = 60%); age+sex+income 0.0317.
  - Rerun for this rehearsal: age only 0.038, Tier A minus age 0.040 (`helper` noage output, LIVE_CHALLENGES §a).
  - Neuroticism "about half" is accurate: 0.074 of 0.151.
- **Weak answer:** repeating "nearly all".
- **Follow-up:** "Then is SD's predictability age, or race and marital status?" (Age is the largest single source. Race and marital status add about 0.025, and widowed/divorced SD are +0.38/+0.26 on train: `helper_absent.txt`.)

---

## Part 3: Scoring, data provenance, reproducibility (5)

### P1. "Why should I trust your re-scoring over the dataset publishers'?"
- **Strong answer must:** each shipped score was reproduced *exactly* from a documented string-matching bug. The errors are age-dependent, which is why they matter. Originals are kept. Then admit that no independent human has checked the scoring code.
- **Evidence:**
  - Shipped scores reproduced 100% (spendthrift), 99.7% (SD) and 100% (CRT) (`statistical_audit.md` C1).
  - SD is mis-scored for 11.6% of 18–29s vs 4.3% of 65+.
  - CRT is mis-scored for about 29% of 50+ vs 14–19% of younger people.
  - `reports/ai_note.md`: "An independent human check of the scoring code … is still advisable."
- **Weak answer:** "Our item-level scoring is correct by definition."
- **Follow-up:** "Show me one mis-scored record." (CRT answer "emily" or "8.0" marked wrong; SD export "True" vs "TRUE".)

### P2. "Your CRT 'older people are less reflective' result disappeared. What else in your pipeline relies on shipped scores you didn't verify?"
- **Strong answer must:** all six scales are now re-derived. Green values, neuroticism and dictator giving match 100%. The CRT age decline was an artefact. CRT is still unreliable (KR-20 0.58), so it shouldn't be compared across groups at all.
- **Evidence:**
  - Corrected CRT means by band: 2.38, 2.45, 2.43, 2.35 (`statistical_audit.md`).
  - Reliability: green α 0.93, neuroticism 0.90, SD 0.81, spendthrift 0.81 (`reliability.csv`).
  - The unseen-group CLI still resurrects CRT-age patterns in small cells (G08 CRT −0.39 "distinct", n = 40) (`PERSONA_STRESS_TEST.md`).
- **Weak answer:** "We fixed it." It ignores that the CLI can still show the withdrawn pattern.
- **Follow-up:** "Should CRT be dropped from the persona cards?" (Defensible. At minimum, label it "not comparable across groups".)

### P3. **[DEFECT]** "Type `sex=Male; sex=Female` into your generator."
- **Strong answer must:** say before running it that it's a known critical bug. `parse_criteria` keeps only the last clause (`crit[var] = lv`), exits 0, and profiles all women. Name the mitigation: read the "Outer-layer definition" line and n back before interpreting. Name the fix: reject repeated variables with exit 2.
- **Evidence:**
  - Run for this rehearsal: `x_dup_sex`, exit 0. Output reads "Outer-layer definition: sex = Female", n = 1044 (736 train / 308 held out) (`D_review/cli_outputs/x_dup_sex.md`).
  - `B_unseen/FAILURE_TAXONOMY.md` F1.
  - Realistic trigger: re-typing `age_band` when refining a request.
- **New related defect (found here):** the say/do sub-block prints a decline rate for cells of n ≥ 10, while the README says behavioural estimates need ≥ 20 per condition.
  - `cli_outputs/a_lowincome_18_49.md`: "grey_default: 64% (0.35–0.85), n=11".
  - The frozen P1 evidence prints "green_default: 29% (0.13–0.53), n=17".
- **Weak answer:** running it live and being surprised.
- **Follow-up:** "What else does the generator get wrong?" (Ties in "% other side"; CIs printed for insufficient cells; `--name` with `/` crashes and with `../` escapes `--out`; F2–F11 in `FAILURE_TAXONOMY.md`.)

### P4. "Reproduce the whole thing now."
- **Strong answer must:** a persona takes seconds. The full pipeline takes about 8–11 minutes without the download. A fresh-clone run passed 33/33 tests with 0 numeric mismatches. A single uninterrupted run *including* the download was never verified, because Hugging Face connections kept resetting.
- **Evidence:**
  - `reports/final_audit/live_review_simulation.md` §D: 33/33 tests, 10 min 50 s, 0 mismatches at rtol 1e-9.
  - CLI builds in this rehearsal: 2.3–2.7 s each (8 runs).
- **Weak answer:** "`python run_all.py` reproduces everything" (overclaims the download step).
- **Follow-up:** "Why does a byte-identity test fail on a fresh machine?" (CRLF line endings and BLAS differences at the 15th–17th digit. Tests now compare numerically.)

### P5. "What exactly is the 'choice', what licence is the data under, and is anything in the Mega-Study mislabelled?"
- **Strong answer must:** cover the scenario and its timing, the absence of incentives, the licences, and the label inversion.
  - The choice is a hypothetical vignette ($39 renewable vs $32), with no incentives (flat panel payment), about 4 months after the attitude survey.
  - The brief says CC BY 4.0; the Mega-Study card lists Apache-2.0.
  - `targeting_fairness`'s `target` label is inverted relative to the displayed text, so using it flips the sign of the effect.
- **Evidence:**
  - `SAY_DO_GAP_REASSESSMENT.md` §2 (QSF text, QSF author note on the incentive structure, 30 May 2025 vs 29 Jan–1 Feb 2025).
  - README provenance.
  - `research_frontier/overnight/OVERNIGHT_RESULTS.md` (coding from `Segment`; label inverted).
- **Weak answer:** "Participants chose a green tariff" (implies a purchase).
- **Follow-up:** "Does hypothetical bias make your green rates too high or too low?" (Typically too virtuous: Murphy et al. 2005, median hypothetical/actual WTP ≈ 1.35, so real-stakes uptake would probably be lower.)

---

## Part 4: Practical product decisions (5)

### D1. "Here's a new group: 65+ with income under $30k. Go."
- **Strong answer must** follow this order:
  1. Run the CLI.
  2. Read the definition line and n back.
  3. Note n_train 40 / n_test 17: there can be no held-out check.
  4. Distrust the three "distinct" labels (two have Typical outside the raw CI; CRT has w = 0.04).
  5. Note that neuroticism is −0.09 (−0.40, +0.22), which only *hints* that low income dampens the 65+ calm.
  6. Make no behavioural claim (cells 12/7).
- **Evidence:** `B_unseen/PERSONA_STRESS_TEST.md` §7 row 1; `VALIDITY_CRITERIA.md` T1/T2/T5/T9.
- **Weak answer:** reading the card top to bottom as findings ("poorer older people are greener, +0.45").
- **Follow-up:** "What would you need to say something firm?" (n_train ≥ 100 and n_test ≥ 40; see D4.)

### D2. "Should Brace sell census-based personas to clients?"
- **Strong answer must:** only as descriptive priors on temperament and self-presentation group means, labelled "group, not individual". Never for values or choices. Always paired with one measured domain item.
- **Evidence:**
  - Memo §1.4: shifts of 0.4–0.6 SD in group temperament, about a 10% individual error cut, "nothing usable" on values or choices.
  - Green values, spendthrift, CRT and dictator giving: R² ≤ 0.04 in every model family (`headline_challenge.md` §1).
- **Weak answer:** "Yes, with caveats" (without saying which outputs are allowed).
- **Follow-up:** "A client insists on a persona for a campaign decision. What do you put on the card?" (A "DO NOT INFER: choices" box plus the recommended measurement.)

### D3. "Why not just ask an LLM to role-play the demographic?"
- **Strong answer must:** in published GPT-4.1 twins on these same participants:
  - demographic personas added nothing over the condition-only baseline;
  - raw answers were overconfident;
  - effect sizes were off by 0.4–4× depending on the prompt;
  - distributions were compressed;
  - small groups were worse than the population mean.
  Scope: one model family, two hypothetical studies, training participants only, exploratory.
- **Evidence:**
  - `F_llm_benchmark/CALIBRATION_AND_FAILURES.md`: recalibrated demographic twin Brier 0.241 vs condition-only 0.237, difference −0.004 (−0.017, +0.009); hard answers 0.409; fairness small-group error 0.648 vs 0.364.
  - `overnight/OVERNIGHT_RESULTS.md`: human default ATE +0.217 vs persona twins +0.084 to +0.142 and empty persona +0.874; SD ratio 0.34–0.41.
  - **Do not cite** the open-weight run.
- **Weak answer:** "LLMs are biased" (no numbers), or citing the unfinished Qwen benchmark.
- **Follow-up:** "When *would* you use one?" (Direction screening of many variants before human testing; sign was right in 8/8 comparisons. Never for magnitudes or small groups; `CLIENT_RECOMMENDATIONS.md` §2.)

### D4. "Your 30-person minimum is arbitrary. What should it be?"
- **Strong answer must:** derive it. The d CI half-width is about 1.96/√n, so calling |d| = 0.20 "distinct" needs n ≈ 100. A training-only nested check shows replication improving with n and estimates shrinking less.
- **Evidence:**
  - `helper_minn.txt` (this rehearsal; 20 inner 70/30 splits of the train set). "Distinct" labels replicate (same sign, |d_val| ≥ 0.10):
    - 64.8% at inner-train n 20–29;
    - 66.4% at 30–59;
    - 69.5% at 60–99;
    - 75.0% at 100–199;
    - 75.3% at 200+.
  - Median held-out/train d ratio: 0.46 → 0.79.
  - Analytic half-widths: n = 30 → 0.36; n = 100 → 0.20.
- **Weak answer:** "30 is the central limit theorem rule of thumb."
- **Follow-up:** "Then why not 100 in the CLI?" (Recommend 100 for labels, 30–99 for "exploratory, unlabelled". Changing the frozen CLI after the holdout is a documented choice, not a silent one.)

### D5. "You have four weeks and a modest budget. What's the next study?"
- **Strong answer must:** target the biggest validity gap, which is that nothing is real behaviour. Re-contact panel members whose green values are already measured. Randomise the premium crossed with hypothetical vs incentive-compatible choice. Test whether the green-values slope shrinks with cost.
- **Evidence:**
  - `07_decision_memo.md` §6: about 1,200 re-contacts; $0/$7/$20 × hypothetical vs incentive-compatible.
  - Rationale: the H4/H5 nulls are underpowered (≈ 210 per condition, `hypotheses.md`).
- **Weak answer:** "Collect more demographics" or "run more models" (six model families already agree: `07_decision_memo.md` §7).
- **Follow-up:** "Power it." (6 cells of about 200: ±7 points per cell rate at p ≈ 0.5. Interaction tests need more; state it as an estimate.)
