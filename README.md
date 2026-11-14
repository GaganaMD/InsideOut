# Outer layer → inner layer → choices: Twin-2K-500 personas

This is Brace's research assignment: how much census-observable facts reveal about people's psychology and their (hypothetical) choices.

**Read in this order** (what to submit and what is supporting or historical: [`SUBMISSION.md`](SUBMISSION.md)):
1. [`reports/memo.md`](reports/memo.md) (4 A4 pages, conclusions first).
2. The three one-page persona cards: [`P1_adults_65plus.md`](reports/personas/P1_adults_65plus.md), [`P2_under50_income_below_50k.md`](reports/personas/P2_under50_income_below_50k.md), [`P3_young_never_married.md`](reports/personas/P3_young_never_married.md). Full tables are in `*_evidence.md`.
3. [`reports/exploration_log.md`](reports/exploration_log.md) and [`reports/ai_note.md`](reports/ai_note.md).
4. [`reports/final_audit/statistical_audit.md`](reports/final_audit/statistical_audit.md): the scoring defects found in the dataset and how they were corrected.

## Reproduce everything

```bash
python -m venv .venv
source .venv/bin/activate    # Windows PowerShell: .venv\Scripts\Activate.ps1 ; Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
python run_all.py            # download → audit → analyses → holdout → personas → exploratory/audit → tests
```

- **Requirements:** Python 3.11, and internet access for the first run (about 60 MB from Hugging Face `LLM-Digital-Twin/*`; the downloader retries dropped connections).
- **Measured on a fresh clone and fresh virtual environment:** see `reports/final_audit/live_review_simulation.md` for timing.
- **`--skip-download`** reuses `data/raw/`.
- **Optional:** `tools/page_count.py` renders markdown to A4 PDF to check page limits. It needs pandoc and Edge or Chrome.

## Build a persona for a new group

```bash
python src/personas.py list-levels
python src/personas.py build --name midwest_women --criteria "region=Midwest (ND, SD, NE, KS, MN, IA, MO, WI, IL, MI, IN, OH); sex=Female"
python src/personas.py build --name grads_65 --criteria "age_band=65+; education=College graduate/some postgrad|Postgraduate"
```

**Criteria syntax:** `var=level[|level]; var2=level`.
- Only the Tier A census variables are accepted.
- `party` needs `--allow-party`, and the report is labelled as a sensitivity persona.
- Groups with fewer than 30 training members return **INSUFFICIENT EVIDENCE**.
- Behavioural estimates need at least 20 people per default condition.
- **Scoring mode:** `build` uses **corrected** item-level social-desirability and CRT scores by default. `--legacy-scores` reproduces the dataset's shipped scores, **including their known scoring defects** (180 and 450 people mis-scored), and exists only for historical reproduction. `--corrected-scores` is still accepted but does nothing extra.

Output goes to `reports/generated/`. New personas are built from the training split and carry CIs, but they have **no** holdout check. Only the three submission personas were validated.

## Layout

| Path | What it holds |
|---|---|
| `src/download.py`, `src/audit.py` | Data fetch, audit tables (`audit/`), frozen split (`data/split.csv`) |
| `src/common.py` | Loaders, construct definitions, item-level re-scoring (spendthrift; opt-in social desirability and CRT) |
| `src/predictability.py`, `src/saydo.py`, `src/holdout.py` | Frozen confirmatory analysis (train CV; one-time holdout) |
| `src/personas.py` | Persona generator CLI, P3 selection rule, persona cards |
| `hypotheses.md` | Pre-registered predictions and falsifiers (committed before modelling) |
| `results/` | Frozen numeric outputs (byte-identical since the holdout run; enforced by tests) |
| `src/exploratory_*.py` → `reports/exploratory/` | EXPLORATORY follow-ups (train only) |
| `src/robust_*.py` → `reports/robustness/` | EXPLORATORY robustness (train only) and the adversarial review |
| `src/final_audit.py`, `src/headline_challenge.py` → `reports/final_audit/` | Final audit: scale verification, corrected-score reruns, headline challenge |
| `tools/` | `live_review.py` (CLI simulation), `page_count.py` (A4 page check) |
| `tests/` | Split hash, coding, whitelist, train-only, leakage, reproducibility, originals untouched, scale verification |

## Data caveats
- Every "do" outcome is a **hypothetical** scenario choice. There are no incentives.
- Age is recorded only in 4 bands and income in 5.
- Three shipped scale scores are mis-scored by string-matching bugs: spendthrift (409 people), social desirability (180) and CRT-2 (450). Spendthrift is always re-scored; social desirability and CRT corrections are reported beside the frozen originals (`reports/final_audit/statistical_audit.md`).
- Mega-Study participants over-represent people aged 65+.
