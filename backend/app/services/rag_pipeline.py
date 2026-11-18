import logging
from collections.abc import Iterator

from app.core.config import Settings
from app.schemas.chat import AnswerResponse, SearchResult, Source
from app.services.embeddings import Embedder
from app.services.llm import LLMClient
from app.services.reranker import Reranker
from app.services.vector_store import FaissVectorStore

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an HR assistant that answers employee questions.
Use ONLY the numbered context passages provided. If the answer is not in them,
say you couldn't find it in the handbook. Keep answers short and clear.
Include any limits, numbers or conditions mentioned in the context.
Cite the passages you used like [1] or [2]."""

NOT_FOUND = "I couldn't find this in the handbook. Try rephrasing, or ask HR directly."
LLM_DISABLED_PREFIX = "(LLM disabled, showing the best matching passage)\n\n"


class RAGPipeline:
    """Question -> embed -> FAISS top-k -> rerank -> top-n -> prompt -> LLM."""

    def __init__(self, settings: Settings, embedder: Embedder, store: FaissVectorStore,
                 reranker: Reranker, llm: LLMClient):
        self.settings = settings
        self.embedder = embedder
        self.store = store
        self.reranker = reranker
        self.llm = llm

    @classmethod
    def from_settings(cls, settings: Settings) -> "RAGPipeline":
        logger.info("Loading vector store from %s", settings.vector_store_dir)
        store = FaissVectorStore.load(settings.index_path, settings.chunks_path)
        logger.info("Loading embedding model %s", settings.embed_model)
        embedder = Embedder(settings.embed_model)
        logger.info("Loading reranker %s", settings.rerank_model)
        reranker = Reranker(settings.rerank_model)
        llm = LLMClient(settings.openai_api_key, settings.llm_model,
                        settings.llm_temperature, settings.llm_max_tokens)
        logger.info("Pipeline ready: %d chunks, LLM %s", len(store),
                    "enabled" if llm.enabled else "disabled")
        return cls(settings, embedder, store, reranker, llm)

    # ---------- retrieval ----------
    def retrieve(self, question: str) -> list[SearchResult]:
        query_vector = self.embedder.encode([question])
        candidates = self.store.search(query_vector, self.settings.top_k_retrieve)
        if not candidates:
            return []

        rerank_scores = self.reranker.score(question, [c["embed_text"] for _, c in candidates])

        results = [
            SearchResult(
                source=chunk["source"],
                section=chunk["section"],
                page=chunk["page"],
                text=chunk["text"],
                vector_rank=rank,
                vector_score=round(vec_score, 4),
                rerank_score=round(rr_score, 4),
            )
            for rank, ((vec_score, chunk), rr_score)
            in enumerate(zip(candidates, rerank_scores), start=1)
        ]
        results.sort(key=lambda r: r.rerank_score, reverse=True)
        return results

    # ---------- shared helpers ----------
    def _select_context(self, question: str) -> list[SearchResult] | None:
        """Top-n results, or None when nothing is relevant enough."""
        top = self.retrieve(question)[: self.settings.top_k_final]
        if not top or top[0].rerank_score < self.settings.min_rerank_score:
            logger.info("No relevant context for question (best score below threshold)")
            return None
        return top

    @staticmethod
    def _build_prompt(question: str, top: list[SearchResult]) -> str:
        context = "\n\n".join(
            f"[{n}] ({r.section})\n{r.text}" for n, r in enumerate(top, start=1)
        )
        return f"Context:\n{context}\n\nQuestion: {question}"

    @staticmethod
    def _to_sources(top: list[SearchResult]) -> list[Source]:
        return [
            Source(n=n, source=r.source, section=r.section, page=r.page, text=r.text,
                   rerank_score=r.rerank_score, vector_rank=r.vector_rank)
            for n, r in enumerate(top, start=1)
        ]

    # ---------- whole answer (POST /ask) ----------
    def answer(self, question: str) -> AnswerResponse:
        top = self._select_context(question)
        if top is None:
            return AnswerResponse(answer=NOT_FOUND, found=False, sources=[])

        if self.llm.enabled:
            answer = self.llm.generate(SYSTEM_PROMPT, self._build_prompt(question, top))
        else:
            answer = LLM_DISABLED_PREFIX + top[0].text

        return AnswerResponse(answer=answer, found=True, sources=self._to_sources(top))

    # ---------- streamed answer (POST /ask/stream) ----------
    def stream_answer(self, question: str) -> Iterator[dict]:
        """Yield events as the answer is produced:
        status(searching) -> sources -> status(writing) -> token... -> done
        """
        yield {"type": "status", "stage": "searching"}

        top = self._select_context(question)
        if top is None:
            yield {"type": "sources", "found": False, "sources": []}
            yield {"type": "token", "text": NOT_FOUND}
            yield {"type": "done"}
            return

        sources = [s.model_dump() for s in self._to_sources(top)]
        yield {"type": "sources", "found": True, "sources": sources}
        yield {"type": "status", "stage": "writing"}

        if self.llm.enabled:
            for piece in self.llm.stream(SYSTEM_PROMPT, self._build_prompt(question, top)):
                yield {"type": "token", "text": piece}
        else:
            yield {"type": "token", "text": LLM_DISABLED_PREFIX + top[0].text}

        yield {"type": "done"}