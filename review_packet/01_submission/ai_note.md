# AI usage and verification

**Tools.** Claude (Opus 5.5) in Claude Code. It:
- planned the study;
- wrote all code in `src/` and `tests/`;
- ran the pipeline;
- drafted the hypotheses, persona interpretations, memo and this log.

Two web-fetch subagents read the dataset cards and the two arXiv papers to confirm the file structure. **No LLM was used to produce any number in the submission** (memo, personas, `results/`). LLM *simulations* appear only in the separate post-submission research folder `research_frontier/`; see the last section.

**How the work was checked**
- **Numbers.** Every figure in the reports is produced by the pipeline (`results/`, `reports/personas/*.json`). Prose numbers were copied from those outputs, and `python run_all.py` regenerates all of them.
- **Data claims.**
  - Column names, codings and option labels were read from `question_catalog.json`, the raw Qualtrics CSVs and the QSFs. None were inferred.
  - The GREEN score was reproduced from its items.
  - The ST-TW score was reproduced, which exposed the shipped scoring bug. A test now locks the corrected direction.
- **Leakage controls.**
  - The split was frozen and hashed before any analysis.
  - The hypotheses were committed before modelling (`2540e2c`).
  - The holdout script was committed before its first run (`8104628`).
  - A test checks that personas are built from training members only.
- **Behaviour of the generator.** Tests cover the whitelist rejecting party, ideology and unknown levels, and INSUFFICIENT EVIDENCE for tiny groups.

**References.** Bibliographic details were checked by web search during the final audit. Only the abstracts or catalogue records were read, not the full texts.

| Reference | Status |
|---|---|
| Roberts, Walton & Viechtbauer (2006), *Psychological Bulletin* 132(1), 1–25 | Verified. Note: a meta-analysis of *longitudinal* studies |
| Rick, Cryder & Loewenstein (2008), *Journal of Consumer Research* 34(6), 767–782 | Verified |
| Reynolds (1982), *Journal of Clinical Psychology* 38(1), 119–125; Form C, 13 items | Verified |
| Thomson & Oppenheimer (2016), *Judgment and Decision Making* 11(1), 99–113; CRT-2 | Verified |
| Soto, John, Gosling & Potter (2011), "Age differences in personality traits from 10 to 65: Big Five domains and facets in a large cross-sectional sample", *Journal of Personality and Social Psychology* | Title, authors, year and journal agree across several secondary records (library catalogue, textbook citation, aggregators). Volume, pages and DOI appear only in secondary aggregators and could not be checked against the publisher or PubMed, so **they are deliberately omitted**. (A PubMed Central link that search results associated with this paper turned out to be a different article.) It covers ages 10–65, so not the 65+ cell |

The persona cards cite these only as "published age differences", and they no longer depend on any specific quoted figure.

**Later additions.** The same tools produced the exploratory follow-ups, the robustness analyses and the adversarial review (`reports/exploratory/`, `reports/robustness/`). They were checked the same way: numbers come from script outputs; tests check training-only data, leakage, reproducibility and that original files are unchanged; and memo figures were cross-checked against the result CSVs. Neuroticism was re-derived from its items and matched exactly.

**Final audit.** The same tools re-derived all six scales from their items. That found and exactly reproduced two more shipped scoring bugs (social desirability and CRT-2). They also:
- added opt-in corrected scoring, with the default path still reproducing the frozen results (tested);
- reran the affected analyses side by side with the originals;
- ran a fresh-clone, fresh-virtual-environment reproduction and a live-review CLI simulation (`reports/final_audit/`).

**Overnight audit, research and corrections (2026-11-14/15).** Claude, including parallel Claude subagents, audited the submission, ran exploratory research and debugged the tooling. Each change to a submitted file was approved by the author before it was made.

- **AI-generated suggestions.** Subagent reviews *proposed* these defects:
  - a repeated-criteria bug in the CLI;
  - percentage gains printed next to raw-unit CIs;
  - several overstated sentences;
  - shrinkage-inconsistent "distinct" labels;
  - median ties;
  - a behaviour-cell floor of 10 instead of 20.

  Their literature summaries and interpretations in `research_frontier/brace_challenge_lab/` are AI-written and were **not** independently verified by a human.
- **Checks actually performed before any change.**
  - **Reproduced:** each proposed defect was reproduced from code or data. For example:
    - `sex=Male; sex=Female` profiled all 1,044 women;
    - `src/holdout.py` showed that the CI was in raw units;
    - the "top third" cut was recomputed as 41% of training;
    - the "nearly all" claim was checked against `nested.csv`.
  - **Rejected when the evidence disagreed:** one suggested inconsistency (21% vs 22% aged 65+) was checked and not changed.
  - **Locked:** fixes come with regression tests.
  - **Every change logged** in `reports/final_audit/post_review_corrections.md`.
  - **Verified after the changes:**
    - `results/` and `data/split.csv` are unchanged;
    - the memo and cards still meet the page limits;
    - a fresh clone reproduces the committed outputs (`SUBMISSION_READINESS.md`).
- **Post-submission LLM research (not part of the submitted findings).** In `research_frontier/`:
  - **Published GPT-4.1 predictions:** published GPT-4.1 digital-twin predictions (Peng et al.) were compared with human data.
  - **Open-weight models on Modal:** Qwen2.5-7B and Qwen3-4B were run on Modal GPUs with pre-registered prompts. These prompts contained only k-anonymous demographic cells, public scenario text and cross-fitted aggregate profile estimates.
  - **GPT-4.1 via OpenRouter:** attempted under the same rules, with a spending cap.

  These are labelled exploratory, and none of them changed a submitted estimate.

An AI writing the analysis and also auditing it is a real limitation. The guards against it are a byte-identical regeneration check, 30+ tests and a reproduction of every reported bug from the raw exports. An independent human check of the scoring code (`src/common.py`, `src/final_audit.py`) is still advisable.
