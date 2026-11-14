# EXPLORATORY: Interpretation of the redistribution follow-up

All figures come from `redistribution_vs_demographics.md` and `results.json` (training split only, out-of-fold).

## What replicated
- **Demographics alone carry almost nothing.**
  - Government-responsibility outcome: ΔR² +0.006 (−0.036 to +0.048).
  - Willingness-to-pay-taxes outcome: +0.012 (−0.036 to +0.057).
  - On the binary version, demographics are slightly worse than the base rate in Brier score (+0.004, CI includes 0).
  - Demographics do reduce MAE slightly (−0.03 to −0.05, CI excluding 0), but the gain is not practically meaningful.
  - This is the same pattern as green energy (+0.011, CI includes 0), now in a second domain with twice the n (833).
- **A measured attitude from a separate survey 5 months earlier adds a lot.**
  - Policy support adds ΔR² +0.34 (+0.28 to +0.40) on the primary outcome and +0.30 on the tax item. Both are stable across fold seeds.
  - On the binary scale, ΔBrier is −0.058 vs −0.033 for green, and ΔAUC is +0.20 vs +0.14.

## What does **not** replicate, and why this is not a full cross-domain replication
1. **No say–do contrast.** The green outcome was a costed choice; this outcome is a stated attitude. The comparison is "attitude predicts a later attitude", not "attitude predicts action".
2. **No experimental context.** The survey has no randomizer, so we cannot ask whether context adds information beyond psychology (green: default adds about 0.01 Brier, borderline).
3. **Construct proximity, not psychological depth.** A single ideology item does at least as well as the pre-specified policy scale:
   - primary outcome: ΔR² +0.38 vs +0.34 (difference −0.04, CI −0.11 to +0.03);
   - tax item: about equal.

   A general *value* (EQUALITY importance) adds less: +0.20 and +0.16. The gain tracks how *political* the predictor is, not how specifically psychological it is.
4. **The outcome is closer to the predictor than in the green case.** Both are policy opinions, which is why the gains are larger. A larger ΔR² here is not evidence that psychology matters more for redistribution than for energy choices.

## So what survives across both domains (exploratory)
**The robust cross-domain finding is the negative one: census-observable demographics add essentially no out-of-fold predictive value for either outcome.** A directly measured, domain-relevant attitude adds a lot in both. How much it adds depends on how close predictor and outcome are, so the size of the gain is not comparable across the two domains.

## Limitations
- Training split only (833 people). The original holdout was already inspected and was not used.
- Ridge regression with a fixed α = 1.0; an ordinal outcome treated as continuous.
- Single-item ideology; Cronbach's α for the 3-item policy scale is 0.71.
- Party was deliberately excluded. It would likely raise the "demographics" ceiling, as party did for green values (R² 0.02 → 0.07).
- Everything is self-report on an online panel.
