# Morning brief (2026-11-15)

## What changed overnight

**The submission was corrected, with your authorization. No estimate changed.**
- **Fixes, in commits `0852b63` and `5eddaf6`:**
  - the repeated-criteria CLI bug, with 4 regression tests;
  - the mixed %/raw-unit tables;
  - seven overstated sentences.
- **Change log:** `reports/final_audit/post_review_corrections.md`.
- **Checks:** 39 submission tests pass. The memo is 4 pages and each card is 1 page.

## Confirmed (frozen held-out evidence)
- **What census facts reveal:** they predict temperament and self-presentation, mostly through age. Held-out R²: neuroticism 0.17, social desirability 0.08. They predict close to nothing for values, money style, CRT or generosity.
- **What the personas get right:**
  - The distinct traits replicated in direction.
  - Persona means cut individual error by 9–14% where a trait is distinct.
  - Persona behaviour rates failed (P2: 27% became 47%).
- **What drives the green choice:**
  - Green values predict the choice, but this is an association, not a causal effect.
  - The randomised default causes it: +25 points.

## Exploratory (training only or new tonight; label as such)
- **Default among the greenest:** even in that group, the default moves the choice from 53% to 79% (+26).
- **"Say–do gap" is not identified.** No item mentions paying a premium, the choice is hypothetical, and the decline share depends on the cut (25–51%).
- **Open-weight LLM personas (Qwen2.5-7B, Qwen3-4B), pre-registered:**
  - Every persona prompt is *worse* than a population average or a 4-variable logistic model (Brier +0.05 to +0.18).
  - Narrative wording makes predictions more confident and more stereotyped, with no accuracy gain.
  - Giving a model a psychological profile erases the default effect (+0.01 to +0.12 vs a human +0.215).
- **Published GPT-4.1 twins:** they recover the direction of effects but not their size (0.4–0.67× with personas; 4× with no persona), and they compress the spread (SD ratio about 0.35–0.41).
- **P2 neuroticism** splits evenly between age and income within age. P1's calm survives adjustment and is not acquiescence.

## Null results
- H5 (green × income).
- H4 (inconclusive).
- A sex difference in P3's green gap.
- Narrative vs numeric accuracy.
- Demographic models for any choice outcome.

## Unresolved (say "not identifiable")
- **Age effects:** maturation vs cohort vs panel selection.
- **Social desirability:** response style vs real adjustment.
- **Income and neuroticism:** the direction of causation.
- **GPT-4.1 with an estimated profile:** not run, because the OpenRouter key is expired.
- **Generator issues:** the three found in the stress test (shrinkage labels, the behaviour floor, median ties) were fixed in `f9cbe6b` without changing any estimate.

## Practise these (in order)
1. **Five hard live groups** (`B_unseen/PERSONA_STRESS_TEST.md`):
   - 65+ with income under $30k (watch the CRT label);
   - a repeated variable (now rejected; explain the fix);
   - 18–29 with $100k+;
   - Midwest with an associate degree;
   - students.
2. **Live loop:** run `python src/personas.py build …`, read the definition and n back, check the shrink weight, then narrate only the "distinct" traits.
3. **Hardest questions** (`D_review/REVIEW_SIMULATION.md`): H7 (say–do), H5 (interaction test), H3 (self-presentation), S3 (units), P3 (the CLI bug). Answer each with "found it, fixed it, no estimate changed".
4. **One-sentence LLM answer:** "In our tests, LLM personas never beat a free statistical baseline. Narrative personas made them more confident, not more accurate."
5. **Client logic** (`E_client/CLIENT_DECISION_BRIEFS.md`): test, don't infer. Ask for one measured attitude and run one small randomised test.

**Costs:**
- Modal: about $0.46 for the night (offline batch $0.03, open-weight benchmark $0.43), against the $5 cap.
- OpenRouter: $0.
- No Modal apps are left running.
- The cached model weights (`brace-hf-cache`, about 23 GB) cost about $2 a month if kept. To delete them: `modal volume delete brace-hf-cache`.
