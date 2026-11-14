# 08 · Visual and communication audit of the four README figures

**Scope:** `figures/fig1–fig4` and their README captions at commit `6140750`. Nothing was changed; this file only gives recommendations.

## Figure-by-figure

| Figure | Statistically valid? | Could it mislead a technical reviewer? | Fit for a founder-facing README |
|---|---|---|---|
| **Fig 1:** held-out R² by construct | Point estimates yes; they are asserted equal to the frozen or corrected result files. Intervals are **conditional on the fitted model**. They match refit uncertainty for neuroticism, but are about 2–3× too narrow for green values and CRT (`research_frontier/experiments/results/audit_interval_widths.csv`). | (a) The CRT interval "excludes zero" only because refit variability is ignored. (b) The caption calls R² a "group-level signal", but R² is an individual-level metric. The axis includes 0 and is not truncated; frozen and corrected estimates are distinguished. | Good main figure. One message, clean, zero line shown. |
| **Fig 2:** green-choice Brier change (exploratory) | Paired bootstrap of out-of-fold predictions, conditional on the fold models. Labelled exploratory and training-only; the outcome is labelled hypothetical. | (a) **The README caption says the default "adds little prediction once green values are known"**, contradicted by training-only X1: −0.014 Brier beyond green values, above the pre-set threshold. (b) Without a *default-only* row, the "All 10 + randomised default" row near zero suggests the default carries no predictive value; X1 shows default-only beats the base rate by −0.011. The Brier reference (0.249) is given in the axis label. | Useful, but the caption needs one correction. |
| **Fig 3:** persona d (training vs held-out) | Wald intervals with fixed population references. Corrected scores are used for social desirability and CRT; no estimand mixing (asserted against cards and corrected CSVs). | (a) 18 intervals with no multiplicity note. (b) The ±0.2 band is a convention, but it is labelled. (c) Training d includes persona members in the reference population, a small attenuation. The P3 fragility annotation is clear. | Somewhat dense for a 60-second read, but it carries the key "replicates on held-out people" evidence. |
| **Fig 4:** pipeline (Mermaid) | Accurately reflects the commit sequence. Spendthrift was re-scored before pre-registration, and the social-desirability/CRT audit came after the holdout. | No. | Good. **Deployment check outstanding:** validated locally with the Mermaid 10.9.1 parser plus a negative control, but not yet rendered on github.com. |

## Recommended corrections, ranked by severity
None requires a new analysis. All are caption or text edits to the README, which need your approval per the preservation rule.

1. **MAJOR (text): Figure 2 caption.** Replace "but adds little prediction once green values are known" with: "it also adds a modest amount of prediction beyond green values (ΔBrier ≈ −0.013, training-only), and on its own beats the base rate by about 0.011."
2. **MAJOR (text): Figure 1 intervals.** Add: "Intervals hold the fitted model fixed; they exclude model-refit uncertainty, which is similar for neuroticism but about 2–3× larger for the weakest constructs."
3. **MINOR (text): Figure 1 "group-level signal".** Replace with: "R² is the share of individual-level variance predicted. Predictions are demographic-cell averages, so R² = 0.17 means those averages differ meaningfully while 83% of person-to-person variation remains unexplained."
4. **MINOR (figure, optional): Figure 2.** Add "default only" and "green values + default (no demographics)" rows from X1. That makes the demographics-harm result visible, but it changes an existing figure, so approval is needed.
5. **MINOR: numbering.** README figures are numbered by reading order (1, 2 = persona file `fig3`, 3 = attitude file `fig2`, 4). Rename the files or captions in the next README edit.
6. **MINOR: Figure 3.** Add "intervals are not adjusted for 18 comparisons" to the caption.
7. **Deployment:** after the first push, confirm that the Mermaid block renders on github.com.

## Is any of this serious enough to block submission?
- **No.** Items 1–2 are factual-precision fixes of two caption sentences. The underlying numbers, frozen results and conclusions are unaffected.
- Recommended: **fix items 1–3 before submission** (about 10 minutes of editing, with approval). The rest is optional.
