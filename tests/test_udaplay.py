import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


STARTER = Path(__file__).resolve().parents[1] / 'project' / 'starter'


def test_required_research_module_exists():
    assert importlib.util.find_spec('lib.udaplay') is not None


def module():
    from lib import udaplay
    return udaplay


class StructuredClient:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = []
        self.beta = SimpleNamespace(chat=SimpleNamespace(
            completions=SimpleNamespace(parse=self.parse)))

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        parsed = kwargs['response_format'].model_validate(next(self.outputs))
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(
            parsed=parsed, refusal=None))])


class Store:
    def __init__(self, documents):
        self.documents = documents
        self.queries = []

    def search(self, query, limit=3):
        self.queries.append(query)
        return self.documents


class Search:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def search(self, **kwargs):
        self.calls.append(kwargs)
        return {'results': self.results}


def local_document():
    return module().Evidence(
        source_id='local:006', title='Pokémon Gold and Silver',
        content='Pokémon Gold and Silver was released on Game Boy Color in 1999.',
        url='games/006.json', distance=0.1,
    )


def test_all_game_records_have_stable_ids_and_sources():
    records = module().load_games(STARTER / 'games')
    assert len(records) == 15
    assert len({record['id'] for record in records}) == 15
    assert records[0]['metadata']['source'] == 'games/001.json'
    assert 'Publisher:' in records[0]['document']
    assert 'YearOfRelease:' in records[0]['document']


def test_invalid_game_record_is_rejected(tmp_path):
    (tmp_path / '001.json').write_text(json.dumps({'Name': 'Incomplete'}))
    with pytest.raises(ValueError, match='001.json'):
        module().load_games(tmp_path)


def test_empty_dataset_is_rejected(tmp_path):
    with pytest.raises(ValueError, match='No game'):
        module().load_games(tmp_path)


def test_empty_retrieval_is_insufficient_without_an_llm_call():
    client = StructuredClient([])
    result = module().evaluate_retrieval('Unknown game?', [], client, 'test-model')
    assert not result.useful
    assert result.confidence == 0
    assert not client.calls


def test_evaluation_uses_structured_model_and_original_question():
    client = StructuredClient([{'useful': True, 'confidence': 0.95,
                                'description': 'Release year is explicitly stated.'}])
    result = module().evaluate_retrieval('When was it released?', [local_document()], client, 'test-model')
    assert result.useful
    payload = client.calls[0]
    assert payload['temperature'] == 0
    assert payload['response_format'] is module().EvaluationReport
    assert 'When was it released?' in payload['messages'][1]['content']


def test_web_search_preserves_urls_and_excludes_invalid_results():
    search = Search([
        {'title': 'Publisher', 'url': 'https://example.org/game', 'content': 'Release platforms.'},
        {'title': 'Bad', 'url': 'javascript:alert(1)', 'content': 'Bad'},
    ])
    evidence = module().game_web_search('Platforms?', search)
    assert len(evidence) == 1
    assert evidence[0].url == 'https://example.org/game'
    assert search.calls[0]['query'] == 'Platforms?'


def test_sufficient_local_retrieval_skips_web_search():
    client = StructuredClient([
        {'useful': True, 'confidence': 0.95, 'description': 'Year is stated.'},
        {'answer': 'It was released in 1999.', 'confidence': 0.95, 'source_ids': ['local:006']},
    ])
    search = Search([])
    agent = module().ResearchAgent(Store([local_document()]), client, search, model='test-model')
    report = agent.invoke('When was Pokémon Gold and Silver released?')
    assert report.answer == 'It was released in 1999.'
    assert report.route == 'local'
    assert not search.calls
    assert [step['stage'] for step in report.trace] == ['retrieve_game', 'evaluate_retrieval', 'report']
    assert report.sources[0].url == 'games/006.json'


def test_insufficient_retrieval_triggers_web_fallback():
    client = StructuredClient([
        {'useful': False, 'confidence': 0.2, 'description': 'Wrong game.'},
        {'answer': 'The listed platforms do not include PS5.', 'confidence': 0.9, 'source_ids': ['web:1']},
    ])
    search = Search([{'title': 'MKX platforms', 'url': 'https://example.org/mkx',
                      'content': 'Platforms: PS4, Xbox One, PC.'}])
    report = module().ResearchAgent(Store([local_document()]), client, search).invoke('Was Mortal Kombat X released on PS5?')
    assert report.route == 'web'
    assert search.calls
    assert report.sources[0].url == 'https://example.org/mkx'
    assert 'game_web_search' in [step['stage'] for step in report.trace]


def test_low_confidence_retrieval_triggers_web_even_when_useful():
    client = StructuredClient([
        {'useful': True, 'confidence': 0.3, 'description': 'Ambiguous.'},
    ])
    search = Search([])
    report = module().ResearchAgent(Store([local_document()]), client, search).invoke('Uncertain?')
    assert report.route == 'unanswered'
    assert search.calls
    assert report.confidence == 0
    assert not report.sources


def test_followup_uses_prior_context_and_sessions_are_isolated():
    client = StructuredClient([
        {'useful': True, 'confidence': 0.9, 'description': 'Supported.'},
        {'answer': 'Released in 1999.', 'confidence': 0.9, 'source_ids': ['local:006']},
        {'query': 'Which platform was Pokémon Gold and Silver released on?'},
        {'useful': True, 'confidence': 0.9, 'description': 'Supported.'},
        {'answer': 'Game Boy Color.', 'confidence': 0.9, 'source_ids': ['local:006']},
        {'useful': True, 'confidence': 0.9, 'description': 'Supported.'},
        {'answer': 'A new session.', 'confidence': 0.9, 'source_ids': ['local:006']},
    ])
    store = Store([local_document()])
    agent = module().ResearchAgent(store, client, Search([]))
    agent.invoke('When was Pokémon Gold and Silver released?', session_id='a')
    followup = agent.invoke('And which platform?', session_id='a')
    assert 'Pokémon' in followup.resolved_question
    assert 'Released in 1999.' in client.calls[2]['messages'][1]['content']
    agent.invoke('Unrelated new session', session_id='b')
    assert store.queries[-1] == 'Unrelated new session'
    assert len(agent.history['a']) == 2
    assert len(agent.history['b']) == 1


def test_unknown_citation_id_is_rejected():
    client = StructuredClient([
        {'useful': True, 'confidence': 0.9, 'description': 'Supported.'},
        {'answer': 'Invented answer.', 'confidence': 0.9, 'source_ids': ['fake:1']},
    ])
    agent = module().ResearchAgent(Store([local_document()]), client, Search([]))
    with pytest.raises(ValueError, match='citation'):
        agent.invoke('Release?')
    assert not agent.history.get('default')


def test_provider_failure_is_not_saved_as_success():
    class BrokenStore:
        def search(self, query, limit=3):
            raise ConnectionError('Provider unavailable')
    agent = module().ResearchAgent(BrokenStore(), StructuredClient([]), Search([]))
    with pytest.raises(ConnectionError):
        agent.invoke('Release?')
    assert not agent.history.get('default')


def test_followup_context_highlights_latest_topic_without_source_documents():
    client = StructuredClient([
        {'useful': True, 'confidence': 0.9, 'description': 'Supported.'},
        {'answer': 'Released in 1999.', 'confidence': 0.9, 'source_ids': ['local:006']},
        {'query': 'Who published Super Mario 64?'},
        {'useful': True, 'confidence': 0.9, 'description': 'Supported.'},
        {'answer': 'Nintendo published Super Mario 64.', 'confidence': 0.9, 'source_ids': ['local:006']},
        {'query': 'Which platform was Super Mario 64 released on?'},
        {'useful': True, 'confidence': 0.9, 'description': 'Supported.'},
        {'answer': 'Nintendo 64.', 'confidence': 0.9, 'source_ids': ['local:006']},
    ])
    agent = module().ResearchAgent(Store([local_document()]), client, Search([]))
    agent.invoke('When was Pokémon Gold and Silver released?')
    agent.invoke('Who published Super Mario 64?')
    agent.invoke('And on which platform?')
    payload = json.loads(client.calls[5]['messages'][1]['content'])
    assert payload['latest_turn']['question'] == 'Who published Super Mario 64?'
    assert payload['latest_turn']['answer'] == 'Nintendo published Super Mario 64.'
    assert 'documents' not in payload
    assert 'content' not in payload['latest_turn']
