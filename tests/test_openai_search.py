from types import SimpleNamespace

import pytest

from lib import udaplay


class ResponsesClient:
    def __init__(self, output):
        self.calls = []
        self.output = output
        self.responses = SimpleNamespace(create=self.create)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output=self.output, status='completed')


def response_output(text='MKX launched on PS4, Xbox One and Windows. [source]', url='https://example.org/mkx'):
    citation = SimpleNamespace(type='url_citation', url=url, title='MKX platforms',
                               start_index=text.index('[source]'), end_index=len(text))
    return [
        SimpleNamespace(type='web_search_call', status='completed'),
        SimpleNamespace(type='message', content=[SimpleNamespace(
            type='output_text', text=text, annotations=[citation],
        )]),
    ]


def test_openai_search_requires_real_search_and_retains_attributed_citations():
    client = ResponsesClient(response_output())
    search = udaplay.OpenAIWebSearchClient(client, model='test-search-model')
    evidence = udaplay.game_web_search('Was MKX released on PS5?', search)
    assert len(evidence) == 1
    assert evidence[0].url == 'https://example.org/mkx'
    assert 'PS4, Xbox One and Windows' in evidence[0].content
    assert client.calls[0]['tools'] == [{'type': 'web_search'}]
    assert client.calls[0]['tool_choice'] == 'required'
    assert client.calls[0]['model'] == 'test-search-model'


def test_uncited_model_text_is_not_accepted_as_web_evidence():
    output = response_output()
    output[1].content[0].annotations = []
    search = udaplay.OpenAIWebSearchClient(ResponsesClient(output))
    assert udaplay.game_web_search('Platforms?', search) == []


def test_search_is_rejected_if_no_search_tool_was_called():
    search = udaplay.OpenAIWebSearchClient(ResponsesClient(response_output()[1:]))
    with pytest.raises(ValueError, match='search'):
        search.search('Platforms?')


def test_invalid_openai_citation_urls_are_filtered():
    search = udaplay.OpenAIWebSearchClient(ResponsesClient(response_output(url='javascript:alert(1)')))
    assert udaplay.game_web_search('Platforms?', search) == []


def test_citation_receives_its_own_paragraph_not_unrelated_claims():
    text = 'Unrelated unsupported claim.\n\nMKX was released on PS4. [source]\n\nOther information.'
    output = response_output(text=text)
    output[1].content[0].annotations[0].end_index = text.index('[source]') + len('[source]')
    search = udaplay.OpenAIWebSearchClient(ResponsesClient(output))
    evidence = udaplay.game_web_search('Platforms?', search)
    assert 'MKX was released on PS4' in evidence[0].content
    assert 'Unrelated unsupported claim' not in evidence[0].content
    assert 'Other information' not in evidence[0].content
