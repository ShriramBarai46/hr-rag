import json

import pytest
from fastapi.testclient import TestClient

from app.schemas.chat import AnswerResponse, Source
from app.services.rag_pipeline import RAGPipeline


class FakePipeline:
    class llm:
        enabled = True

    store = [1, 2, 3]

    def retrieve(self, question):
        return []

    def answer(self, question):
        if question == "boom please":
            raise RuntimeError("LLM down")
        return AnswerResponse(answer="ok", found=True, sources=[
            Source(n=1, source="h.md", section="Salary", text="t",
                   rerank_score=1.0, vector_rank=1)])

    def stream_answer(self, question):
        yield {"type": "status", "stage": "searching"}
        if question == "boom please":
            raise RuntimeError("LLM down")
        yield {"type": "token", "text": "ok"}
        yield {"type": "done"}


@pytest.fixture
def client(monkeypatch):
    # Replace the real (slow) pipeline before the app starts
    monkeypatch.setattr(RAGPipeline, "from_settings", classmethod(lambda cls, s: FakePipeline()))
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/api/v1/health").json() == {"status": "ok", "chunks": 3, "llm_enabled": True}


def test_ask_ok(client):
    r = client.post("/api/v1/ask", json={"question": "When is salary paid?"})
    assert r.status_code == 200
    assert r.json()["sources"][0]["section"] == "Salary"


def test_ask_validation(client):
    assert client.post("/api/v1/ask", json={"question": "x"}).status_code == 422


def test_ask_error_is_hidden(client):
    r = client.post("/api/v1/ask", json={"question": "boom please"})
    assert r.status_code == 502
    assert "LLM down" not in r.text


def test_stream_returns_ndjson_events(client):
    r = client.post("/api/v1/ask/stream", json={"question": "When is salary paid?"})
    assert r.status_code == 200
    events = [json.loads(line) for line in r.text.splitlines()]
    assert [e["type"] for e in events] == ["status", "token", "done"]


def test_stream_error_is_hidden(client):
    r = client.post("/api/v1/ask/stream", json={"question": "boom please"})
    events = [json.loads(line) for line in r.text.splitlines()]
    assert events[-1]["type"] == "error"
    assert "LLM down" not in r.text