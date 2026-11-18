from fastapi import APIRouter, Depends

from app.api.deps import get_pipeline
from app.schemas.chat import HealthResponse
from app.services.rag_pipeline import RAGPipeline

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(pipeline: RAGPipeline = Depends(get_pipeline)) -> HealthResponse:
    return HealthResponse(status="ok", chunks=len(pipeline.store),
                          llm_enabled=pipeline.llm.enabled)