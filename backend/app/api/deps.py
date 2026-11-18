from fastapi import Request

from app.services.rag_pipeline import RAGPipeline


def get_pipeline(request: Request) -> RAGPipeline:
    """The pipeline is created once at startup and stored on app.state."""
    return request.app.state.pipeline