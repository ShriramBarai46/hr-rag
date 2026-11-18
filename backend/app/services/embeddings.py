import numpy as np
from sentence_transformers import SentenceTransformer


class Embedder:
    """Turns text into normalized float32 vectors (inner product = cosine similarity)."""

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str], show_progress: bool = False) -> np.ndarray:
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
        )
        return vectors.astype("float32")