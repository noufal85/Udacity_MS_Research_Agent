import pytest

from lib import udaplay


def configure_openai_only(monkeypatch):
    monkeypatch.setattr(udaplay, 'load_dotenv', lambda *args, **kwargs: None)
    monkeypatch.setenv('OPENAI_API_KEY', 'test-credential')
    monkeypatch.setenv('OPENAI_BASE_URL', 'https://example.test/v1')
    monkeypatch.delenv('TAVILY_API_KEY', raising=False)


def test_part_one_does_not_require_a_web_search_key(monkeypatch):
    configure_openai_only(monkeypatch)
    settings = udaplay.configure_environment(require_web=False)
    assert settings['embedding_model']


def test_full_agent_still_requires_tavily(monkeypatch):
    configure_openai_only(monkeypatch)
    with pytest.raises(RuntimeError, match='TAVILY_API_KEY'):
        udaplay.configure_environment()
