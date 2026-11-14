# Outer layer → inner layer → choices: Twin-2K-500 personas

This is Brace's research assignment: how much census-observable facts reveal about people's psychology and their (hypothetical) choices.

**Start with** [`reports/memo.md`](reports/memo.md), then the three personas in [`reports/personas/`](reports/personas/).

## Reproduce everything

```bash
pip install -r requirements.txt
python run_all.py            # download → audit → analyses → holdout → personas → tests (≈5 min after download)
```

This needs Python 3.11 and internet access for the first download (about 50 MB from Hugging Face, `LLM-Digital-Twin/*`).

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

Output goes to `reports/generated/`. New personas are built from the training split and carry CIs, but they have **no** holdout check. Only the three submission personas were validated.

## Layout

| Path | What it holds |
|---|---|
| `src/download.py`, `src/audit.py` | Data fetch, audit tables (`audit/`), frozen split (`data/split.csv`) |
| `src/common.py` | Loaders, construct definitions, ST-TW re-scoring |
| `src/predictability.py` | Outer-layer predictability map (train CV) |
| `src/saydo.py` | Green-energy say–do models (train) |
| `src/personas.py` | Persona generator CLI, P3 selection rule |
| `src/holdout.py` | One-time evaluation on the frozen test split |
| `hypotheses.md` | Pre-registered predictions and falsifiers (committed before modelling) |
| `results/` | All numeric outputs |
| `reports/` | Memo, personas, exploration log, AI note, party sensitivity persona |
| `src/exploratory_*.py` → `reports/exploratory/` | EXPLORATORY follow-ups (train only): green values vs demographics; redistribution attitude vs demographics |
| `src/robust_*.py` → `reports/robustness/` | EXPLORATORY robustness (train only): demographic model complexity, persona stability, CLI checks, adversarial review |
| `tests/` | Integrity tests (split hash, coding, whitelist, train-only, leakage, reproducibility, originals untouched) |

## Data caveats
- Every "do" outcome is a **hypothetical** scenario choice. There are no incentives.
- Age is recorded only in 4 bands and income in 5.
- The shipped `score_ST-TW` is mis-scored for 20% of people, so we re-score it (see `audit/AUDIT.md`).
- Mega-Study participants over-represent people aged 65+.
