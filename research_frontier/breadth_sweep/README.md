# Breadth sweep (exploratory; not part of the submission pipeline)

`run_all.py` does not call this, and no submitted estimate depends on it. It was added on 2026-11-15, after the holdout had been inspected, in response to an independent review. Training split only.

Regenerate from the repository root:

```bash
python research_frontier/breadth_sweep/breadth_sweep.py
```

## 1. Are the six pre-registered constructs typical? (`all_scores_r2.csv`)

Same model as `src/predictability.py` (ridge on one-hot Tier A, 5×5 repeated CV, seed 20261114), applied to every usable shipped score.

- 50 usable scores (4 excluded for non-numeric codes).
- Median CV R² 0.05; maximum 0.16.
- 11 scores reach 0.10, including crystallized intelligence (0.15), conscientiousness (0.13) and numeracy (0.11).
- Economic-game choices and green values stay near 0.

**Reading.** The six pre-registered constructs are not a representative sample of the inner layer: four of them sit in the less predictable half. The ceiling (R² of about 0.16 at most) is the general result. The memo's map of what census facts can and cannot see holds for those six constructs only.

**Limits.**
- Only the six pre-registered scores were re-derived from items, and three of those were mis-scored as shipped. Every other row is labelled `UNAUDITED shipped score` and was not independently re-scored.
- Training split only; no holdout check.
- Several rows overlap (synonym, antonym and crystallized intelligence are related scores).
- The interval column uses the same heuristic as the frozen map (fold SD / √5).

## 2. Organ donation (`organ_choice.json`)

The same participants made a second hypothetical choice in `default_eric`, about organ-donor status, which the submission does not use.

- **Coding, checked against the raw files.** `OPTOUT_Organ` option 1 is "currently a potential donor; if acceptable, click here". `OPTIN_Organ` option 2 is "change your status". Raw counts (182 of 299 and 170 of 301 across all participants) reproduce the processed donor rates of 0.609 and 0.565.
- **Result (training split, n = 428).** Adding Tier A to the randomised default condition changes out-of-fold Brier by −0.001 (95% CI −0.009 to +0.007, paired participant bootstrap). Demographics add nothing detectable.
- **Limit.** The default itself moves donation by only about 9 points on the training split, so this is a weak test. It is supporting evidence for the memo's negative result on choices, not a submitted finding.
