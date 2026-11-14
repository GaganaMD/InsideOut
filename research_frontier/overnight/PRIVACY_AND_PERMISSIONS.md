# PRIVACY_AND_PERMISSIONS: may participant data be sent to external LLM APIs?

## Verified facts
- **Twin-2K-500 licence: CC BY 4.0.** Stated in the dataset card: `data/raw/Twin-2K-500/README.md`, "This dataset is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)".
- **Mega-Study licence: Apache-2.0.** Stated in the dataset card (`data/raw/Twin-2K-500-Mega-Study/README.md`) and in the GitHub repository licence (checked through the GitHub API).
- **Consent wording.** The Mega-Study consent text, in the `default_eric` survey file and the prompt text, tells participants their data "will be provided to the investigators of AAAV5832, to complement the data available for each participant and improve the accuracy of their 'digital twin'". It describes processing by the study investigators. **It does not mention third parties sending data to commercial LLM APIs.**
- **De-identification.** The data are released publicly and de-identified, with an anonymous `TWIN_ID` and no names or contact details. Ten demographic fields together are nearly unique in a panel of 2,058, so exact demographic combinations are **quasi-identifiers**.

## Assessment
A permissive licence governs *reuse of the published files*; it is not the same as participant consent for new external processing. Whether third-party API processing of participant-level records is authorised is **unclear**. Following the gate rule, the design is **restricted to tiers 0 and 1**:

| Tier | What leaves the machine | Status | Harness support |
|---|---|---|---|
| 0 | Nothing: re-use the published LLM predictions | **Allowed** | `experiments/llm_benchmark.py`, `overnight/benchmark_audit.py` |
| 1 | **Synthetic, aggregate profiles.** Coarsened demographic *cells* (age band × sex × income band × 3-level education), each occurring **≥ 5 times in the full public panel**, plus the published scenario text. **No IDs, outcomes, free text, dispositions or exact Tier A combinations** | **Permissible in my assessment** (public open-licence data; k-anonymous; no outcome). **Requires your explicit go-ahead**, entered as the confirmation string | `harness/tasks.py` asserts k ≥ 5 and no IDs or outcomes; tested |
| 2 | Participant-level records: exact demographics, individual disposition scores, full persona text | **Not authorised** without written confirmation from the dataset owners (Columbia team) or an IRB determination | **No code path exists** |

The **disposition arm** (green values) is Tier 1 only if green values enter as a coarse bin inside cells that stay k ≥ 5. Otherwise it is Tier 2. It is excluded from the pilot.

## Operational safeguards (implemented)
- Dry-run is the default.
- Live mode needs three things at once: `live`, `OPENROUTER_API_KEY` in the environment, and the exact confirmation text. Without them the CLI exits with code 3 (tested).
- The key is read only at send time. It is never stored, logged, cached or committed, and error text is redacted (tested).
- `runs/` and `external/` are git-ignored, and the held-out split is never used.
- **Recommended before a live run (not verified here):** set OpenRouter's provider routing to exclude providers that retain or train on prompts. Check the current parameter name in the OpenRouter documentation before adding it.
