"""Show how your documents are chunked. No models, no API key needed.

Run from the backend folder:
    python -m scripts.inspect_chunks
    python -m scripts.inspect_chunks --size 100 --overlap 30
"""
import argparse

from app.core.config import get_settings
from app.services.ingestion.chunker import chunk_documents
from app.services.ingestion.loaders import load_directory


def main() -> None:
    settings = get_settings()

    parser = argparse.ArgumentParser(description="Inspect chunking")
    parser.add_argument("--size", type=int, default=settings.chunk_size)
    parser.add_argument("--overlap", type=int, default=settings.chunk_overlap)
    args = parser.parse_args()

    docs = load_directory(settings.raw_data_dir)
    chunks = chunk_documents(docs, args.size, args.overlap)

    print(f"chunk_size={args.size}  chunk_overlap={args.overlap}")
    print(f"{len(docs)} sections -> {len(chunks)} chunks\n")

    for c in chunks:
        short_section = c.section.split(" > ")[-1]
        print(f"[{c.id}] {short_section}  ({len(c.text)} chars)")
        print(f"    {c.text}\n")

    sizes = [len(c.text) for c in chunks]
    print(f"Smallest: {min(sizes)} | Largest: {max(sizes)} | Average: {sum(sizes) // len(sizes)} chars")

    too_big = [c.id for c in chunks if len(c.text) > args.size]
    print("OK: all chunks within the size limit" if not too_big else f"WARNING: chunks over limit: {too_big}")


if __name__ == "__main__":
    main()