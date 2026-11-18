from dataclasses import asdict, dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.ingestion.loaders import Document


@dataclass
class Chunk:
    id: int
    source: str
    section: str
    page: int | None
    text: str          # clean text, shown to users
    embed_text: str    # text with context header, used for embedding + reranking

    def to_dict(self) -> dict:
        return asdict(self)


def chunk_documents(docs: list[Document], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Recursive chunking with overlap + a context header on every chunk."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks: list[Chunk] = []
    for doc in docs:
        for piece in splitter.split_text(doc.text):
            chunks.append(
                Chunk(
                    id=len(chunks),
                    source=doc.source,
                    section=doc.section,
                    page=doc.page,
                    text=piece,
                    embed_text=f"{doc.source} > {doc.section}: {piece}",
                )
            )
    return chunks