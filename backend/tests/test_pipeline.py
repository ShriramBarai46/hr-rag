import numpy as np

from app.core.config import Settings
from app.services.rag_pipeline import NOT_FOUND, RAGPipeline
from app.services.vector_store import FaissVectorStore

CHUNKS = [
    {"id": 0, "source": "h.md", "section": "Leave > Annual leave", "page": None,
     "text": "24 paid leaves per year.", "embed_text": "annual leave 24 days"},
    {"id": 1, "source": "h.md", "section": "Leave > Carry forward", "page": None,
     "text": "Carry forward max 10 days.", "embed_text": "carry forward 10 days"},
    {"id": 2, "source": "h.md", "section": "Salary", "page": None,
     "text": "Paid on last working day.", "embed_text": "salary credited"},
]


class FakeEmbedder:
    def encode(self, texts, show_progress=False):
        return np.array([[1.0, 0.0, 0.0]] * len(texts), dtype="float32")


class FakeReranker:
    """Gives the highest score to the chunk that contains a word from the question."""
    def score(self, question, passages):
        words = question.lower().split()
        return [5.0 if any(w in p for w in words) else -8.0 for p in passages]


class FakeLLM:
    enabled = True

    def __init__(self):
        self.calls = 0

    def generate(self, system_prompt, user_prompt):
        self.calls += 1
        return "LLM answer"

    def stream(self, system_prompt, user_prompt):
        self.calls += 1
        yield from ["LLM ", "answer"]


def make_pipeline(llm=None):
    # Vectors chosen so FAISS ranks Annual leave first, Carry forward second
    vectors = np.array([[1, 0, 0], [0.9, 0.1, 0], [0.5, 0.5, 0]], dtype="float32")
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)
    store = FaissVectorStore.build(vectors, CHUNKS)
    settings = Settings(top_k_retrieve=3, top_k_final=2, min_rerank_score=-3.0)
    return RAGPipeline(settings, FakeEmbedder(), store, FakeReranker(), llm or FakeLLM())


def test_reranking_changes_order():
    results = make_pipeline().retrieve("carry forward")
    assert results[0].section == "Leave > Carry forward"
    assert results[0].vector_rank == 2          # was 2nd in FAISS, 1st after rerank


def test_not_found_skips_llm():
    llm = FakeLLM()
    resp = make_pipeline(llm).answer("capital of france")
    assert resp.found is False
    assert resp.answer == NOT_FOUND
    assert llm.calls == 0


def test_answer_returns_sources():
    resp = make_pipeline().answer("salary credited")
    assert resp.found is True
    assert resp.answer == "LLM answer"
    assert resp.sources[0].section == "Salary"
    assert len(resp.sources) == 2


def test_stream_sends_sources_before_tokens():
    events = list(make_pipeline().stream_answer("salary credited"))
    types = [e["type"] for e in events]
    assert types == ["status", "sources", "status", "token", "token", "done"]
    assert events[1]["sources"][0]["section"] == "Salary"
    assert "".join(e["text"] for e in events if e["type"] == "token") == "LLM answer"


def test_stream_not_found_skips_llm():
    llm = FakeLLM()
    events = list(make_pipeline(llm).stream_answer("capital of france"))
    assert events[1] == {"type": "sources", "found": False, "sources": []}
    assert events[2]["text"] == NOT_FOUND
    assert llm.calls == 0