# Reproduction

Requires Python 3.11 and the packages in `requirements.txt`. The data is downloaded by the first pipeline step (`src/download.py`) into `data/raw/`, which is git-ignored.

```bash
pip install -r requirements.txt
```
```bash
python run_all.py
```
```bash
python -m pytest -q tests
```

Build a persona for new criteria (training data only):
```bash
python src/personas.py list-levels
```
```bash
python src/personas.py build --name my_group --criteria "age_band=65+; income=Less than $30,000"
```

## Expected results
- **`run_all.py`** took about 10 minutes on a Windows laptop, CPU only.
- **`pytest`:** 43 tests at `3f4179d`.
- **Comparing regenerated outputs** with the committed files, ignoring line endings:
  - no differences, except `reports/final_audit/integrity_checks.json`, which records the git log;
  - `results/` should be identical.

  Use `git diff --ignore-cr-at-eol --stat` on Windows.
- **Recorded fresh-clone check:** `SUBMISSION_READINESS.md` in the repository root.
- **Tests that guard the evaluation:**
  - `tests/test_pipeline.py::test_split_frozen` checks the split hash;
  - `test_persona_built_from_train_only` checks that personas use training members only.
