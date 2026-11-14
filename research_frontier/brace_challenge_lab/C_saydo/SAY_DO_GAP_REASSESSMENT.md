# Reassessing the "say–do gap" (Workstream C)

All new numbers below come from the **training split only** (n = 428 linked `default_eric` participants; GREEN reliability uses all 1,442 training participants). They are produced by `saydo_reassessment.py` (seed 20261114) and stored in `saydo_reassessment_results.json` and `saydo_reassessment_stdout.txt`. Held-out figures are quoted from the frozen `results/holdout_saydo.json` and were not recomputed. No frozen file was changed.

## Verdict

The data support two things:
- a **robust association** between stated green values and a **hypothetical, costed** supplier choice;
- a **causal default effect** that is about as large, and that is present even among the greenest respondents.

They do **not** support calling the 47–50% figure a "say–do gap" in the sense of attitude–behaviour *inconsistency*:
1. "Say" never mentioned paying a premium.
2. "Do" is a hypothetical vignette, with no stakes.
3. The 47% is a product of where the cut-off falls. It ranges from 25% to 51% depending on the cut, and the "top third" is actually the top 41%.

Measurement error does **not** explain away the declines. GREEN is highly reliable (α = 0.93), and even a generous reliability correction leaves about 34–42% of the top third declining. What remains is better described as **"most green-valued respondents do not accept a $7/month (+22%) premium plus a switch in a hypothetical scenario"**. Whether that is a gap between values and behaviour is **not identifiable** with these data.

## 1. What participants said (Twin wave 1, 29 Jan – 1 Feb 2025)

GREEN is Twin `QID235`, the six-item GREEN consumption-values scale (Haws, Winterich & Naylor 2014). Respondents were asked: "Here are a number of characteristics that may or may not apply to you. Please indicate next to each statement the extent to which you agree or disagree…" The answer scale was: Disagree strongly / Disagree a little / Neither agree nor disagree / Agree a little / Agree strongly (scored 1–5). `w1_score_GREEN` is the mean of the six items; the script verifies this exactly.

| Item | Text | Item–rest r | OR per SD for the choice (Tier A-adjusted) | AME per SD |
|---|---|---|---|---|
| 1 | It is important to me that the products I use do not harm the environment. | .83 | 2.63 | +17.7 pts |
| 2 | I consider the potential environmental impact of my actions when making many of my decisions. | .85 | 2.09 | +14.4 |
| 3 | My purchase habits are affected by my concern for our environment. | .84 | 2.28 | +15.7 |
| 4 | I am concerned about wasting the resources of our planet. | .71 | 2.06 | +14.1 |
| 5 | I would describe myself as environmentally responsible. | .76 | 1.71 | +10.9 |
| 6 | I am willing to be inconvenienced in order to take actions that are more environmentally friendly. | .78 | 3.24 | +20.1 |

On the training split, α = **0.93** (95% CI 0.92–0.93; n = 1,442), and α = 0.93 in the choice sample too. Distribution in the choice sample: skew −0.57; 6.3% sit at the ceiling of 5.0.

**Redistribution (exploratory; stated attitude only).** The outcome survey is `preference_redistribution` (`QID26` GOVT_RESPONSIBILITY), fielded 27–30 Jun 2025:
- **Wording:** "Some people think that the government in Washington should do everything possible to improve the standard of living of all poor Americans; they are at Point 1… Other people think it is not the government's responsibility, and that each person should take care of himself; they are at Point 5." The answer options are 1–5 plus "Don't know".
- **Secondary item** (`QID27` HLTHTAX): "How willing would you be to pay higher taxes to improve the level of health care for all people in the United States?" (Very willing … Very unwilling, plus Don't know/Can't choose).
- **Predictor:** Twin `QID287_4/5/10` (Medicare for All; public option; a 2% tax on assets above $50M), each rated Strongly oppose … Strongly support.
- **What this is:** attitude predicting attitude. There is no choice, cost or randomisation. The existing `reports/exploratory/redistribution/INTERPRETATION.md` already says so correctly, and nothing in it is a say–do test.

## 2. What participants chose (Mega-Study `default_eric`, fielded 30 May 2025)

Source: `survey.qsf` (`QID539` OPTIN_Green, `QID554` OPTOUT_Green). The common opening reads:

> "Imagine you have to relocate to another town. After you move into your new flat, you receive a letter from the electric power supplier, [X]. You are told that by moving into your new flat you became an [X] customer…"

- **Grey default (OPTIN_Green):**
  - Twon: "We offer low-priced electricity tariffs—you cannot beat our prices. Save money with Twon! Your monthly premium is $32".
  - A later flyer from GreenGrid: "GreenGrid sells clean electricity, generated from renewable energy sources. Contribute to climate protection and environmental protection! Your monthly premium will be $39."
  - Question: "What do you do?" Options: **1 = Stay with Twon / 2 = Switch to GreenGrid**.
- **Green default (OPTOUT_Green):** the same text with the roles swapped (GreenGrid at $39 is the incumbent; the Twon flyer offers $32). Options: **1 = Stay with GreenGrid / 2 = Switch to Twon**.
- **Coding:** `src/audit.py` codes chose_green = OPTOUT 1 or OPTIN 2. I checked this against the QSF and it is correct.
- **What the choice costs:** renewable costs +$7/month (+22%, about $84/yr). In both arms, the non-default option also requires a "switch".

**Other block in the same survey: organ donation.**
- **Items:** `QID614` OPTIN_Organ and `QID616` OPTOUT_Organ: "In this state every person is considered [not] to be an organ donor unless they choose [not] to be."
- **Different instruction:** only the organ item says "Please read and respond as you would if you were actually presented this choice today. We are interested in your honest response." The green item has no such realism instruction.
- **Flow:** a top-level BlockRandomizer (FL_344) picks green→organ or organ→green with even presentation (299 vs 301). Within each, the green and organ conditions are randomised independently.

**Contamination checks (train):**
- Order × green default: OR 1.76, p = 0.19. The default effect looks larger when the green item comes first (62% vs 35%) than second (53% vs 37%), but this is not detectable at this n.
- Organ condition × green default: OR 1.61, p = 0.27.
- GREEN × order: OR 1.17, p = 0.51.
- No detectable spillover, but the test has low power. Every respondent saw **two** default vignettes, so carry-over sensitisation to defaults cannot be ruled out.

**Incentives.** None. The QSF information sheet says only: "If you complete or formally withdraw from the study, you will be compensated by the panel once the project is completed". This is a flat panel payment. There is no lottery, no bonus and no consequential choice. A QSF author note even reads "We need to figure out how to explain incentive structure". Choices are **hypothetical**.

**Provenance of the scenario.** The vignette structure (a move, an incumbent supplier, a flyer from a green competitor, a price premium) matches descriptions of the green-default electricity experiments in Pichert & Katsikopoulos (2008). I did not see the original text, so "adapted from" is plausible but unverified. They reported that defaults shift green-electricity choice; secondary sources summarise roughly 68% vs 41%. That summary is unverified against the full text.

**Time gap.** Twin wave 1 ran 29 Jan – 1 Feb 2025 and the Mega-Study on 30 May 2025: about **4 months** between "say" and "do".

## 3. Attitudes and choice after Tier A adjustment (train, n = 428)

Model: logit(chose_green) ~ GREEN_z + green_default + Tier A. Sparse levels were collapsed: Pacific→West, <HS→HS, Separated→Divorced, Student/Home-maker→Other. Citizenship was dropped because there is 1 non-citizen.

| Quantity | Estimate (95% bootstrap CI, B = 1000) | Frozen unadjusted (`results/saydo.json`) |
|---|---|---|
| AME, +1 SD GREEN (associational) | **+18.0 pts** (14.0–21.7); OR 2.80 | +18.8 (15.3–22.0) |
| AME, green default (causal, randomised) | **+22.7 pts** (13.3–31.9) | +24.7 (16.3–33.1) |

Tier A adjustment barely moves the GREEN association (+18.2 unadjusted in the same specification). Demographics do not confound it much, though unmeasured confounders such as party, identity or income volatility remain possible.

## 4. Does the default change the attitude–choice relationship? (H4)

| Quantity (Tier A-adjusted) | Estimate (95% CI) |
|---|---|
| GREEN AME, grey default | +21.0 pts (15.0–26.5) |
| GREEN AME, green default | +15.8 pts (11.1–20.6) |
| **Difference (probability scale)** | **−5.3 pts (−11.9 to +1.9)** |
| Interaction OR | 0.77 (0.39–1.43) |
| Linear probability model interaction (HC3) | −1.7 pts (−10.0 to +6.5) |
| Default effect at −1 SD GREEN | +25.1 (11.8–37.9) |
| Default effect at +1 SD GREEN | +19.2 (6.0–33.5) |

The direction is consistent with H4: attitudes matter a bit more when acting means switching. The interval includes zero on both the probability and odds scales, so **H4 remains inconclusive**, as the memo says. Part of the probability-scale difference is mechanical: under the green default, high-GREEN people are already near the ceiling. The frozen test-only refit (OR 0.41) is a separate, noisier estimate and should not be pooled informally.

## 5. Subgroup differences in the GREEN slope (Tier A-adjusted; B = 500)

| Split | AME per SD by level (95% CI; n) | LR test p | Holm p |
|---|---|---|---|
| Age | 18–29: +20.6 (9.1–31.7; 48) · 30–49: +16.2 (9.0–22.3; 143) · 50–64: +18.1 (12.4–23.1; 148) · 65+: +18.4 (8.8–27.8; 89) | 0.88 | 1.00 |
| Income | ≥$50k: +18.8 (13.6–23.9; 255) · <$50k: +16.6 (9.7–23.4; 173) | 0.45 | 1.00 |
| Sex | Female: +16.8 (11.7–21.5; 199) · Male: +19.3 (12.7–25.1; 229) | 0.81 | 1.00 |
| Education | No BA: +16.7 (10.2–22.5; 210) · BA+: +19.0 (14.5–23.6; 218) | 0.25 | 1.00 |

**No credible subgroup differences.** The tests are underpowered: with 48 people aged 18–29, a slope difference of under ±15 points cannot be ruled out. These should not be reported as "the attitude works equally in all groups"; they are simply not detectable at this n. This is consistent with the null H5.

## 6. Overlap between items and outcome

- **Content.** Items 3 ("purchase habits") and 6 ("willing to be inconvenienced") are the closest to the outcome, and item 6 has the largest OR (3.24). None of the items mention price or paying more. The scale measures *values*, not a stated willingness to pay $7/month.
- **Dropping the two behavioural items.** A 4-item scale (items 1, 2, 4, 5) still gives an AME of **+16.4 pts (12.2–20.5)**. The association is not an artefact of near-duplicate wording.
- **A different item type.** Twin `QID287_3` (support for "Federal investments to ensure a carbon-pollution free electricity sector by 2035"; r = 0.61 with GREEN) gives AME +15.8 pts per SD (OR 2.30).
- **Timing.** The measures are about 4 months apart and come from different surveys and panels, so same-session priming is not the explanation. Shared method variance (self-report vs self-report vignette) remains.

## 7. True gap, or a measurement artefact?

**(a) Where the cut-off falls drives the headline number** (grey-default arm; Wilson 95% CIs):

| "High green" definition | Share of sample | Decline under grey default | Decline under green default |
|---|---|---|---|
| Above median (≥ 3.67) | 55% | 51% (42–60), n = 118 | 26% |
| **Frozen "top third" (≥ 4.0)** | **41%** | **47% (37–58), n = 87** | 21% |
| All six items ≥ 4 ("agree" on every item) | 35% | 46% (35–57), n = 74 | 23% |
| Top 20% (≥ 4.5) | 21% | 40% (28–55), n = 47 | 16% |
| Top 10% (≥ 4.83) | 10% | 29% (15–49), n = 24 | 15% |
| GREEN = 5 (strongly agree on all items) | 6% | 25% (10–49), n = 16 | 0% (0–26), n = 11 |

The decline rate falls steadily as the bar for "green" rises. The memo's "top third" is in fact the top **41%**, because 39 people are tied at exactly 4.0 and the cut uses ≥.

**(b) Reliability and attenuation.**
- α = 0.93, so item-sampling error is small.
- The bound is computed for the grey-default arm with a probit model, under classical error and a normal latent attitude.
- Decline share among the top third of the *true* attitude:
  - r = 1: 41.7% (32–52)
  - r = 0.89: 40.1% (30–51)
  - r = 0.80: 38.6% (28–50)
  - r = 0.70: 36.4% (25–48)
  - r = 0.60: 33.6% (21–47)
- r < α stands in for occasion-specific error over the 4-month gap. GREEN has **no retest** in Twin, so true stability is not identified.
- **Conclusion:** even with perfectly measured attitudes, roughly a third or more of the greenest third would decline (point estimates 34–42%). Unreliability does not explain the declines.
- The bound is model-dependent: GREEN is skewed and bounded, not normal.

**(c) Why it is still not a demonstrated "gap":**
1. The "say" item never claimed willingness to pay a 22% premium. Declining is not *inconsistent* with agreeing to "I am concerned about wasting resources".
2. The choice is hypothetical. Hypothetical bias usually *inflates* virtuous choices: Murphy et al. (2005) report a median hypothetical/actual WTP ratio of about 1.35. A real-stakes version would probably show *more* declining, so this direction of bias does not rescue the "gap" framing as a size estimate.
3. Status-quo friction. Under the grey default, choosing green requires switching. That the default moves the greenest group by +26 points (below) shows declining is partly inertia, not a value judgement.
4. Self-reported green attitudes and behaviour are related but far from identical in the wider literature (Kormos & Gifford 2014: self-report vs objective behaviour, r ≈ .46). That literature concerns self-reported *behaviour*, so it is offered only as context.

## SUPPORTED finding (with evidence)

**A randomised green default raises renewable choice substantially, including among the greenest respondents.**
- Among the frozen "top third" (GREEN ≥ 4; n = 176), the default raises the renewable choice rate by **+25.8 points (10.2–39.5)**: 53% under grey vs 79% under green.
- Across the full sample, Tier A-adjusted: +22.7 pts (13.3–31.9). This is consistent with the frozen +24.7 and the frozen holdout (decline among top-third 50% grey vs 14% green; n = 46 / 29).
- Because the default was randomised (QSF BlockRandomizer, even presentation, 300/300), this is a **causal** effect of choice architecture on the hypothetical choice. It holds whatever caveats apply to GREEN.

## TEMPTING BUT UNSUPPORTED interpretation (with evidence)

**"Half of the people who say they are green do not act on it. A stable 47–50% say–do gap shows that green attitudes are largely cheap talk."**

This fails on five counts:
1. **The number depends on the threshold.** Decline is 51% above the median, 47% in the top 41% (labelled "top third"), 29% in the top 10%, and 25% among those strongly agreeing on every item (§7a).
2. **No inconsistency is defined.** No GREEN item mentions paying more; none implies $39 over $32 (§1, §6).
3. **"Do" is a hypothetical, unincentivised vignette** with no realism instruction (§2), so it measures stated choice, not behaviour.
4. **"Replicates" rests on n = 87 and n = 46.** Train 47% (37–58) vs test 50% (36–64): overlapping CIs about 25 points wide establish consistency, not a "stable feature of the population".
5. **Calling the attitude effect "translation"** (attitudes causing choices) has no identification strategy. GREEN is associational. Only the default is causal.

## Defects and overclaims in the frozen memo (`reports/memo.md`)

1. **§1, conclusion 2:** "Values do predict the hypothetical green choice, and that gap is a stable feature of the population." The second clause is an overclaim (see above), and "that gap" has no referent in the sentence.
2. **§1, conclusion 2, third bullet:** "The **say–do gap** is substantial and replicates. Among people in the top third on green values, **47%** … and **50%** …".
   - "Top third" is actually the top **41%** on train (≥ 4.0 with ties, `src/saydo.py`: `tr.green >= tr.green.quantile(2/3)`). On test, the same train cut-off captures 75/172 = 44%.
   - No CIs are given.
   - The "say–do" label is not justified by item content.
3. **§5, "Next" item 4:** "Ask the client for **one** cheap inner-layer item, a 6-item green-values scale." This is internally inconsistent: one item versus six. It also implies the scale would transfer to a real purchase, which is untested.
4. **§6:** "The default itself added a borderline ~0.01". This is a predictive Brier increment. Read next to the causal +25-point effect, it could be mistaken for "the default barely matters"; the two quantities answer different questions.
5. **Not a defect:** H4 is correctly reported as inconclusive; the redistribution analysis is correctly flagged as "not a say–do test"; §5 states "Everything is hypothetical".

## References (located; URLs/DOIs checked via search, full texts not read)

- Pichert, D., & Katsikopoulos, K. V. (2008). Green defaults: Information presentation and pro-environmental behaviour. *Journal of Environmental Psychology*, 28, 63–73. doi:10.1016/j.jenvp.2007.09.004. https://eprints.soton.ac.uk/415446/
- Haws, K. L., Winterich, K. P., & Naylor, R. W. (2014). Seeing the world through GREEN-tinted glasses. *Journal of Consumer Psychology*, 24(3), 336–354. doi:10.1016/j.jcps.2013.11.002. https://pure.psu.edu/en/publications/seeing-the-world-through-green-tinted-glasses-green-consumption-v/
- Murphy, J. J., Allen, P. G., Stevens, T. H., & Weatherhead, D. (2005). A meta-analysis of hypothetical bias in stated preference valuation. *Environmental & Resource Economics*, 30(3), 313–325. doi:10.1007/s10640-004-3332-z. https://ideas.repec.org/a/kap/enreec/v30y2005i3p313-325.html
- Kormos, C., & Gifford, R. (2014). The validity of self-report measures of proenvironmental behavior: A meta-analytic review. *Journal of Environmental Psychology*, 40, 359–371. doi:10.1016/j.jenvp.2014.09.003. https://eepro.naaee.org/research/eeresearch/validity-self-report-measures-pro-environmental-behavior

## Limitations of this reassessment

- n = 428, with no new held-out evaluation.
- Some bootstrap resamples of the Tier A models raised non-convergence warnings. Estimates were retained, and percentile CIs were stable relative to a smoke test.
- The reliability grid (0.89–0.60) is assumed, not estimated. The fitted α is 0.93, and r = 1 is also shown.
- Subgroup analyses used B = 500.
