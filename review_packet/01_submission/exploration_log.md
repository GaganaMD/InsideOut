# Exploration log

In order. ✗ = dropped, ✓ = kept, ⚠ = problem found.

1. ✓ **Downloaded the files, not the whole repos.** I pulled only the files needed from both Hugging Face repos. The Hub connection kept resetting, so `download.py` became a per-file retry loop.
2. ⚠ **Pre-computed scores were found** (`raw_data/wave N scores.csv`, keyed `TWIN_ID`, same IDs as `pid`). This saved a day of item scoring.
3. ✗ **Rejected "under-40" personas.** Age is recorded only in 4 bands, so any persona must use those bands.
4. ✗ **Dropped the original P2** (18–29 college graduates with income < $50k). It had 51 people, and only 4 of them were in the green experiment.
5. ⚠ **No incentives anywhere.** I searched the QSFs for bonus, lottery and real-money wording and found none. The redistribution study pays a fixed $2, and the Twin economic games say "Suppose you were given $5". All "do" outcomes are hypothetical.
6. ✗ **Considered and parked `preference_redistribution` and `context_effects` as say–do tests.**
   - Redistribution is stated attitudes only, with no choice and no cost.
   - Context effects is decoy susceptibility, not a say–do contrast.
   - `default_eric` was the only study with a costed choice and a randomised manipulation.
7. ✓ **Froze a stratified 70/30 split** (age band × college) before reading any inner-layer–outcome relationship. sha256 checked by a test.
8. ⚠ **GREEN check passed.** It is exactly the mean of QID235_1–6, all items pro-environment.
9. ⚠ **ST-TW is mis-scored in the shipped file** for 409 people: QID31 answers 6 and 11 are coded as 0. I re-scored it as Q31 + Q32 + (6−Q33) + (6−Q34), with higher meaning spendthrift. The direction is verified (r = 0.75 with QID31).
10. ✗ **Excluded four economic scores** (discount, present bias, risk aversion, loss aversion). Each had 191–1,394 non-numeric codes, and discount had values up to 4.5e15.
11. ✓ **Committed the hypotheses before modelling.**
12. ⚠ **Deviation from the plan.** The plan said inner 5-fold CV for ridge, but that run took over 10 minutes. I switched to efficient leave-one-out inner selection. Outer CV is unchanged.
13. ✗ **H1 falsified.** I expected CRT to be predictable and temperament not, and the opposite happened. Kept as a headline finding.
14. ⚠ **Randomisation check p = 0.043** (age and education imbalance between default arms). Adjusting for age, education and sex left the estimates unchanged, so this was added as a sensitivity analysis.
15. ✓ **P3 chosen by the pre-registered rule:** 18–29 never married. The runner-up was a race-defined group. The rule decided, not taste.
16. ✓ **Alternative-explanation checks before the holdout** (training data only):
    - Social-desirability adjustment of the 65+ neuroticism gap: −0.50 to −0.32.
    - Income within age band: +0.30 SD neuroticism.
    - Never-married vs other 18–29s on green values, adjusted: −0.45 SD.
17. ⚠ **Config write failed partway** (Windows cp1252 could not encode "−") and a truncated file was committed. I rewrote it in UTF-8 and amended the commit before the holdout. Interpretations were written before the holdout was run.
18. ✓ **Holdout evaluated once** (first-run commit recorded in `results/holdout_first_run.json`). Later pipeline runs reproduce identical numbers, and nothing was tuned after it.
19. ⚠ **Post-holdout finding: the shrinkage prior over-shrinks non-Tier-A groups** (party sensitivity persona, dictator giving). I documented it rather than fixing it, because modelling changes after the holdout would be tuning on the test set.
20. ✗ **Not done:** LLM-from-demographics baseline, ACS reweighting, hierarchical behaviour model, and use of the other 16 Mega-Study studies.
21. ✓ **Exploratory follow-up 1 (train only, after the holdout).** Measured GREEN vs demographics for the green choice. Demographics did not beat the base rate; GREEN added ΔBrier −0.035 with the default held constant.
22. ⚠ **Exploratory follow-up 2: redistribution (pre-specified in `0234938`).** The survey has no randomisation, so condition models were not applicable, and the outcome is a stated attitude, not a decision. Policy support added ΔR² +0.34. Ideology did as well, which points to construct proximity.
23. ✓ **Robustness: demographic complexity.** Compact, regularised and tuned demographic models never reach the pre-set threshold. Best result: AUC 0.58, ΔBrier −0.004.
24. ⚠ **Robustness: persona stability.** Neuroticism is stable in all 17 variants. P3's green gap is fragile and concentrated in young never-married men, so the memo was corrected. P2's social desirability is fragile.
25. ✓ **Neuroticism re-derived from BFI items** (exact match). Social desirability, CRT and dictator giving are still not re-derived.
26. ⚠ **Final audit: two more shipped scores are mis-scored.** Social desirability (180 people; 'True' vs 'TRUE') and CRT-2 (450; 'emily' or '8.0'). Both are reproduced exactly from the raw exports, and both are age-related. The CRT 'decline with age' was an artefact. P1 and P2 CRT claims were withdrawn; social-desirability conclusions hold. Originals are kept, and corrected reruns sit beside them.
27. ✓ **Headline challenge (exploratory).** Neuroticism predictability survives OLS, ridge and boosting (0.13–0.15), and about half of it is age. Values and choices stay at R² ≤ 0.04 in every model family. Reweighting the experiment to the panel's age mix leaves the green-values OR unchanged.
28. ✗ **Persona text rewritten as evidence-tiered cards** (observed / interpretation / speculation; claim ledger). The 'partnering raises green concern' story was dropped as speculation.
29. ⚠ **requirements.txt was missing six runtime packages.** Fixed and tested in a fresh virtual environment.
