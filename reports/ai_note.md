# AI usage and verification

**Tools.** Claude (Opus 5.5) in Claude Code. It:
- planned the study;
- wrote all code in `src/` and `tests/`;
- ran the pipeline;
- drafted the hypotheses, persona interpretations, memo and this log.

Two web-fetch subagents read the dataset cards and the two arXiv papers to confirm the file structure. No OpenRouter or other LLM was used.

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

**Not verified in-session.** Three literature citations come from the model's background knowledge and were not re-read during this project:
- Roberts et al. 2006 and Soto et al. 2011 (age trends in personality);
- Rick et al. 2008 (tightwad–spendthrift scoring).

The scoring rule was nonetheless confirmed empirically against the item data. Treat the age-trend citations as pointers, not checked quotations.

**Later additions.** The same tools produced the exploratory follow-ups, the robustness analyses and the adversarial review (`reports/exploratory/`, `reports/robustness/`). They were checked the same way: numbers come from script outputs; tests check training-only data, leakage, reproducibility and that original files are unchanged; and memo figures were cross-checked against the result CSVs. Neuroticism was re-derived from its items and matched exactly.
