# Adversarial review: the five strongest criticisms Brace could raise

Each criticism is followed by the evidence for and against it and what was changed before submission.

## 1. "Your 'say–do gap' is really a say–say gap. Nobody did anything."
- **Evidence for the criticism.**
  - None of the audited Mega-Study QSFs contains incentive language. The redistribution study pays a flat $2.
  - The Twin economic games are framed "Suppose you were given $5".
  - The green "choice" is a scenario answer.
- **Response.**
  - This is stated in the audit, the memo, every persona report and the README.
  - The green outcome still differs from a plain attitude item in three ways: it names a price difference ($39 vs $32), it has a randomised default that shifts it causally (+25 points), and 47–50% of high-green-values people decline the costly option.
  - So it measures attitude-to-costed-choice consistency, not real-world purchasing.
- **Correction made.** The memo's persona table column "Behaviour" was renamed "Hypothetical green choice". Nowhere else does the text claim real behaviour.

## 2. "'Demographics predict nothing' is an artefact of overfitting about 40 dummy variables on 428 people."
- **Evidence for the criticism.** The full Tier A model was badly over-confident (calibration slope 0.25).
- **Response.** Robustness #1 (`reports/robustness/demographic_complexity/`) used the same folds and compared four demographic models:
  - a compact age + income + education model;
  - the full model;
  - a strongly regularised full model (C = 0.05);
  - an inner-CV-tuned full model.

  No variant reaches the pre-set threshold (ΔBrier ≤ −0.010 with a CI excluding 0) for either outcome:
  - Green: best ΔBrier −0.0025 (−0.0056, +0.0007), AUC 0.58. The compact model is *worse* than baseline.
  - Redistribution: the tuned model is detectable but tiny, ΔBrier −0.0042 (−0.0084, −0.0002), AUC 0.58.
- **Correction made.** The memo now says "no *practically meaningful* signal" rather than "no signal", and reports the AUC 0.58 ceiling.
- **Scope.** The negative finding applies to *values and choices*. The outer layer does predict neuroticism (holdout R² 0.17) and social desirability (0.07). The memo already says so, and the two claims must not be merged.

## 3. "P3's headline 'young never-married adults are less green' came from searching about 1,000 groups. It is a forking-paths artefact."
- **Evidence for the criticism.**
  - Robustness #2 (`reports/robustness/persona_stability/`) shows the green gap is not stable under one-criterion changes. The CI excludes 0 in only 3 of 6 variants.
  - It vanishes when the marital criterion is dropped (d −0.11) or the age band is shifted to 30–49 (d −0.09).
  - It is concentrated in men (d −0.40, CI −0.59 to −0.20). For women it is d −0.12 (CI includes 0), though that cell has only 86 people.
- **Evidence against.** P3 itself was chosen by a pre-registered rule, and the direction replicated on the untouched holdout (test d −0.40).
- **Correction made.**
  - The memo's surprise bullet now states the concentration in men and labels the finding exploratory.
  - The original persona estimates were not changed; the persona report already lists sex composition (56% male) as alternative explanation 1.
  - Brace should treat this as a hypothesis for new data, not a result.

## 4. "Your three personas are one age gradient in three costumes."
- **Evidence for the criticism.**
  - In every persona, the most stable conclusion is neuroticism. It keeps its sign and its CI excludes 0 in all 17 variants.
  - P2's social desirability difference is fragile: widening P2 to 18–64 makes it non-significant (d −0.08).
  - P2 and P3 share the high-neuroticism profile and overlap by 41%.
- **Response.**
  - This is reported as a *finding* in memo §5: "Three personas from census data are closer to two." Tier A collapses mostly onto a life-stage axis.
  - The stability analysis adds that what survives redefinition is neuroticism (all personas) and social desirability for 65+. Everything else is criterion-dependent.
  - The cross-persona contrast is real: P1 is calmer and higher in social desirability; P2 and P3 are less calm. It is also limited.
- **Correction made.** None to the estimates. The stability table is the honest qualifier and is linked from the memo.

## 5. "You looked at the holdout and then kept analysing. How do we know nothing leaked?"
- **Evidence for the criticism.** Two follow-ups and two robustness analyses came after the holdout was inspected, and the persona interpretations were written after training-set exploration.
- **Response (verifiable in git).**
  - The split hash (`8ef47da0…`) is checked by a test.
  - The hypotheses were committed before modelling (`2540e2c`). The holdout script was committed before its single first run (`8104628`), which is recorded in `results/holdout_first_run.json`.
  - Every later analysis uses the training split only. Tests assert that no test-split participant enters, that held-out-fold outcomes cannot change their own predictions, and that original results, personas and configuration files are byte-identical to their committed versions.
  - The redistribution follow-up was pre-specified before modelling (`0234938`).
  - Deviations are logged: inner CV was switched to leave-one-out for runtime, and a truncated config was amended *before* the holdout.
- **Correction made.** None needed. The follow-ups are labelled exploratory everywhere.

## Further criticisms (not top five, acknowledged)
- **Representativeness.** This is an online panel, and Mega-Study participants skew old (65+: 22% vs 10%). There is no ACS reweighting.
- **Scale scores.** 3 of 6 constructs are now verified from items: GREEN (exact), neuroticism (exact; re-derived during this review) and spendthrift (shipped score wrong, re-scored). Social desirability, CRT and dictator giving are not re-derived.
- **Randomisation imbalance** in `default_eric` (p = 0.04). The adjusted estimates are unchanged.
- **Shrinkage prior.** It is estimated from Tier A groups and over-shrinks non-Tier-A groups (party sensitivity persona, dictator giving).
- **No LLM baseline**, although the brief suggests one.
