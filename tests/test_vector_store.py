from langchain_core.documents import Document

from src.database import ingest, retriever


class FakeEmbeddings:
    def embed_query(self, text):
        return [0.1, 0.2]

    def embed_documents(self, texts):
        return [[float(i)] for i, _ in enumerate(texts)]


class FakeChunkRepository:
    def __init__(self, existing_ids=(), matches=()):
        self.upserts = []
        self.deleted = set()
        self.existing_ids = set(existing_ids)
        self.matches = list(matches)
        self.match_args = None

    def upsert(self, rows):
        self.upserts.append(rows)
        self.existing_ids.update(row["id"] for row in rows)

    def list_ids(self):
        return set(self.existing_ids)

    def delete_ids(self, ids):
        self.deleted.update(ids)

    def match(self, embedding, match_count, module=None):
        self.match_args = (embedding, match_count, module)
        return self.matches


def make_chunk(chunk_id, module="modulo_1"):
    doc_id = chunk_id.split(":")[0]
    return Document(
        id=chunk_id,
        page_content=f"texto {chunk_id}",
        metadata={"doc_id": doc_id, "module": module, "document": "Doc", "section": "p. 1"},
    )


def test_query_relevant_documents_filters_by_distance_and_keeps_metadata(monkeypatch):
    repo = FakeChunkRepository(matches=[
        {"id": "a:00000", "content": "perto", "metadata": {"document": "Res. CVM 44", "section": "p. 3"}, "distance": 0.2},
        {"id": "a:00001", "content": "longe", "metadata": {"document": "Res. CVM 44", "section": "p. 9"}, "distance": 0.8},
    ])
    monkeypatch.setattr(retriever, "ChunkRepository", repo)
    monkeypatch.setattr(retriever, "get_embeddings", lambda: FakeEmbeddings())

    docs = retriever.query_relevant_documents("o que é fato relevante?", module="modulo_3", k=5, max_distance=0.5)

    assert repo.match_args == ([0.1, 0.2], 5, "modulo_3")
    assert [doc.page_content for doc in docs] == ["perto"]
    assert docs[0].metadata == {"document": "Res. CVM 44", "section": "p. 3", "distance": 0.2}


def test_query_relevant_documents_returns_empty_on_failure(monkeypatch):
    class BrokenRepository:
        @staticmethod
        def match(*args, **kwargs):
            raise RuntimeError("supabase fora do ar")

    monkeypatch.setattr(retriever, "ChunkRepository", BrokenRepository)
    monkeypatch.setattr(retriever, "get_embeddings", lambda: FakeEmbeddings())

    assert retriever.query_relevant_documents("pergunta") == []


def test_vectorize_chunks_upserts_in_batches_and_removes_stale_chunks(monkeypatch):
    repo = FakeChunkRepository(existing_ids={"velho:00000", "a:00000"})
    monkeypatch.setattr(ingest, "ChunkRepository", repo)
    monkeypatch.setattr(ingest, "get_embeddings", lambda: FakeEmbeddings())
    monkeypatch.setattr(ingest, "INSERT_BATCH_SIZE", 2)

    ingest.vectorize_chunks([make_chunk("a:00000"), make_chunk("a:00001"), make_chunk("b:00000", "modulo_2")])

    assert [len(batch) for batch in repo.upserts] == [2, 1]
    row = repo.upserts[1][0]
    assert row["id"] == "b:00000" and row["doc_id"] == "b" and row["module"] == "modulo_2"
    assert row["embedding"] == [0.0]
    assert repo.deleted == {"velho:00000"}
