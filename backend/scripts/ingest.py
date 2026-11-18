"""Build the vector store from files in data/raw.

Run from the backend folder:
    python -m scripts.ingest
"""
import logging

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.services.embeddings import Embedder
from app.services.ingestion.chunker import chunk_documents
from app.services.ingestion.loaders import load_directory
from app.services.vector_store import FaissVectorStore

logger = logging.getLogger("ingest")


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    # 1. Load
    docs = load_directory(settings.raw_data_dir)
    if not docs:
        raise SystemExit(f"No .md, .pdf or .txt files found in {settings.raw_data_dir}")

    # 2. Chunk
    chunks = chunk_documents(docs, settings.chunk_size, settings.chunk_overlap)
    logger.info("Created %d chunks from %d sections", len(chunks), len(docs))

    # 3. Embed
    embedder = Embedder(settings.embed_model)
    vectors = embedder.encode([c.embed_text for c in chunks], show_progress=True)

    # 4. Store
    store = FaissVectorStore.build(vectors, [c.to_dict() for c in chunks])
    store.save(settings.index_path, settings.chunks_path)
    logger.info("Saved vector store to %s", settings.vector_store_dir)


if __name__ == "__main__":
    main()