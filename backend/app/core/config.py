from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ folder (config.py -> core -> app -> backend)
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """All settings. Values are read from backend/.env (env var names are case-insensitive)."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    app_name: str = "HR Handbook Assistant"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173"]

    # LLM (OpenAI)
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float | None = 0.2
    llm_max_tokens: int = 600

    # Local models
    embed_model: str = "all-MiniLM-L6-v2"
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 80

    # Retrieval
    top_k_retrieve: int = 20
    top_k_final: int = 3
    min_rerank_score: float = -3.0

    # Paths
    raw_data_dir: Path = BASE_DIR / "data" / "raw"
    vector_store_dir: Path = BASE_DIR / "data" / "vector_store"

    @property
    def index_path(self) -> Path:
        return self.vector_store_dir / "index.faiss"

    @property
    def chunks_path(self) -> Path:
        return self.vector_store_dir / "chunks.json"


@lru_cache
def get_settings() -> Settings:
    """Create settings once and reuse them everywhere."""
    return Settings()