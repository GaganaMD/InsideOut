# Fresh-environment reproduction and live-review simulation

## A. Fresh clone, fresh virtual environment (Windows 11, Python 3.11.13)

| Step | Command | Result | Time |
|---|---|---|---|
| Clone | `git clone <repo> fresh` (at `7655eb5`) | ok | <5 s |
| Environment | `python -m venv .venv` and `pip install -r requirements.txt` | ok: all pinned packages from PyPI | 1 min 53 s |
| Full run, run 1 | `python run_all.py` | **FAILED in `download.py`.** All 12 Twin-2K-500 files arrived, but the optional Mega-Study `README.md` failed 8 times with `WinError 10054` (connection reset by the Hugging Face host). This is a local network problem, also seen during the original download | 11 min 46 s |
| Fix | Dataset READMEs made optional; failure message tells the user to re-run (`ffcf12c`) | — | — |
| Download resumed | `python src/download.py` | ok: all 22 data files; README warned and skipped | 1 min 33 s |
| Full run, run 2 | Second clone (at `1ff0963`) with the same raw data copied in: `python run_all.py --skip-download` | All 15 pipeline steps ran. **3 of 33 tests failed**: see below | 8 min 16 s |
| Full run, run 3 | Fresh clone at the final commit, `--skip-download` | see section D | see section D |

**What run 2 exposed, and the fixes**
1. **The "originals untouched" tests compared raw bytes.**
   - In a new environment, Windows writes CRLF, and pip's numpy/BLAS build differs from Anaconda's in the 15th–17th significant digit (e.g. OR 3.494366243461478 vs …481).
   - **Every number agrees to at least 12 significant digits.** Only the PNG rendering differs.
   - **Fix:** `tests/_committed.py` compares CSV/JSON numerically (rtol 1e-9), compares text with line endings normalised, and skips PNGs.
2. **The integrity check was out of date.** It reported a config commit after the holdout: the phase-3 interpretation rewrite.
   - **Fix:** the check now verifies that persona names and criteria are unchanged since `8104628` (they are) and lists text-only config commits separately.
3. **A committed output was stale.** `reports/sensitivity/sensitivity_party_republican.md` had not been regenerated after the report-rendering change. It is regenerated in the final commit.

**Other checks**
- No absolute local paths in tracked files (`git grep` for user-directory paths: none).
- No credentials (`git grep` for HF/OpenAI-style tokens, `api_key=` or `Bearer`: none).
- No OpenRouter key was used or committed.
- `tools/page_count.py` additionally needs pandoc and Edge or Chrome. It is optional and not part of `run_all.py`.

## B. Live-review simulation: five unseen persona requests
Run with `python tools/live_review.py` (wrapping `python src/personas.py build … --corrected-scores`). Outputs are in `live_review/`.

| # | Request | Purpose | Exit | Time | Outcome |
|---|---|---|---|---|---|
| 1 | `sex=Female` | broad group | 0 | 3.1 s | ok. n = 1,044 (736 train / 308 held out). CI widths: neuroticism 0.14, green values 0.14 |
| 2 | `region=South (…); education=College graduate/some postgrad\|Postgraduate; age_band=30-49` | several constraints | 0 | 2.5 s | ok. n = 154 (107 / 47). Every construct "not distinguishable". Green choice flagged **INSUFFICIENT** (12 and 19 per condition) |
| 3 | `employment=Unemployed; age_band=50-64` | small group | 0 | 2.4 s | ok. n = 63 (48 / 15). CIs about 4× wider (neuroticism 0.61). Green choice **INSUFFICIENT** (6 and 10) |
| 4 | `age_band=18-29; employment=Retired` | empty group | 0 | 2.3 s | **INSUFFICIENT EVIDENCE: n_train = 0 < 30**. No profile reported |
| 5 | `ideology=Very liberal` | prohibited variable | 2 | 2.3 s | Rejected: "'ideology' is not an allowed outer-layer variable". `party=…` without `--allow-party` is also rejected (`reports/robustness/persona_stability/cli_checks.csv`) |

**Quality check of the valid personas**
- Sample sizes, intervals and population baselines (population mean, population green-choice rate per condition) are reported for every construct.
- Uncertainty grows as groups shrink, and the 20-per-condition and 30-train thresholds trigger as designed.
- **Explanation quality:** the generator intentionally produces numbers and evidence labels only, with no narrative. A "why it fits" for a new group must be written by the analyst using the same observed / interpretation / speculation discipline as the submission cards.
- **Visible oddity.** In request 1, dictator giving's "Typical" (39.42, the population mean, because τ² = 0) lies just outside the raw-mean CI (39.53–42.00), with d = +0.07. The two columns are different estimands, as the report states. It is the documented M2 limitation and was left unchanged to avoid modifying the frozen method after the holdout.
- **Labelling.** "Weak difference" appears for trivially small but non-zero d in large groups (women: d +0.04 to +0.13 across several constructs). The label is defined as "CI excludes 0 but |d| < 0.20". The analyst should read d, not the label.

## C. Timing summary
- One persona request: about 2–3 s.
- Full pipeline without download: about 8 minutes, dominated by repeated cross-validation in the exploratory and robustness steps.
- Download: about 1.5 min when the network cooperates; it is resumable.

## D. Final fresh-clone verification
- **Run 3** (fresh clone at `b259541`, pip environment, `--skip-download`): 32/33 tests passed.
  - The redistribution follow-up drifted by about 1e-5 relative, because a sparse Ridge model used an iterative solver.
  - Fixed in `435e037` with dense input and an exact solver. Two report cells moved in the 3rd decimal; no conclusion changed (`statistical_audit.md`, Minor).
- **Run 4** (same fresh clone pulled to `435e037`): `python run_all.py --skip-download` → **exit 0, 33/33 tests passed, 10 min 50 s**.
  - Every tracked output in `results/`, `reports/`, `audit/` and `data/split.csv` matches the committed version numerically (rtol 1e-9): **0 mismatches**.
- **Not verified end-to-end:** a single uninterrupted `python run_all.py` that includes the download. On this network the Hugging Face host reset connections repeatedly. Download and pipeline were verified separately: the resumed download completed all 22 data files in 93 s.
