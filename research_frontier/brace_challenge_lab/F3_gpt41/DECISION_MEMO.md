# Decision memo: what the GPT-4.1 persona experiment means for the outer-to-inner-layer approach

**Question.** Brace's approach goes from census-observable facts (the outer layer) to an inner-layer profile, and from there to choices. Does an LLM given that information predict a costed green-energy choice better than simple statistics, and does a narrative persona help?

**Answer, on this evidence: no.** This is one hypothetical scenario, 427 training participants in 76 demographic cells, and is exploratory.

## What we found
1. **Census facts carry almost no signal for this choice, and an LLM does not add any.**
   - A demographic logistic model ties the population rate: Brier 0.2410 vs 0.2414.
   - GPT-4.1 given the same demographics scores 0.268. That is not better, and its interval includes "slightly worse".
   - Two open-weight models did worse still.
2. **An estimated psychological profile does not rescue it.**
   - Adding the outer-layer-derived profile changed GPT-4.1's Brier by −0.009 [−0.024, +0.006].
   - The profile is built from the same demographics, so it carries no new information about the person. The LLM cannot create inner-layer information that the outer layer does not contain.
3. **Narrative framing made no difference for GPT-4.1** (Brier +0.001; confidence +0.001). In the open-weight models it raised confidence without improving accuracy. Prose personas are therefore at best neutral, and at worst a source of false certainty.
4. **LLM personas misread the situation.**
   - GPT-4.1 predicts the randomised default moves the choice by about 0.08, against a human +0.215.
   - Without a persona it ignores the default entirely.
   - It under-predicts the green choice overall (0.35 vs 0.47).
   - Its predictions track the profile's green-values number closely (r ≈ 0.77). The model over-weights the stereotype and under-weights the choice architecture.
5. **The probabilities are not decision-grade without calibration.** They come from a narrow, coarse set of values (0.15–0.85, 34 distinct), with slopes of 0.42–0.54 and a +0.2 intercept.

## Implications for Brace
- **Keep demographic personas descriptive**, for group-level temperament and self-presentation, where the submission found held-out signal. Do not use them, or LLM renderings of them, to forecast choices or effect sizes.
- **For choice questions:**
  - measure one relevant inner-layer attitude directly; in the submission, the green-values scale outperformed all demographics;
  - test the intervention itself in a small randomised study. The default effect was larger than any persona-based prediction.
- **If LLM personas are used at all, as cheap hypothesis generators:**
  - counterbalance option order;
  - calibrate against even a small human sample;
  - never present narrative personas as evidence.

## Limits
- One scenario, a hypothetical choice, and the training split only.
- Cells are small (median 5 people).
- GPT-4.1's snapshot cannot be verified behind the alias.
- The three models used different probability-extraction methods, so the cross-model differences are not a controlled comparison.

**Total LLM spend for this experiment:** $1.25 billed (OpenRouter).
