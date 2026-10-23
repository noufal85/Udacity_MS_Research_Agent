# Validation and submission readiness

Part 1 has been executed with real OpenAI embeddings and saved outputs. Part 2 remains blocked by a missing Tavily key. Offline tests are not substitutes for the assignment's remaining live agent demonstration.

## Checks performed

The complete offline suite passed: **22 tests**. Compilation and `pip check` passed without errors, and the source-only notebook gate passed. Part 1 passes its saved-output gate; the full gate remains failed because Part 2 is not executed.

- Parsed all fifteen original game JSON records and checked their schema, IDs and source paths.
- Tested local success, insufficient retrieval, empty retrieval, low confidence, web URL preservation, follow-up resolution, session isolation, invalid citations and provider failures.
- Used a real temporary Chroma collection with deterministic test-only vectors to verify persistence, reopening, repeatable upserts and retrieval. These vectors are not used in the project notebooks and do not demonstrate semantic embedding quality.
- Executed a separate small notebook in a real Python kernel to validate the notebook runner and working directory. This is a runner test, not a project demonstration.
- Validated both deliverable notebooks' JSON and Python source with `scripts/verify_submission.py --source-only`.
- Verified the user-authorized OpenAI key against `https://api.openai.com/v1`. A real `gpt-4o-mini` completion succeeded. The key was held only in an ephemeral process environment.
- Executed `scripts/execute_notebooks.py --part 1`. All five Part 1 code cells executed, producing four saved output cells, with no error outputs.
- Confirmed the saved outputs show 15 validated records, collection `udaplay` containing 15 documents, persistence after reopening, and a semantic query whose top result is Grand Theft Auto: San Andreas with publisher Rockstar Games and source `games/002.json`.
- Invoked the Part 1 saved-output verifier successfully. The complete verifier still rejects Part 2's missing execution counts and outputs.

## Remaining rubric gate

Configure a Tavily key locally alongside the OpenAI key and personal endpoint, run `python scripts/execute_notebooks.py --part 2`, inspect the saved notebook, then run `python scripts/verify_submission.py`. Required remaining evidence includes at least three Part 2 queries, visible retrieval/evaluation/search stages, cited answers and conversation memory. Commit and push the reviewed Part 2 notebook after the gate passes. On a fresh checkout, execute Part 1 first to rebuild the ignored database.

Public availability of the source repository does not establish completion of this execution gate.
