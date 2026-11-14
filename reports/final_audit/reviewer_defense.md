# Reviewer preparation

## 90-second pitch
We asked how much census-observable facts tell you about what is inside people, and about the choices they make.

On 2,058 US adults, with a split frozen before any analysis and pre-registered hypotheses, the answer depends sharply on *what* you want to know:
- Ten census-style variables explain about 15% of the variance in **neuroticism**, about half of it through **age**, and about 6–8% of **social desirability**, almost all through age.
- They explain essentially nothing about **green values, money style, reflective thinking or generosity**: 0–4%, robust to simpler, regularised and nonlinear models.
- In a hypothetical green-energy offer ($39 renewable vs $32), one measured value, green values, predicted the choice (OR ≈ 3 per SD). So did the randomised default (+25 points). Demographics did not beat the base rate.
- Our personas therefore get **group averages** right on what age can see, replicating on held-out people, but they don't predict **individuals** well or forecast choices.

The practical advice: for a client decision, one cheap inner-layer question beats any amount of demographic slicing.

We pre-registered a hypothesis that was wrong: we expected cognition to be the visible part. We also found and corrected three mis-scored public scale scores. One of those errors had manufactured an apparent age decline in reflective thinking.

## Five most important findings
1. **What the outer layer sees is mostly age.** Neuroticism R² 0.15 (holdout 0.17), with age alone at 0.074. Social desirability 0.06 (holdout 0.08). Everything else ≤ 0.04.
2. **Green values beat demographics for a costed hypothetical choice.** ΔBrier −0.035 holding the default constant. Demographics never reach a practically meaningful gain: best AUC 0.58.
3. **The say–do gap replicates.** 47% (train) and 50% (test) of the top third on green values decline the $39 renewable option when it requires switching.
4. **Personas replicate as group shifts, not as individual predictions.** Distinct traits kept their sign on the holdout and cut MAE by 9–14%. Persona-level choice rates never beat the population rate.
5. **Measurement matters.** Three of six shipped scale scores are mis-scored by string-matching bugs, and two of those in an age-related way. The CRT "decline with age" was an artefact.

## Five serious objections and answers
| Objection | Answer (evidence) |
|---|---|
| "You looked at the holdout and kept going." | It was evaluated once (`results/holdout_first_run.json`, commit `8104628`). No model, split, hypotheses or persona-definition file changed after it (`integrity_checks.json`). Everything later is training-only and labelled exploratory, and tests enforce that the holdout outputs are byte-identical. The score correction re-scores measurement; it selects nothing. |
| "'Demographics don't predict choices' is overfitting on n = 428." | Compact, strongly regularised and inner-CV-tuned models all fail the pre-set threshold (best ΔBrier −0.004, AUC 0.58; `reports/robustness/demographic_complexity/`). Reweighting the experiment sample to the panel's age mix changes nothing (green-values OR 2.54 → 2.56). |
| "It's a say–say gap; nothing was incentivised." | Agreed and stated everywhere: no Mega-Study QSF has incentives. The green item still has a stated price difference and a randomised default with a causal effect. Our claim is about attitude–costed-choice consistency, not purchasing. |
| "Your personas are one age gradient." | Largely true, and we say so. Neuroticism is the only trait stable in all 17 redefinitions. P2 and P3 share it. P3's green-values difference is fragile and concentrated in men. We chose not to force three archetypes. |
| "Why trust your scale scores over the published ones?" | Every correction reproduces the shipped score *exactly* from a documented string-matching rule on the raw export (100%, 100% and 99.7%). Corrected scores match the cleaned catalog CSV for all 2,058 people. Originals are preserved, and both versions are reported. |

## Three conclusions the data do NOT support
1. "Older people are less reflective": the corrected CRT scores show no age gradient, and CRT is unreliable (KR-20 0.58).
2. "Financially constrained young adults are less willing to pay for green energy": 27% on train, but 47% on the holdout.
3. "Being single makes young people less environmentally concerned": the gap is concentrated in men, vanishes under redefinition, and is not causally identified.

(Also unsupported: any statement about *real* purchasing, or about Americans in general rather than this online panel.)

## Demonstration: a new persona live
```bash
python src/personas.py list-levels
python src/personas.py build --name demo_midwest_women_50plus --corrected-scores --criteria "region=Midwest (ND, SD, NE, KS, MN, IA, MO, WI, IL, MI, IN, OH); sex=Female; age_band=50-64|65+"
```
The output, in `reports/generated/`, contains n (train and held out), typical value and spread, d vs population with CI, a confidence label, and the green-choice rate per default condition. Cells below 20 people per condition, or groups below 30 training members, are flagged INSUFFICIENT EVIDENCE. Prohibited variables (party without `--allow-party`, ideology, religion) are rejected with exit code 2.

Explaining a new persona is the analyst's job: the generator reports numbers and evidence labels, never narrative.

**Known oddity to pre-empt.** For dictator giving, the "Typical" value equals the population mean for every group, because no census group differs on it (τ² = 0). For a group that differs slightly, such as women (d +0.07), "Typical" can sit just outside the raw-mean CI. The two columns are different estimands, and the report says so.

## Group mean vs individual prediction vs hypothetical choice
- **Group mean:** "65+ panelists average 2.28 on neuroticism vs 3.14 for 18–29s." That is a statement about two distributions, and here it is large (d = −0.87).
- **Individual prediction:** knowing someone is 65+ cuts the error in guessing their neuroticism by about 13%. A random 65+ person is still *more* neurotic than a random 18–29-year-old a quarter of the time.
- **Hypothetical choice:** "chose the $39 renewable option in a survey scenario". It measures a stated intention under a framed price and default, not a purchase. It depends strongly on the default (causal) and on green values (correlational).

## With a larger, representative dataset we would
- Weight to ACS margins, or use a probability sample. Measure age and income finely, and add repeated waves to separate ageing, cohort and self-presentation.
- Use incentivised or observed choices (real tariffs, donations) in several domains, with randomised prices as well as defaults.
- Fit hierarchical models (persona effects as partial pooling within one population model) instead of cell means. Estimate the shrinkage prior per construct family, so no group's "typical" value falls outside its own CI.
- Add an LLM-from-demographics baseline, the comparison the brief suggests and we did not run.
