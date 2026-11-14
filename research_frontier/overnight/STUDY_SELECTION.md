# STUDY_SELECTION: which Mega-Study studies support the next experiment

Source: `overnight/study_audit.py` → `overnight/results/study_audit.csv`.
- Each study's survey file and response file were downloaded from the public GitHub mirror (`TianyiPeng/Twin-2K-500-Mega-Study`, Apache-2.0).
- Randomisers were parsed from the Qualtrics survey flow.
- **Reading the randomisers:**
  - "show **1** of k branches" means a genuine between-subjects condition;
  - "show **k** of k" only randomises display order and is **not** a condition.

| Study | Rows (unique IDs) | Train / test | Between-subjects condition? | Published LLM specifications (demographics / empty / full) | Usable for treatment-effect recovery |
|---|---|---|---|---|---|
| **default_eric** | 600 (600) | 428 / 172 | **Yes**: green vs grey default (1 of 2), plus organ-donor default | ✓ / ✓ / ✓ | **Yes**: binary choice, known human effect +0.22 |
| **targeting_fairness** | 357 (357) | 260 / 97 | **Yes**: broad vs female-targeted ad (`target` field, 179/178) | ✓ / ✓ / ✓ | **Yes**: single 1–9 fairness rating (`fair1`) |
| **context_effects** | 501 (501) | 362 / 139 | **Yes**: 6 groups (1 of 6) assign decoy versions (binary / attraction / compromise) across 3 products | ✓ / ✓ / ✓ | **Yes, but complex**: per-product choice shares; about 60 people per group |
| hiring_algorithms | 999 (999) | 696 / 303 | **Yes**: algorithmic vs human hiring team (502/497) | ✓ / ✓ / ✓ | Possible: outcome is 4 jobs × 8 Likert items; needs item mapping |
| accuracy_nudges | 1,003 | 686 / 317 | Yes (1 of 4, nested) | ✓ / ✓ / ✓ | Possible: many outcomes (headline ratings); complex |
| affective_priming | 1,000 | 694 / 306 | Yes (1 of 4 writing primes) | ✓ / ✓ / ✓ | Possible: requires free-text priming |
| idea_evaluation | 1,174 | 830 / 344 | Yes (1 of 3 × 1 of 2) | ✓ / ✓ / ✓ | Possible: 1,000+ looped rating columns |
| junk_fees, story_beliefs, consumer_minimalism | 400 / 251 / 200 | — | Nested randomisers | ✓ / ✓ / ✓ | Small or complex designs |
| obedient_twins | 1,009 (**1,001**) | 709 / 292 | 1-of-2 randomisers | ✓ / ✓ / ✓ | **Duplicate IDs (8)**: resolve first |
| digital_certification | 655 (**600**) | 423 / 177 | Yes | ✓ / ✓ / ✓ | **Duplicate IDs (55)**: resolve first |
| privacy, idea_generation | 1,200 / 200 | — | **No**: display-order randomisation only | ✓ / ✓ / ✓ (idea_generation has no full persona) | **No** |
| infotainment, preference_redistribution, promiscuous_donors, quantitative_intuition, recommendation_algorithms | — | — | **No randomizer in the flow** | ✓ / ✓ / ✓ (preference_redistribution has no full persona) | **No**: predictive only |

All 19 studies use `TWIN_ID`, matching our split, and every one has published demographics-only and empty-persona predictions.

## Ranking for "do LLM twins reproduce human choices and randomised effects?"
1. **default_eric.** Binary choice, clean two-arm randomisation, and a large known human effect. It is the **only study where a measured Twin disposition (green values) is directly relevant**, enabling the disposition arm. The harness is already built.
2. **targeting_fairness.** A clean two-arm design and one interpretable outcome. Its fairness judgement is a different kind of outcome (moral or attitudinal), which tests generality.
3. **context_effects.** The classic decoy effects test the "hyper-rationality" distortion directly. It is more complex: about 60 per group, and per-product estimands.

**Not selected:**
- hiring_algorithms: a good reserve, but its outcome needs mapping.
- Studies without a between-subjects condition: they cannot test effect recovery.
- Studies with duplicate IDs: until resolved.

**Data-verification items before the medium run:**
- extract the exact scenario wording and outcome coding for targeting_fairness and context_effects;
- confirm context_effects' group → version mapping from `FL_213_DO_*` columns;
- decide how to treat context_effects' practice scenario.
