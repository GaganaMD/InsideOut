# Data audit (hour 1)

Regenerate: `python -I src/download.py && python -I src/audit.py`. Everything below is from files in `audit/`
or was read directly from the raw files. File hashes are in `sources.json`.

## Sources
| Dataset | Hub repo | Files used (under `data/raw/<repo>/`) |
|---|---|---|
| Twin-2K-500 | `LLM-Digital-Twin/Twin-2K-500` | `question_catalog_and_human_response_csv/{question_catalog.json, wave1_3_response[_label].csv, wave4_response[_label].csv}`, `raw_data/wave {1,2,3} scores.csv`, `raw_data/wave_1_*_anonymized.csv` |
| Mega-Study | `LLM-Digital-Twin/Twin-2K-500-Mega-Study` | `.dat/{default_eric,preference_redistribution,context_effects}/raw_data/{response.csv,survey.qsf}`, `data/<study>-00000-of-00001.parquet` |

## IDs and joins
- Twin: `pid` (int 1–2058) in the response CSVs; `TWIN_ID` in the score files. These are the same 2,058 unique IDs.
- Mega-Study raw `response.csv`: `TWIN_ID` (int). Parquet: `PID` stored as `"pid_<n>"`. The two ID sets match for all three studies.
- Qualtrics CSVs have two header rows: row 0 is the question text, row 1 is the ImportId. Data starts at row 2.

| Study | Rows | Missing ID | Found in Twin | Train | Test | All finished |
|---|---|---|---|---|---|---|
| default_eric | 600 | 0 | 600 | 428 | 172 | yes |
| preference_redistribution | 1198 | 0 | 1198 | 841 | 357 | yes |
| context_effects | 501 | 0 | 501 | 362 | 139 | yes |

## Missingness
- Outer layer (14 demographic items): 0 missing. No values fall outside the catalog's options.
- Scores: 54 score columns, 0 missing, except `w2_score_forwardflow` (1 missing).
- Four scores are partly non-numeric and are excluded for now:

  | Score | Non-numeric |
  |---|---|
  | `w2_score_discount` | 191, plus implausible values up to 4.5e15 |
  | `w2_score_presentbias` | 192 |
  | `w2_score_riskaversion` | 233 |
  | `w2_score_lossaversion` | 1,394 "no switch" |

## Scale scores: already available
`raw_data/wave N scores.csv` holds validated, pre-scored constructs (full list in `scores_dictionary.csv`):
- Big Five, need for cognition, agency/communion, minimalism, BES, GREEN, cognitive tests, CRT, ultimatum (wave 1);
- social desirability, a second conscientiousness measure on a 0–8 scale, anxiety, HI/VI/HC/VC, financial literacy, numeracy, trust game (wave 2);
- RFS, ST-TW, depression, CNFU-S, self-monitoring, SCC, need for closure, maximization, Wason, dictator (wave 3).

Not verified: the scoring rules and reverse-keying behind these files, and the direction of ST-TW. Both are needed before interpreting signs.

## Outer layer (`variable_map_outer.csv`)
- **Tier A (census-observable):**
  - region (5 regions; Census West is split into West and Pacific)
  - sex
  - age (**4 bands only: 18–29 / 30–49 / 50–64 / 65+**)
  - education (6 levels)
  - race (5 categories)
  - citizenship
  - marital status
  - income (5 bands; sample median band $50–75k)
  - household size
  - employment
- **Tier B (party, QID20):** self-identified party, not registration. Always reported with an ablation that drops it.
- **Dropped:**
  - religion: not asked by the census;
  - religious attendance: behavioural self-report;
  - ideology: attitudinal, i.e. inner layer.

## Experiments: what the "do" actually is
**No incentives anywhere.**
- The Mega-Study QSFs contain no bonus, lottery or real-money language. The redistribution study states a fixed $2 fee. The only "incentive" match is a designer's internal note.
- The Twin economic games are framed hypothetically ("Suppose you were given $5…").

Every "do" is therefore a **hypothetical scenario choice**.

**default_eric**
- Between-subject manipulation of the default. Each participant answered one green-energy item and one organ-donation item.
- Green energy is the brief's "$39 GreenGrid (renewable) vs $32 Twon" choice:
  - `OPTOUT_Green`: green is the default; 1 = stay with GreenGrid.
  - `OPTIN_Green`: grey is the default; 2 = switch to GreenGrid.
- Share choosing green, by default condition:

  | Default | Train | Test |
  |---|---|---|
  | Green default | 0.577 (n = 222) | 0.692 (n = 78) |
  | Grey default | 0.359 (n = 206) | 0.362 (n = 94) |

**preference_redistribution**
- No manipulation. 1,198 participants answered GSS/ANES-style attitude items: `GOVT_RESPONSIBILITY` (1–5, plus 6 = don't know), `HLTHTAX`, `GETAHEAD`, `FAIR`, `IMMJOBS_GSS`, `AFFRMACT_GSS`, `PRES20_GSS`.
- One attention-check failure.
- These are stated attitudes, not behaviour.

**context_effects**
- Attraction and compromise decoys across TV, phone and printer scenarios, about 167 people per scenario cell.
- Hypothetical purchase choices. This is a bias-susceptibility task, not a say–do test.

## Selection into the Mega-Study (`selection_by_study.csv`)
Participants are older than non-participants:

| Study | 65+ among participants | 65+ among non-participants | 18–29 among participants | 18–29 among non-participants |
|---|---|---|---|---|
| default_eric | 22% | 10% | 11% | 22% |

The same pattern holds in the other two studies. Results from the experiments over-represent older people.

## Persona feasibility (`persona_feasibility.csv`)
| Candidate | n | Train / test | n in default_eric (train / test) |
|---|---|---|---|
| 65+ and retired | 143 | 98 / 45 | 51 / 25 |
| 18–29, college, income < $50k | 51 | 37 / 14 | **3 / 1: infeasible** |
| 18–49, college, income < $50k | 143 | 95 / 48 | 20 / 10 |
| Republican (Tier B) | 540 | 387 / 153 | 123 / 43 |
| Non-college men 50+, South/Midwest (Tier A alternative) | 102 | 75 / 27 | 33 / 10 |

Ad-hoc counts, not saved to `persona_feasibility.csv`:

| Group | n | n in default_eric |
|---|---|---|
| 65+ (any employment) | 277 | 132 |
| 18–49, income < $50k | 425 | 98 |
| Democrat | 847 | 250 |

## Split (`data/split.csv`)
- 70/30 participant-level split, stratified on age band × college/no college. Seed 20261114.
- 1,442 train / 616 test.
- sha256 `8ef47da0…5dbe5f`. Re-running `audit.py` refuses to overwrite a split that differs.
- Built from pid and outer-layer strata only.
- Disclosure: the green-choice rates by condition and split above were printed during the audit. No attitude–outcome relationship has been examined yet.
