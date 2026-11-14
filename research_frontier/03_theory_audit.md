# 03 · Theory audit of the ten frameworks

## Where the list comes from
- A repository-wide search (`git grep` for each framework name, excluding `research_frontier/`) finds **no copy of the ten-framework list** anywhere in the repository.
- The list exists only in the original planning prompt that started this project, the first conversation turn, before the repository was created. That prompt named exactly the ten candidates below, so the list here is authoritative for that origin.
- **The repository never adopted the ten frameworks.** `hypotheses.md` pre-registered H1–H6 without naming any theory. The initial plan narrowed to three ideas:
  - variance decomposition / ecological fallacy;
  - the low-cost hypothesis of attitude–behaviour consistency;
  - identity sorting.

  Only the first two left a trace in the analysis (H2–H5 and the persona caveats).

## Category mismatch
The ten items are not all the same kind of thing. They fall into four categories:
- **Behavioural mechanisms or explanatory theories** (make empirical claims about people): Theory of Planned Behavior (TPB), Prospect Theory, Social Cognitive Theory, Cognitive Dissonance, Dual-Process Theory.
- **Epistemological positions** (claims about knowledge): Hume's problem of induction, Bayesian epistemology.
- **Philosophy of science or methodology:** Popperian falsificationism, Mill's methods.
- **Philosophy of mind:** philosophical behaviourism.

Only the first group can be "supported" or "contradicted" by data. The others can only be *applied* (as method) or *invoked* (as an interpretive stance). The table keeps that distinction.

## Framework-by-framework

| Framework | Kind | Observable here | Missing | Relevant analysis | How used | Verdict on current analysis | Classification |
|---|---|---|---|---|---|---|---|
| **Theory of Planned Behavior** (Ajzen 1991) | Behavioural theory: attitude toward the behaviour, subjective norm and perceived behavioural control → intention → behaviour | A *general* environmental disposition (green values); a hypothetical choice | Attitude toward *this* behaviour, subjective norms, perceived behavioural control, a stated intention, actual behaviour | H2–H5 (`src/saydo.py`); X1 and X2 | Compatible measure only. The general attitude → specific choice link (OR ≈ 2.5–3) fits TPB's attitude path but equally fits trait models or plain consistency bias | Fails to distinguish | **PARTIALLY OPERATIONALIZED** |
| **Prospect Theory** (Kahneman & Tversky 1979) | Behavioural theory: reference dependence, loss aversion, probability weighting | Twin has loss-aversion and framing items; the default arm sets a possible reference point | A within-person contrast of willingness-to-accept vs willingness-to-pay for the tariff; usable loss-aversion scores (1,394 of 2,058 are "no switch" codes); a neutral arm | Default effect (+25 points) | Not tested. A default effect is equally explained by endorsement, inertia or effort (Jachimowicz et al. 2019) | Fails to distinguish | **CONCEPTUALLY RELEVANT** |
| **Social Cognitive Theory** (Bandura) | Behavioural theory: self-efficacy, observational learning, outcome expectancies | None | All core constructs | None | Not used | — | **NOT TESTABLE WITH CURRENT DATA** |
| **Cognitive Dissonance** (Festinger) | Behavioural theory: inconsistency drives attitude or behaviour change | Cross-sectional attitudes and choices | Induced inconsistency, a manipulation, attitude change over time | The say–do gap is *descriptive* | Not tested. A say–do gap is not evidence of dissonance | — | **NOT TESTABLE WITH CURRENT DATA** |
| **Dual-Process Theory** | Behavioural theory: intuitive vs deliberative processing | CRT-2 (KR-20 0.58) | A manipulation of processing (time pressure, load), or process measures; reliable individual differences | CRT predictability (H1) only | Using CRT is **not** a test of dual-process theory. No theoretical contrast was run (for example CRT × default susceptibility, which needs within-person data) | — | **CONCEPTUALLY RELEVANT** |
| **Hume's problem of induction** | Epistemology | — | — | The held-out split; the "panel ≠ US" caveat | Applied as a stance: held-out validation checks generalisation to unseen *people*, not to unseen *populations or times* | Not testable | **Methodology / interpretive** |
| **Popperian falsificationism** | Methodology | — | — | `hypotheses.md` lists explicit falsifiers. H1 was falsified, H3 not supported, H6d narrowly falsified | **Directly applied** as a procedure; one of the project's strengths | Applied | **Methodology (applied)** |
| **Bayesian epistemology** | Epistemology / method | — | — | Empirical-Bayes shrinkage in personas | Partially applied: shrinkage toward the population is Bayesian in spirit. No priors on hypotheses; inference is frequentist | Applied partially | **Methodology (partial)** |
| **Philosophical behaviourism** | Philosophy of mind | — | — | Hypothetical "do" outcomes | Relevant only as a warning: a scenario choice is still a verbal report, so "say–do" is "say–say" here | Not testable | **Interpretive only** |
| **Mill's methods** | Method of causal inquiry | Randomised default (method of difference); age gradients (concomitant variation) | — | Default effect; persona gradients | The randomised default is a valid method-of-difference contrast. Age gradients are concomitant variation **without** control of cohort or selection | Applied | **Methodology (partial)** |

## Minimum valid test with current data, and what would weaken each interpretation
- **TPB (attitude path).**
  - *Minimum test:* green values predicts the choice holding the default fixed. **Done** (H2; OR 2.95 on train and 3.49 on test).
  - *Weakened if* the purchase-specific items carry the whole effect. X2 says they carry *more* (ΔBrier 0.015), but attitude-only items still predict meaningfully.
  - *Rival:* any consistency or self-presentation account. Social desirability adjustment did not change the OR (2.92 shipped scores, 2.89 corrected).
- **Prospect Theory (reference dependence of the default).**
  - *Minimum test:* none with these data. A possible weak test is an interaction between individual loss aversion and default condition, but loss aversion is mostly unscorable ("no switch").
  - *Would need:* willingness-to-accept vs willingness-to-pay for green power, as in Pichert & Katsikopoulos' second experiment, or a neutral/active-choice arm.
- **Dual-Process.**
  - *Minimum test:* CRT × default interaction on the green choice (between-subjects), testing whether reflective people are less swayed by the default.
  - *Problems:* weak power (n = 428), an unreliable CRT, and a forking path after the holdout was inspected. **Not run.**
- **Low-cost hypothesis** (added; not on the original list, but the best-fitting mechanism).
  - *Minimum test:* green values × income as a cost proxy. Pre-registered as H5 and **null**, which is weak because income is a poor proxy for cost.
  - *Proper test:* vary the price premium.

## Alternative explanations for the same observations
- **Attitude predicts choice:** TPB attitude path; trait consistency; demand or consistency effects across surveys; construct overlap (X2); shared response style.
- **Default shifts choice:** endorsement (an implied recommendation), endowment or reference dependence (Prospect Theory), inertia or effort, inferred social norm.
- **Age gradients:** maturation, cohort, panel selection, age-graded self-presentation (social desirability correlates −0.44 with neuroticism).

## Bottom line
- **No behavioural theory on the list was directly tested.**
- **TPB is partially operationalised:** we have an attitude → hypothetical-choice association, which is necessary but far from sufficient.
- **Falsificationism and Mill's method of difference were genuinely *applied*,** through the pre-registered falsifiers and the randomised default. These are the project's methodological backbone and should be described as methodology, not as "theories tested".
