"""Retrieval check: is the expected page/section in the top-n? No LLM calls.

Run from the backend folder:
    python -m scripts.evaluate
"""
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.services.rag_pipeline import RAGPipeline

# (question, text that should appear in the correct result's section label)
TEST_CASES = [
    ("How many earned leaves do I get in a year?", "Page 4"),
    ("Do I get leave on my birthday?", "Page 4"),
    ("How many casual leaves are allowed in a year?", "Page 4"),
    ("How many leaves can I carry forward to next year?", "Page 5"),
    ("What happens if I am absent for more than 5 days without informing?", "Page 5"),
    ("How long is maternity leave?", "Page 6"),
    ("What are the office timings?", "Page 7"),
    ("Which Saturday is off?", "Page 8"),
    ("When is the lunch break?", "Page 8"),
    ("How many times in a month can I come late?", "Page 9"),
    ("How long is the probation period?", "Page 13"),
    ("What can I wear to office on Saturday?", "Page 13"),
    ("What is the bike allowance per km?", "Page 18"),
]


def main() -> None:
    settings = get_settings()
    setup_logging("WARNING")
    pipeline = RAGPipeline.from_settings(settings)
    n_final = settings.top_k_final

    vector_hits = rerank_hits = 0
    for question, expected in TEST_CASES:
        results = pipeline.retrieve(question)
        by_vector = sorted(results, key=lambda r: r.vector_rank)[:n_final]
        by_rerank = results[:n_final]

        v_hit = any(expected.lower() in r.section.lower() for r in by_vector)
        r_hit = any(expected.lower() in r.section.lower() for r in by_rerank)
        vector_hits += v_hit
        rerank_hits += r_hit

        top = by_rerank[0] if by_rerank else None
        label = f"{top.section} (score {top.rerank_score})" if top else "no results"
        print(f"{'OK  ' if r_hit else 'MISS'} {question}\n      -> {label}")

    total = len(TEST_CASES)
    print(f"\nHit rate @top{n_final}: vector only {vector_hits}/{total}, "
          f"with reranking {rerank_hits}/{total}")


if __name__ == "__main__":
    main()