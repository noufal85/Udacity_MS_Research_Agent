import hashlib

import numpy as np
from chromadb.api.types import EmbeddingFunction

from lib.udaplay import GameVectorStore, load_games
from test_udaplay import STARTER


class FixtureEmbedding(EmbeddingFunction):
    """Deterministic vectors for persistence tests; never used by the notebooks."""

    def __init__(self):
        self.dimension = 32

    def __call__(self, input):
        return [self.vector(text) for text in input]

    def embed_query(self, input):
        return self(input)

    @staticmethod
    def vector(text):
        return np.array(list(hashlib.sha256(text.encode()).digest()), dtype=float).tolist()

    @staticmethod
    def name():
        return 'test_fixture_embedding'

    def get_config(self):
        return {}

    @staticmethod
    def build_from_config(config):
        return FixtureEmbedding()


def test_chroma_persists_and_reopens_all_fifteen_games(tmp_path):
    path = tmp_path / 'chromadb'
    store = GameVectorStore(path, embedding_function=FixtureEmbedding(), create=True)
    records = load_games(STARTER / 'games')
    assert store.ingest(records) == 15
    assert store.ingest(records) == 15

    reopened = GameVectorStore(path, embedding_function=FixtureEmbedding())
    assert reopened.collection.name == 'udaplay'
    assert reopened.collection.count() == 15
    results = reopened.search(records[0]['document'])
    assert results[0].source_id == 'local:001'
    assert results[0].url == 'games/001.json'
    assert results[0].distance >= 0


def test_empty_collection_does_not_request_embeddings(tmp_path):
    store = GameVectorStore(tmp_path, embedding_function=FixtureEmbedding(), create=True)
    assert store.search('A game') == []
