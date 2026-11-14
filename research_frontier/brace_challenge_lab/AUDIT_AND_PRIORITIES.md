# Independent audit and prioritisation (2026-11-15)

Scales are H/M/L. **Evidence** is the strength of the evidence, **Rel.** is relevance to Brace's assignment, and **Nov.** is novelty relative to the frozen submission.

## Findings ranked

| # | Finding | Evidence | Rel. | Nov. | Status | Source |
|---|---|---|---|---|---|---|
| 1 | The outer layer sees temperament and self-presentation. It is close to blind to values, money style, reasoning and generosity (held-out R² 0.17 neuroticism, 0.08 SD, ≤ 0.02 for the rest). | H (frozen held-out) | H | — | Confirmatory | memo §1 |
| 2 | The randomised default causally shifts the hypothetical green choice: +25 points (16–33). Even among the greenest it lifts the choice from 53% to 79% (+26, 10–40). | H (randomised) | H | M | Confirmatory / exploratory subgroup | memo; `C_saydo` |
| 3 | Persona behaviour rates do not forecast. P2's "27% green" became 47% held out, and persona membership makes choice prediction worse (ΔBrier +0.004). | H | H | L | Confirmatory | memo §4; `D_review/LIVE_CHALLENGES.md` (e) |
| 4 | **LLM persona prompts are worse than free baselines.** Open-weight Qwen: every persona format has higher Brier than a demographic logistic model (+0.05 to +0.18, all CIs > 0). Published GPT-4.1 demographic twins: raw Brier 0.409 vs 0.249. | H (pre-registered; two model families; one scenario) | H | **H** | Exploratory | `F2_modal_open_weight/RESULTS.md`; `F_llm_benchmark` |
| 5 | **Narrative personas increase confidence and stereotyping with no accuracy gain.** Narrative vs numeric: \|p − 0.5\| is +0.06 and +0.09 (CIs > 0); correlation with the green z-score is 0.76 vs 0.47–0.62. | M–H | H | **H** | Exploratory | `F2` |
| 6 | **LLMs given a psychological profile lose the situational (default) effect:** +0.01 to +0.12 predicted vs +0.215 human. Published GPT-4.1 personas attenuate effects to 0.4–0.67× the human size; the empty persona inflates them 4×. | M–H | H | H | Exploratory | `F2`; `overnight/OVERNIGHT_RESULTS.md` |
| 7 | **Twins compress heterogeneity.** The fairness-rating SD is about 0.35–0.41 of the human SD (TV ≈ 0.55). | H | M | M | Exploratory | `OVERNIGHT_RESULTS.md` |
| 8 | **"Say–do gap" is not identified.** The items never mention paying more, the choice is hypothetical, and the decline share runs from 25% to 51% depending on the cut. Measurement error does not explain the declines away (alpha 0.93; 34–42% of the truly greenest would still decline). | H | H | M | Reframes memo §1 (now corrected) | `C_saydo` |
| 9 | **P2 neuroticism is half age, half income within age** (+0.24, 0.15–0.33). Lower SD in P2 is all age. P3's marital criterion adds nothing to neuroticism. | M–H | M | M | Exploratory (train) | `A_mechanisms` |
| 10 | **P1 calm survives adjustment** (−0.41 adjusted; −0.18 with employment + SD). It appears on forward- and reverse-keyed items, so acquiescence is ruled out. Maturation, cohort and selection are not separable. | M | M | M | Exploratory | `A_mechanisms` |
| 11 | Position bias in LLM survey answers is large (0.51 for Qwen2.5). | H | M | H | Methodological | `F2` |
| 12 | Mega-Study `targeting_fairness` labels its conditions backwards relative to the displayed text. | H (survey display logic) | L | H | Data-provenance | `overnight/OVERNIGHT_MODAL_PLAN.md` |
| 13 | Measured attitudes (or a twin built from them) improve choice prediction by about 12–13% of baseline; demographics do not. | H (repeated CV, train) | H | L (replicates memo §6) | Exploratory | `OVERNIGHT_RESULTS.md` |

**Null results worth stating:**
- H5: green × income.
- H4: inconclusive.
- A P3 sex difference: interaction null.
- Narrative accuracy effect: null.
- Profile vs demographics for Qwen3: null.
- Demographic models for any choice outcome: null.
- Targeting-fairness predictability beyond the condition: null.

## Critical weaknesses found in the submission

| Weakness | Severity | Status |
|---|---|---|
| Repeated-criteria bug: a silent wrong group in the live CLI | **Critical** for the live review | **Fixed** with regression tests (`0852b63`) |
| Percentage gain printed next to a raw-unit CI | Medium (a reviewer trap) | **Fixed**, rendering only |
| Overclaims: "concentrated in men", "is self-presentation", "every age band", "top third", "stable feature", "nearly all of SD's R²" | Medium | **Fixed**, wording only (`0852b63`, `5eddaf6`) |
| Behaviour block thresholds: the say/do block uses n ≥ 10, while the README says 20 | Low–medium | **Open.** Disclose it if asked. |
| "Distinct" uses the raw d, while "Typical" is the shrunk value, so the two can disagree in small groups (65+ & < $30k CRT) | Medium for the live review | **Open.** Read the shrink weight in the JSON before narrating. |
| The "% on other side of median" column ignores ties (dictator: 64% sit at the median) | Low | **Open** |

**No critical weakness remains open.**

## At most three changes before the deadline

1. **Mandatory: done.** Fix the criteria bug and add tests.
2. **Mandatory: done.** Correct the overclaims and the table units without changing any estimate. Every change is logged in `reports/final_audit/post_review_corrections.md`.
3. **Optional, recommended if time allows** (about 30 minutes; needs your approval). Make the generator abstain from "distinct" labels when the shrunk estimate's CI includes the population mean, and print the shrink weight. This removes the most likely live-review embarrassment, the 65+ low-income CRT label.

**Optional research extensions, not for the deadline:**
- the GPT-4.1 C-vs-D comparison, once there is a valid OpenRouter key;
- a second scenario for the open-weight benchmark;
- ACS reweighting.
