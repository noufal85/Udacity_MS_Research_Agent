# Validation and submission readiness

The project includes complete implementation sources, but live notebook execution is blocked by missing credentials. Offline tests are not substitutes for the assignment's saved real outputs.

## Checks performed

The complete offline suite passed: **20 tests**. Compilation and `pip check` passed without errors, and the source-only notebook gate passed. The full saved-output gate remains failed for the reasons below.

- Parsed all fifteen original game JSON records and checked their schema, IDs and source paths.
- Tested local success, insufficient retrieval, empty retrieval, low confidence, web URL preservation, follow-up resolution, session isolation, invalid citations and provider failures.
- Used a real temporary Chroma collection with deterministic test-only vectors to verify persistence, reopening, repeatable upserts and retrieval. These vectors are not used in the project notebooks and do not demonstrate semantic embedding quality.
- Executed a separate small notebook in a real Python kernel to validate the notebook runner and working directory. This is a runner test, not a project demonstration.
- Validated both deliverable notebooks' JSON and Python source with `scripts/verify_submission.py --source-only`.
- Invoked `scripts/execute_notebooks.py`; its configuration check reported missing `OPENAI_API_KEY` and `TAVILY_API_KEY` before any live calls or notebook mutations.
- Invoked the full `scripts/verify_submission.py`; it correctly rejected the unexecuted notebooks and absent runtime evidence.

## Remaining rubric gate

Configure valid OpenAI and Tavily credentials locally, run `python scripts/execute_notebooks.py`, inspect both saved notebooks, then run `python scripts/verify_submission.py`. Required evidence includes Part 1 ingestion and semantic-search output, at least three Part 2 queries, visible retrieval/evaluation/search stages, cited answers and conversation memory. Commit and push the reviewed executed notebooks after the gate passes.

Public availability of the source repository does not establish completion of this execution gate.
