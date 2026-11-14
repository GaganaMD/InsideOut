# Client decision briefs (hypothetical clients)

**Evidence base, which applies to every brief.** Twin-2K-500 (2,058 US adults, online opt-in panel) and the Mega-Study.
- Every "choice" is a **hypothetical, unincentivised survey vignette** collected about 4 months after the attitude measures.
- Numbers are frozen confirmatory (`results/`) unless they are labelled exploratory (training split only).
- Sample-size figures are rough planning arithmetic, not power analyses. They use the usual two-arm formula, n per arm ≈ 2·(1.96 + 0.84)²·p(1−p)/δ² (5% two-sided, 80% power).
- No result from the in-progress open-weight LLM run is used.

**What a "demographic persona" can and cannot carry here**
- It can move a group-level estimate of temperament or self-presentation by about 0.4–0.6 SD (`reports/memo.md` §1.4).
- It carries almost nothing about values, money style or choices. Green values, spendthrift, CRT and dictator giving all have CV R² ≤ 0.04 (`reports/final_audit/headline_challenge.md` §1).

---

## 1. Green-energy provider considering a price premium

**Situation.** A provider wants to know whether customers will accept a renewable tariff at a premium, and which customer segments to target.

**What we can reasonably predict**
- **Defaults matter a lot, causally.** In the $39 renewable vs $32 vignette (+$7/month, +22%), making renewable the default raised uptake by **+24.7 points (16.3–33.1)**. Train rates were 58% vs 36% (`results/saydo.json`; `reports/memo.md` §1.2).
  - The effect holds among the greenest respondents: **+25.8 points (10.2–39.5)**, 53% → 79% (`C_saydo/SAY_DO_GAP_REASSESSMENT.md`).
- **A short attitude scale separates likely from unlikely takers.** +1 SD of green values goes with **+19 points** (15–22; OR 2.95, 1.96–4.43).
  - Out-of-fold, adding the 6-item scale cut Brier by **−0.035 (−0.051, −0.020)** vs condition only (`D_review/cli_outputs/helper_choice.txt`, exploratory, train).

**What we cannot predict**
- **Real uptake levels.** No study paid people or charged them.
  - Hypothetical stated-preference studies tend to overstate willingness to pay. Murphy et al. (2005) report a median hypothetical/actual ratio of about 1.35 (cited in `SAY_DO_GAP_REASSESSMENT.md`).
  - So treat 58%/36% as upper-leaning.
- **Response to any premium other than $7.** Only one price was tested.
- **Which demographic segments respond.** Persona membership made choice prediction *worse* (ΔBrier +0.0036, CI +0.0017 to +0.0055). Tier A demographics were worse still (+0.0144, CI +0.0013 to +0.0275) (`helper_choice.txt`).
  - Income × attitude was null: OR 0.84 (0.52–1.35) (H5, `reports/memo.md` §2).
  - The "budget-constrained young" story failed the holdout: 27% → 47% (P2 card).

**Most important uncertainty.** The price-response curve under real money: how fast uptake falls as the premium rises, and whether the green-values gradient shrinks with cost (`research_frontier/07_decision_memo.md` §6).

**Risk of relying on demographic personas.**
- You would target by age or income, which does not predict this choice.
- You would miss the people with high green values who are spread across all segments: green values have R² ≈ 0.02 from census data.
- "Half of green people won't pay" is not a safe planning number. It ranges from 25% to 51% depending on where you draw the line (`SAY_DO_GAP_REASSESSMENT.md` §7a).

**Low-cost follow-up.**
- **Design:** a randomised price × default test inside the provider's real sign-up flow, or in an incentive-compatible survey. Use three premiums (for example $0 / $7 / $15) × two defaults, and add the 6-item green-values scale at sign-up.
- **Sample size:** at a ~40% base rate, detecting a 10-point difference between two arms needs about 2·7.84·0.24/0.01 ≈ **380 per arm**. Six cells come to about 2,300.
  - If the main question is only "does the premium cut uptake by 10+ points under the default?", two arms of about 380 suffice.

**Recommendation: TEST.**
- Rolling out an opt-out (default) renewable plan is supported in *direction*. It is causal in this vignette, and green defaults are documented in the field (`07_decision_memo.md` §3).
- But the premium level and the uptake rate must be tested with real money before pricing.
- **DO NOT INFER** segment targeting from demographics.

---

## 2. Company choosing between two marketing messages

**Situation.** A company has two messages (A vs B) and wants to know which works better, possibly for different demographic segments.

**What we can reasonably predict**
- Almost nothing message-specific. **This dataset contains no test of these messages.** The only randomised contrasts analysed are a default and a targeting manipulation.
- **One relevant caution about targeting.** In the Mega-Study `targeting_fairness` vignette, a plan targeted at women was rated **1.28 points less fair** on a 1–9 scale than a broad plan (95% CI −1.76 to −0.81; n = 260 train; `research_frontier/overnight/OVERNIGHT_RESULTS.md`).
  - That file's `target` label is inverted. The sign is correct only when coded from `Segment`.
  - Visible demographic targeting can carry a perceived-fairness cost. That is one hypothetical study; how well it generalises to this company's audience is unknown.

**What we cannot predict**
- Which message wins. Whether it wins differently by segment: subgroup slopes were undetectable even for a strong predictor (green-values slope by age, income, sex or education: all LR p ≥ 0.25, Holm p = 1.00; `SAY_DO_GAP_REASSESSMENT.md` §5).
- **Effect size from synthetic respondents.** Published GPT-4.1 twins got the direction of randomised effects right in 8 of 8 comparisons, but sizes ranged from 0.39× to 4× the human effect depending on prompt. On a rating scale they kept only 34–41% of the human spread (`OVERNIGHT_RESULTS.md` §A, §B).

**Most important uncertainty.** Whether the difference between A and B is large enough to matter. Message effects are often a few points, which needs large samples.

**Risk of relying on demographic personas.**
- Persona-based "segment X prefers message B" claims would be stories with no evidence base.
- Demographic twins produce compressed distributions and worse small-group errors than the population average: 0.648 vs 0.364 on the fairness scale (`F_llm_benchmark/CALIBRATION_AND_FAILURES.md` §5).
- Overtly demographic targeting can backfire, as in the fairness result above.

**Low-cost follow-up.**
- **Design:** a randomised A/B test on the real channel (email, ads) with a behavioural outcome (click or sign-up).
  - Optionally, LLM screening first, to drop clearly weak variants. Direction only; never to size the effect.
- **Sample size:** at a 30% base rate, a 5-point difference needs about 2·7.84·0.21/0.0025 ≈ **1,300 per arm**. A 10-point difference needs about **330 per arm**.
  - Segment-level conclusions need roughly 4× more per segment for an interaction, so plan for the overall winner unless the budget is large.

**Recommendation: DO-NOT-INFER from personas; TEST.**
- Run the A/B test.
- Do not choose a message, or a segment-specific message, from persona cards or synthetic respondents.

---

## 3. Public-interest organisation evaluating a policy communication

**Situation.** An organisation wants to know how a policy message (for example, about government help for the poor or health-care taxes) will land with different demographic groups.

**What we can reasonably predict**
- **Who already supports the policy is predictable from prior attitudes, not from demographics.**
  - Redistribution attitude (training split, exploratory, n = 833): demographics add ΔR² **+0.006 (−0.036, +0.048)**.
  - Policy support measured 5 months earlier adds **+0.34 (+0.28, +0.40)**, and a single ideology item adds about +0.38 (`reports/exploratory/redistribution/INTERPRETATION.md`).
- **Identity carries signal that census data does not.** Self-reported party triples the predictability of green values: R² 0.023 → 0.068 (`reports/memo.md` §2).

**What we cannot predict**
- **Persuasion.** No message was randomised in the redistribution survey, so the dataset says nothing about whether any communication changes views. This is attitude predicting attitude (`INTERPRETATION.md` §"What does not replicate").
- **Backlash or tails.** Synthetic respondents lose the extremes: on the fairness scale, humans gave 9 in 34% of cases and ≤ 5 in 24%; the demographic twin gave 9 in 1% and ≤ 5 in 0% (`CALIBRATION_AND_FAILURES.md` §4).

**Most important uncertainty.** Whether the message moves anyone, and whether it polarises: it might move supporters and opponents in opposite directions. Both need a randomised test that measures prior attitude.

**Risk of relying on demographic personas.**
- "Older/low-income people will support X" is not supported. Demographics predict this attitude at ΔR² ≈ 0.
- Persona-based segmentation would also hide the political-identity split that actually drives responses.
- Public-interest work is sensitive to backlash, which is exactly what personas and synthetic samples under-represent.

**Low-cost follow-up.**
- **Design:** a two-arm online survey experiment (message vs neutral control). Measure 2–3 prior-attitude or ideology items *before* exposure, and the outcome (support, or a behavioural proxy such as signing a petition) after.
- **Sample size:** for a small effect (d = 0.2), about 2·7.84/0.04 ≈ **390 per arm** without covariates.
  - A pre-measured attitude explaining about 34% of variance (the redistribution figure above) cuts that to roughly 390 × 0.66 ≈ **260 per arm**.
  - Testing whether the effect differs by prior attitude (polarisation) needs about 4× more.

**Recommendation: DO-NOT-INFER from demographic personas; TEST before launch.**
- Use prior attitude and ideology, not census demographics, as the segmentation variables, and measure them directly.
