import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_pipeline
from app.schemas.chat import AnswerResponse, QuestionRequest, SearchResult
from app.services.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.post("/search", response_model=list[SearchResult])
def search(body: QuestionRequest, show_all: bool = False,
           pipeline: RAGPipeline = Depends(get_pipeline)):
    """Retrieval only (no LLM). By default returns only relevant chunks.
    Set show_all=true to see every candidate with its scores (for debugging)."""
    results = pipeline.retrieve(body.question)
    if show_all:
        return results
    return [r for r in results if r.rerank_score >= pipeline.settings.min_rerank_score]


@router.post("/ask", response_model=AnswerResponse)
def ask(body: QuestionRequest, pipeline: RAGPipeline = Depends(get_pipeline)):
    """Full RAG answer with sources, returned all at once."""
    try:
        return pipeline.answer(body.question)
    except Exception:
        logger.exception("Failed to answer question")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate an answer. Check the server logs.",
        )


@router.post("/ask/stream")
def ask_stream(body: QuestionRequest, pipeline: RAGPipeline = Depends(get_pipeline)):
    """Same answer, streamed as it is written.
    Response: one JSON event per line (NDJSON)."""

    def events():
        try:
            for event in pipeline.stream_answer(body.question):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception:
            logger.exception("Failed to stream answer")
            yield json.dumps({
                "type": "error",
                "message": "Could not generate an answer. Check the server logs.",
            }) + "\n"

    return StreamingResponse(
        events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )