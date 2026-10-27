import pytest

from lib import udaplay


def configure_openai_only(monkeypatch):
    monkeypatch.setattr(udaplay, 'load_dotenv', lambda *args, **kwargs: None)
    monkeypatch.setenv('OPENAI_API_KEY', 'test-credential')
    monkeypatch.setenv('OPENAI_BASE_URL', 'https://example.test/v1')
    monkeypatch.delenv('TAVILY_API_KEY', raising=False)
    monkeypatch.delenv('WEB_SEARCH_PROVIDER', raising=False)


def test_part_one_does_not_require_a_web_search_key(monkeypatch):
    configure_openai_only(monkeypatch)
    settings = udaplay.configure_environment(require_web=False)
    assert settings['embedding_model']


def test_full_agent_defaults_to_openai_without_a_tavily_key(monkeypatch):
    configure_openai_only(monkeypatch)
    settings = udaplay.configure_environment()
    assert settings['web_provider'] == 'openai'


def test_explicit_tavily_provider_still_requires_its_key(monkeypatch):
    configure_openai_only(monkeypatch)
    monkeypatch.setenv('WEB_SEARCH_PROVIDER', 'tavily')
    with pytest.raises(RuntimeError, match='TAVILY_API_KEY'):
        udaplay.configure_environment()
