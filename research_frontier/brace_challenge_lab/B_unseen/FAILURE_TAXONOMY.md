# Failure taxonomy: frozen persona generator (`src/personas.py build`)

Severity scale from `VALIDITY_CRITERIA.md` §6:
- **CRITICAL**: a silent wrong answer.
- **HIGH**: a misleading claim stated with unwarranted confidence.
- **MEDIUM**: a crash, an unhelpful refusal, or a display that undermines a rule.
- **LOW**: a cosmetic issue.

Evidence is in `UNSEEN_GROUP_TESTS.csv`, `supplementary_probes.csv`, `outputs/` and `logs/`.
Held-out figures are a held-out evaluation of the frozen generator.

| # | Failure class | Example (group) | What happens | Severity | Handled by generator? |
|---|---|---|---|---|---|
| F1 | **Repeated variable silently overwritten** | G24 `sex=Male; sex=Female` | `parse_criteria` keeps only the last clause (`crit[var] = lv`). Exit 0, `ok`, profile of `sex = Female` (n = 1,044). Intended n = 0 | **CRITICAL** | **No** |
| F2 | Confidence label from raw d next to a heavily shrunk "Typical" | G08 CRT `2.40 \| 1.57–2.38 \| … -0.39 … distinct` (w = 0.04); G08 green; G12 CRT (w = 0.10); G24 dictator "weak difference" (w = 0.00) | The label says *distinct*, while the headline value sits at the population mean and outside its own CI. Shrink weight is not shown in the markdown | HIGH | Partly. The footnote says the estimands differ; nothing flags the conflict |
| F3 | "% on other side of pop. median" ignores ties | Dictator giving (64% of train at the median), CRT (39%): G08 dictator prints 12%, but the split is 12% below / 72% at / 15% above | Implies most members sit on the "same side" when most are tied | HIGH (readers quote it as "X% of members …") | No |
| F4 | Insufficient behaviour cells still print a CI | G13 `green_default \| 5 \| INSUFFICIENT EVIDENCE … \| 0.57–1.00`; G14 `0.51–1.00` (n = 4) | The rate is hidden but can be inferred, which invites stories from 4–5 people | MEDIUM | Partly. The n < 20 rule is applied; the display leaks the estimate |
| F5 | Profiles that cannot be validated | G08 (n_test = 17), G14 (17); 4 *distinct* labels unverifiable | No held-out check is produced for new groups, and nothing warns when n_test < 20 | MEDIUM | No |
| F6 | Hard 30-person cliff | G11 (29) abstains; G14 (32) gets a *distinct* +0.43 | A discontinuous switch from no profile to a full profile with labels | MEDIUM | By design (documented threshold) |
| F7 | Small-group volatility hidden behind "not distinguishable" | G09 neuroticism train +0.13 → held-out +0.62 (n = 21); G07 green +0.05 → −0.48; G13 CRT −0.19 → −0.50 | "Not distinguishable" is easily read as "same as population" | MEDIUM | Partly. CIs are shown |
| F8 | Whole-population or near-whole groups | G03 (all age bands, share 1.000), G04 citizen=Yes (0.998) | A "persona" with d = 0.00 everywhere; G03 renders `nan%` | LOW | No warning |
| F9 | Strong overlap with existing personas | G08 and G18 are 100% inside P1; G17 is 85% inside P3; G19 51% in P3 | Traits re-surface as "new" findings when they are P1/P3 age traits | MEDIUM (narrative) | No |
| F10 | `--name` with a path separator crashes | X3 `probe/slash_in_name` → `FileNotFoundError` traceback, exit 1 | Crash on reasonable input | MEDIUM | No |
| F11 | `--name` with `../` writes outside `--out` | X4 wrote `B_unseen/X4_traversal_probe.json` when `--out` was `B_unseen/outputs` (moved to `outputs/escaped/`) | Path traversal (local CLI, low exposure) | LOW–MEDIUM | No |
| F12 | Strict exact-string levels | G22 `sex=female`, G23 `region=South` rejected | The correct refusal lists valid levels, but region labels embed state lists and are hard to type live | LOW (usability) | Yes (safe refusal) |
| F13 | INSUFFICIENT EVIDENCE exits 0 | G05, G06, G10, G11, G15, G16, G20 | Scripts cannot detect abstention from the exit code; it must be parsed from stdout or JSON | LOW | Partly |
| F14 | Unknown variable / Tier B / malformed syntax | G21, G25, X1, X5 | exit 2 with a clear message | — | **Yes** |
| F15 | Empty intersection / small n | G20 (n = 0), G15, G16 (14) | INSUFFICIENT EVIDENCE, no profile | — | **Yes** |
| F16 | Behaviour from tiny cells | Every group with a cell under 20 | Rate withheld, status printed; say/do withheld under 10 | — | **Yes** (except the F4 display) |

## Is any of these a CRITICAL defect for the live review?
**F1 is critical under the pre-set rule.** It is a silent wrong output: exit 0, status `ok`, and a full profile for a different group.

The realistic trigger is not `sex=Male; sex=Female`. It is a reviewer refining a request live and repeating a variable, for example
adding `age_band=30-49` to a criteria string that already contains `age_band=18-29|30-49`. The only defence in the output is the
echoed "Outer-layer definition" line. **Mitigation for the frozen submission:** always read that line and n back to the reviewer
before interpreting anything. Never put the same variable in two clauses; use `|` within one clause.

F2 and F3 are not silent: the numbers are on the page. But they produce confident-looking text that a careful analyst must
override. They matter most for small age-challenging groups (G08, G12), where they resurrect a CRT-age pattern the project withdrew.

## Classes that did NOT occur
- No crash on any of the 25 group definitions.
- No profile was produced for an empty or under-30 group.
- No Tier B or unknown variable was accepted.
- No behaviour rate was reported from a cell under 20.
- No construct missingness exists in this dataset (0 NaN across all 2,058 × 6), so missing-data handling was not exercised.
