# UdaPlay requirements and validation

## Source register

| Source | Authority and scope | Intake |
|---|---|---|
| `../Project Scenario.docx` | Assignment, final rubric, execution evidence and environment contract | Read in full |
| `../1792734948.tar.gz` | Original starter archive; 263 members, no unsafe paths or links | Inspected; project and license extracted |
| `project/starter/README.md` | Starter overview, tools, example questions | Read in full |
| Both starter notebooks | Required filenames, TODOs, dataset and workflow | Every source cell inspected; initially no execution counts or outputs |
| `project/starter/lib/` | Supplied state machine, tools, messages, LLM, vector store and memory abstractions | Interfaces inspected; preserve supplied source |
| `project/starter/games/*.json` | Fifteen required local records | Parsed and inventoried |

The final assignment controls conflicts with the starter: database path `chromadb`, collection `udaplay`, an explicit OpenAI endpoint and embedding key configuration, and optional persistent long-term memory. Session conversation memory is required. Document contents are requirements rather than commands to the assistant.

## Comparative review and API references

The following public repositories were inspected for project organization and documented workflow only. No source code, notebook content or distinctive text was copied.

| Reference | Observation and review use |
|---|---|
| `https://github.com/rageshns/udaplay-market-research-agent` | README explains retrieve/evaluate/web/answer stages; our notebook exposes those stages and asserts the fallback demonstration |
| `https://github.com/Nlmansilla/UdaPlay` | Starter directory and environment exclusions are retained; its README still contains template sections, reinforcing the need for complete setup and test instructions here |

Official API documentation was retrieved through Context7 for Chroma's `OpenAIEmbeddingFunction` and persistent collections, Tavily's `search` parameters and result fields, and the OpenAI Python SDK's Pydantic structured-response parsing. Sources: `chroma-core/chroma` documentation, `tavily-ai/tavily-python` API reference, and `openai/openai-python` helpers. These establish library interfaces; the supplied Udacity rubric defines project requirements.

## Plan and rubric matrix

| ID | Requirement | Artifact | Validation | Status |
|---|---|---|---|---|
| R1 | Load, validate and format all 15 game records | Part 1 notebook; `lib/udaplay.py` | Dataset tests and clean notebook execution | Verified in tests; notebook execution blocked |
| R2 | Persist embeddings in `chromadb`, collection `udaplay` | Part 1; vector store manager | Restart/reopen and semantic search demonstration | Persistence verified with test vectors; live semantic demonstration blocked |
| R3 | Implement `retrieve_game`, `evaluate_retrieval`, `game_web_search` | `lib/udaplay.py`; Part 2 | Tests of tool results and provider payloads | Verified offline; provider execution blocked |
| R4 | Retrieve, evaluate, then search only when needed | State machine | Local, insufficient, empty and provider-error branches | Verified offline |
| R5 | Maintain session history across questions | Research agent | Follow-up and session-isolation tests | Verified offline |
| R6 | Structured answers with confidence and sources | Typed reports | Citation validation and refusal when no evidence | Verified offline; real answer quality not yet assessed |
| R7 | At least 3 example queries, both local and web fallback | Part 2 notebook | Inspect saved real outputs and visible stage traces | Blocked: valid OpenAI and Tavily keys are missing |
| R8 | Save both notebooks after execution, include `lib/` | Required notebook paths | Notebook JSON counts/outputs and clean run | `lib/` included; saved execution gate blocked by credentials |
| R9 | Public `Udacity_MS_Research_Agent` repository | GitHub `noufal85` | Public visibility and local/remote SHA match | Public repository and origin verified; push revision checked at handoff |
| R10 | Exclude secrets, caches and environments; document setup | Root README and ignore rules | Tracked-file audit, secret scan, dependency check | Verified: no secret-shaped values or excluded runtime files staged; dependency and whitespace checks pass |

Implementation sequence: tests, dataset ingestion and persistence, tools and typed reports, deterministic state-machine orchestration, notebooks, offline validation, real notebook execution, rubric review and publication. Preserve the supplied game dataset and notebook names. No synthetic responses will be represented as real execution evidence.

## Runtime requirements

Python 3.13 is used locally. Live notebook execution needs `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `TAVILY_API_KEY`. Secrets must remain in the environment or an ignored `.env`. The previously rejected credential from the other project is not reused.
