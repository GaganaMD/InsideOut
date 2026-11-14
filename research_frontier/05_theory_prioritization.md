# 05 · Theory prioritisation: narrowing to two behavioural mechanisms

**Conclusion up front.** **No behavioural theory can be strongly tested with the existing data.** The two mechanisms worth keeping are both about the green-choice experiment, and both need one new, inexpensive study to test properly. Methodological frameworks (falsificationism, Mill's method of difference, Bayesian shrinkage) stay as *methodology*. Philosophical positions are dropped from the "theory" framing.

## Scoring (1 = poor, 5 = strong)

| Candidate | Fit to brief | Constructs measurable now | Identification strength | Separates rivals | Literature anchor | Feasible now | Interview value | Overclaiming risk (5 = low) | Total |
|---|---|---|---|---|---|---|---|---|---|
| **A. Attitude–behaviour consistency under cost** (low-cost hypothesis, TPB attitude path; Diekmann & Preisendörfer 2003) | 5 | 3 | 2 | 3 | 5 | 2 | 5 | 4 | **29** |
| **B. Default mechanisms** (reference dependence vs endorsement vs inertia; Prospect Theory as one rival; Jachimowicz et al. 2019) | 4 | 2 (the default is randomised; mechanism measures absent) | 4 (randomisation) | 4 with new arms | 5 | 1 | 5 | 4 | **29** |
| Age-graded personality (maturity principle) | 4 | 4 | 1 (cohort confound) | 1 | 4 | 4 | 3 | 2 | 23 |
| Dual-Process (CRT as moderator) | 2 | 2 (unreliable CRT) | 2 | 2 | 3 | 2 | 2 | 2 | 17 |
| Full TPB | 3 | 1 | 2 | 2 | 4 | 1 | 3 | 3 | 19 |
| Social Cognitive Theory; Cognitive Dissonance | 1 | 0 | 0 | 0 | 3 | 0 | 1 | 1 | ≤ 6 |

Age-graded personality scores well on data availability, but it is a descriptive regularity, not a mechanism, and cohort and selection cannot be separated. **Keep it as a finding, not a theory.**

## A · Attitude–behaviour consistency under cost
- **Question.** Does a measured environmental disposition predict choosing green energy less strongly as the personal cost rises, and less in an incentivised than a hypothetical choice?
- **Hypotheses.**
  - A1: the green-values slope (log-odds per SD) falls as the premium rises ($0 → $7 → $20/month).
  - A2: the slope is smaller and the uptake level lower when the choice is incentive-compatible than when it is hypothetical.
- **Operationalisation.**
  - Predictor: green values, plus the attitude-only subscale (items 2, 4, 5) to avoid construct overlap (X2).
  - Outcome: binary tariff choice.
  - Premium: randomised.
  - Mode: randomised hypothetical vs incentivised. For example, a lottery in which 1 in N choices is implemented as a cash-equivalent donation to a green-power certificate vs a cash payment.
- **Data needed.** New: about 1,200 re-contacted Twin-2K-500 participants (green values already measured, about 5 months earlier). 3 premiums × 2 modes, crossed with the green/grey default only if budget allows.
- **Baselines.** Prevalence; default-only; demographics-only.
- **Metrics.** The slope and its interaction with premium (main estimand); out-of-sample Brier to confirm predictive relevance.
- **Falsification.** The A1 interaction CI includes 0 and lies within ±0.15 log-odds per SD per $10 (an equivalence bound), or the slope *increases* with cost.
- **Limitations.** Incentivised green choices are hard to make realistic. Re-contact attrition will be non-random.
- **What current data already show (training only).** The green-values OR ≈ 2.5 at a $7 premium. H5 (green values × income as a cost proxy) was null, which is uninformative because income is a weak proxy for cost.

## B · Why the green default works
- **Question.** Is the default effect (+25 points) driven by reference dependence and endowment, implied endorsement, or effort/inertia?
- **Hypotheses.**
  - B1 (reference dependence): willingness-to-accept to give up green power exceeds willingness-to-pay to get it, and the gap predicts staying with the green default.
  - B2 (endorsement): a disclaimer that "the supplier was assigned at random, not recommended" shrinks the default effect.
  - B3 (inertia): a one-click switch vs a form-filling switch changes the default effect.
- **Operationalisation.** A 2 (green/grey default) × 3 design: control, random-assignment disclaimer, low-effort switch. Plus a neutral active-choice arm, and willingness-to-accept / willingness-to-pay items.
- **Data needed.** New: about 300 per cell → about 2,100 participants. A pre-registered online experiment, hypothetical first.
- **Baselines.** The control default effect; the active-choice arm as a reference level, since Hedlin & Sunstein (2016) found active choice can beat a green default.
- **Metrics.** Default effect per arm, as a risk difference with CIs; willingness-to-accept/willingness-to-pay ratio and its association with staying.
- **Falsification.**
  - The disclaimer does not reduce the default effect (equivalence ±5 points), which rules out B2.
  - The willingness-to-accept/willingness-to-pay gap does not predict staying, which weakens B1.
- **Limitations.** Mechanisms can co-occur. Hypothetical stakes again.

## Dropped or merged
- **Merged:** the TPB attitude path → into A. Mill's method of difference → as the design logic of B.
- **Kept as methodology:** falsificationism (pre-registration and falsifiers); Bayesian shrinkage (persona estimates); Hume (generalisation caveat).
- **Dropped as theory claims:** Social Cognitive Theory, Cognitive Dissonance, philosophical behaviourism, Dual-Process as currently operationalised. Prospect Theory survives only as one rival inside B.
