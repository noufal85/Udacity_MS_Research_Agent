# Reviewer feedback and correction plan

Reviewed baseline: public `noufal85/Udacity_MS_Research_Agent`, branch `main`, local and remote commit `0b0038e600271bf28d50da12a7feb7d8cded434c` at intake. The reviewer did not name a commit; their description matches this baseline: Part 1 has five executed cells, while all six Part 2 code cells are unexecuted.

| Feedback | Requirement and category | Reproduction | Change | Regression check | Status |
|---|---|---|---|---|---|
| Demonstration criterion fails despite passing implementation criteria | Saved Part 2 output for three queries, tool activity, cited answers and conversation state; runtime evidence | Baseline notebook had zero executed Part 2 cells and no outputs; full verifier failed | Executed Part 2 with real providers and saved the reviewed outputs | All six code cells executed; two local answers, real web fallback, cited answers, four-turn session; full verifier passes | Resolved |
| Tavily credential blocks execution | Real external search through an API; environment dependency | OpenAI key works but no Tavily key is configured | User explicitly requested using the existing OpenAI key instead; added OpenAI hosted web search while retaining optional Tavily support | Completed hosted search calls and real URL annotations; uncited model text rejected in tests | Resolved |
| Live inspection found ambiguous follow-up selecting an older topic | Conversation context should resolve references to the latest relevant game; behavioral issue | Initial live follow-up incorrectly selected Pokémon after the Mortal Kombat X question | Added compact history with an explicit latest turn and a regression test; reran Part 2 | Saved follow-up resolves Mortal Kombat X; notebook asserts that referent | Resolved |

The assignment's rubric allows web search through an API such as Tavily. The project scenario recommends Tavily; the user's explicit instruction authorizes the OpenAI provider alternative. The three required tool names, retrieval-first sequence, evaluation threshold, reports and session memory remain the submission contracts. Only authentic executed outputs will satisfy the runtime evidence row.
