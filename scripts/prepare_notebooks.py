"""Populate the supplied notebooks while retaining their required paths."""

from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / 'project' / 'starter'


def save_notebook(name, cells):
    path = STARTER / name
    if path.exists():
        existing = nbformat.read(path, as_version=4)
        if any(cell.get('execution_count') is not None or cell.get('outputs') for cell in existing.cells):
            raise RuntimeError(f'Refusing to replace executed notebook: {name}')
    notebook = nbformat.v4.new_notebook(cells=cells)
    notebook.metadata.kernelspec = {
        'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3',
    }
    notebook.metadata.language_info = {'name': 'python', 'version': '3.13'}
    nbformat.write(notebook, path)


md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell

save_notebook('Udaplay_01_starter_project.ipynb', [
    md('# UdaPlay Part 1\n\nBuild a persistent vector database from the fifteen supplied game records. '
       'Run this notebook before Part 2, from `project/starter`. '
       'The database directory is `chromadb` and the collection is `udaplay`.'),
    md('## Environment\n\nConfigure `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `TAVILY_API_KEY` '
       'using an ignored `.env` or exported environment variables. Credentials are never displayed.'),
    code('import importlib.util\nimport sys\n\n'
         'if importlib.util.find_spec("pysqlite3") is not None:\n'
         '    import pysqlite3\n'
         '    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")'),
    code('from pathlib import Path\nimport json\n\n'
         'from lib.udaplay import configure_environment, load_games, GameVectorStore\n\n'
         'settings = configure_environment(require_web=False)\n'
         'print("Required environment variables are configured.")\n'
         'print("Embedding model:", settings["embedding_model"])'),
    md('## Load and validate the dataset\n\nEach JSON file becomes a document with the game name, '
       'platform, genre, publisher, description and release year. File stems provide stable IDs. '
       'Metadata retains the original values and a source path for citations.'),
    code('records = load_games(Path("games"))\n'
         'assert len(records) == 15\n'
         'print("Validated game records:", len(records))\n'
         'print(json.dumps(records[0], indent=2, ensure_ascii=False))'),
    md('## Persist the collection\n\nThe store configures OpenAI embeddings using the same key, '
       'endpoint and model in both notebooks. Upsert makes repeated ingestion safe.'),
    code('store = GameVectorStore(path="chromadb", create=True)\n'
         'count = store.ingest(records)\n'
         'assert count == 15\n'
         'print(f"Collection {store.collection.name!r}: {count} documents")'),
    md('## Reopen and query\n\nReopen the database to demonstrate persistence. '
       'Semantic search returns candidate documents; similarity alone does not establish answer quality. '
       'Part 2 evaluates that separately.'),
    code('reopened = GameVectorStore(path="chromadb")\n'
         'assert reopened.collection.count() == 15\n'
         'query = "Who published Grand Theft Auto: San Andreas?"\n'
         'results = reopened.search(query)\n'
         'assert results\n'
         'print("Query:", query)\n'
         'for result in results:\n'
         '    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))'),
    md('## Part 1 result\n\nThe persistent database is ready for Part 2 after all cells above succeed. '
       'Keep `chromadb/` locally between runs. It is reproducible from the dataset and is excluded from Git.'),
])

save_notebook('Udaplay_02_starter_project.ipynb', [
    md('# UdaPlay Part 2\n\nA stateful research agent that retrieves local game data, evaluates '
       'its sufficiency, searches the web when required, and produces cited reports.'),
    md('## Environment and database\n\nRun Part 1 first. This notebook uses its `chromadb` '
       'database and `udaplay` collection with the same embedding configuration.'),
    code('import importlib.util\nimport sys\n\n'
         'if importlib.util.find_spec("pysqlite3") is not None:\n'
         '    import pysqlite3\n'
         '    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")'),
    code('import json\n\nfrom lib.udaplay import (\n'
         '    configure_environment, ResearchAgent, EvaluationReport, ResearchReport,\n'
         '    retrieve_game, evaluate_retrieval, game_web_search,\n)\n\n'
         'settings = configure_environment()\n'
         'agent = ResearchAgent.from_environment(database_path="chromadb")\n'
         'assert agent.store.collection.count() == 15\n'
         'print("Research model:", settings["model"])\n'
         'print("Database loaded:", agent.store.collection.name)'),
    md('## Tools and state machine\n\n'
       '- `retrieve_game`: query the persistent vector database and retain source metadata.\n'
       '- `evaluate_retrieval`: return a typed `EvaluationReport` with sufficiency, confidence and an explanation.\n'
       '- `game_web_search`: use Tavily when evidence is absent or insufficient.\n\n'
       'The implementations are in `lib/udaplay.py`. The supplied `lib/state_machine.py` '
       'executes explicit retrieve → evaluate → optional web search → report nodes. '
       'Local support below 70% routes to web search even if the evaluator marks it useful. '
       'Retrieved text is treated as data rather than instructions. Reports may cite only supplied source IDs.'),
    code('print("Registered stages:", list(agent.workflow.steps))\n'
         'for function in (retrieve_game, evaluate_retrieval, game_web_search):\n'
         '    print(function.__name__ + ": " + function.__doc__)'),
    md('## Required example queries\n\nThe first two questions concern the local dataset. '
       'Mortal Kombat X is absent, so it must demonstrate web fallback. '
       'Each report shows stage activity, the evaluation explanation, the answer, confidence, and citations. '
       'These are concise decision summaries, not hidden model reasoning.'),
    code('questions = [\n'
         '    "When was Pokémon Gold and Silver released?",\n'
         '    "Which one was the first 3D platformer Mario game?",\n'
         '    "Was Mortal Kombat X released on PlayStation 5?",\n]\n'
         'reports = []\n'
         'for question in questions:\n'
         '    report = agent.invoke(question, session_id="examples")\n'
         '    reports.append(report)\n'
         '    report.display()\n'
         '    print("\\nStructured report:")\n'
         '    print(report.model_dump_json(indent=2))'),
    md('## Conversation memory\n\nA follow-up resolves its reference from the same session. '
       'Other sessions remain isolated. Memory lasts for the current Python process; '
       'persistent long-term memory is an optional extension.'),
    code('followup = agent.invoke("Which company published that game?", session_id="examples")\n'
         'followup.display()\n'
         'print("Session turns:", len(agent.history["examples"]))\n'
         'assert len(agent.history["examples"]) == 4'),
    md('## Performance and evidence checks\n\nThe assertions below verify demonstrated behavior, '
       'rather than assuming the prompts caused the intended route. Confidence is the model’s '
       'self-assessed support, not a calibrated probability of correctness. '
       'Web results may change over time, and the fifteen-record dataset is intentionally small.'),
    code('summary = [{"question": report.question, "route": report.route,\n'
         '            "confidence": report.confidence, "sources": len(report.sources),\n'
         '            "stages": [event["stage"] for event in report.trace]}\n'
         '           for report in reports]\n'
         'print(json.dumps(summary, indent=2, ensure_ascii=False))\n'
         'assert any(report.route == "local" for report in reports)\n'
         'assert reports[2].route == "web", "Mortal Kombat X must demonstrate web fallback"\n'
         'for report in reports:\n'
         '    assert report.sources, "Each example needs supporting citations"\n'
         '    assert report.trace[0]["stage"] == "retrieve_game"\n'
         '    assert report.trace[1]["stage"] == "evaluate_retrieval"\n'
         '    if report.route == "web":\n'
         '        assert all(source.url.startswith(("https://", "http://")) for source in report.sources)\n'
         'print("Required local, fallback, trace and citation demonstrations passed.")'),
])

print('Prepared both required notebooks. Execute them to create real saved outputs.')
