# Validation and submission readiness

Both deliverable notebooks have been executed with real API calls and saved outputs. The user's requested provider change removes the Tavily credential dependency: OpenAI hosted web search uses the same authorized key as embeddings, evaluation and reporting. The full saved-output gate passes.

## Checks performed

The complete offline suite passed: **29 tests**. Source validation, saved notebook validation, compilation and dependency integrity were checked separately. No mocked provider outputs have been inserted into either deliverable notebook.

- Parsed all fifteen original game JSON records and checked their schema, IDs and source paths.
- Tested local success, insufficient retrieval, empty retrieval, low confidence, web URL preservation, follow-up resolution, session isolation, invalid citations and provider failures.
- Used a real temporary Chroma collection with deterministic test-only vectors to verify persistence, reopening, repeatable upserts and retrieval. These vectors are not used in the project notebooks and do not demonstrate semantic embedding quality.
- Executed a separate small notebook in a real Python kernel to validate the notebook runner and working directory. This is a runner test, not a project demonstration.
- Validated both deliverable notebooks' JSON and Python source with `scripts/verify_submission.py --source-only`.
- Verified the user-authorized OpenAI key against `https://api.openai.com/v1`. A real `gpt-4o-mini` completion succeeded. The key was held only in an ephemeral process environment.
- Executed `scripts/execute_notebooks.py --part 1`. All five Part 1 code cells executed, producing four saved output cells, with no error outputs.
- Confirmed the saved outputs show 15 validated records, collection `udaplay` containing 15 documents, persistence after reopening, and a semantic query whose top result is Grand Theft Auto: San Andreas with publisher Rockstar Games and source `games/002.json`.
- Executed `scripts/execute_notebooks.py --part 2` with the same authorized OpenAI key and the OpenAI search provider. All six Part 2 code cells executed with saved outputs and no error outputs.
- Inspected the three structured reports: Pokémon Gold and Silver and Super Mario 64 use local evidence; Mortal Kombat X triggers retrieval, negative evaluation, a real hosted web-search call and a cited answer distinguishing PS4 release from PS5 backward compatibility.
- The final Mortal Kombat X answer cites an official PlayStation game page. Its follow-up asks for the publisher, resolves to Mortal Kombat X and returns a cited publisher answer. The session retains four turns.
- During live inspection, an initial ambiguous follow-up selected an older game. Added a regression test and highlighted the latest turn explicitly in compact conversation context. Reran the complete Part 2 notebook and verified the corrected follow-up with a notebook assertion.
- Ran the full `scripts/verify_submission.py`: saved notebook execution and all required evidence markers pass.

## Reproduction

Configure the OpenAI key and personal endpoint locally, run `python scripts/execute_notebooks.py`, then run `python scripts/verify_submission.py`. A fresh checkout must execute Part 1 first to rebuild the ignored database. The published notebooks already include the reviewed outputs; API credentials are only needed to rerun them, not to inspect them or validate their saved evidence.

Live outputs vary with provider results. This review verifies the saved demonstration and workflow behavior, not an assurance that every future answer will be correct. Hosted search returns cited summaries; they are clearly labeled as summaries rather than verbatim page downloads.
