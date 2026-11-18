from sentence_transformers import CrossEncoder


class Reranker:
    """Cross-encoder: reads (question, passage) together and scores relevance."""

    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    def score(self, question: str, passages: list[str]) -> list[float]:
        if not passages:
            return []
        scores = self.model.predict([(question, p) for p in passages])
        return [float(s) for s in scores]