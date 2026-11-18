import json
from pathlib import Path

import faiss
import numpy as np


class FaissVectorStore:
    """FAISS index for vectors + a list of chunk dicts in the same order."""

    def __init__(self, index: faiss.Index, chunks: list[dict]):
        self.index = index
        self.chunks = chunks

    def __len__(self) -> int:
        return len(self.chunks)

    @classmethod
    def build(cls, vectors: np.ndarray, chunks: list[dict]) -> "FaissVectorStore":
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        return cls(index, chunks)

    def save(self, index_path: Path, chunks_path: Path) -> None:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        chunks_path.write_text(
            json.dumps(self.chunks, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, index_path: Path, chunks_path: Path) -> "FaissVectorStore":
        if not index_path.exists() or not chunks_path.exists():
            raise FileNotFoundError(
                "Vector store not found. Run `python -m scripts.ingest` first."
            )
        index = faiss.read_index(str(index_path))
        chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
        return cls(index, chunks)

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[float, dict]]:
        """Return (score, chunk) pairs, best first."""
        k = min(k, len(self.chunks))
        if k == 0:
            return []
        scores, ids = self.index.search(query_vector, k)
        return [
            (float(score), self.chunks[idx])
            for score, idx in zip(scores[0], ids[0])
            if idx != -1
        ]