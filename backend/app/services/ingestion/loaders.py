import logging
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)

HEADING = re.compile(r"^(#{1,6})\s+(.*)")


@dataclass
class Document:
    """One logical section of a source file (a markdown section, a PDF page, a txt file)."""
    source: str
    section: str
    page: int | None
    text: str


def load_markdown(path: Path) -> list[Document]:
    """Split markdown by headings so each section stays together."""
    docs: list[Document] = []
    stack: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        text = "\n".join(buf).strip()
        if text:
            section = " > ".join(stack) or path.stem
            docs.append(Document(path.name, section, None, text))
        buf.clear()

    for line in path.read_text(encoding="utf-8").splitlines():
        match = HEADING.match(line)
        if match:
            flush()
            level, title = len(match.group(1)), match.group(2).strip()
            stack[:] = stack[: level - 1] + [title]
        else:
            buf.append(line)
    flush()
    return docs


def load_pdf(path: Path) -> list[Document]:
    """One document per page, keeping the page number."""
    reader = PdfReader(str(path))
    docs = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            docs.append(Document(path.name, f"Page {i}", i, text))
    return docs


def load_txt(path: Path) -> list[Document]:
    text = path.read_text(encoding="utf-8").strip()
    return [Document(path.name, path.stem, None, text)] if text else []


LOADERS = {".md": load_markdown, ".pdf": load_pdf, ".txt": load_txt}


def load_directory(directory: Path) -> list[Document]:
    """Load every supported file in a folder."""
    if not directory.exists():
        raise FileNotFoundError(f"Data folder not found: {directory}")

    docs: list[Document] = []
    for path in sorted(directory.iterdir()):
        loader = LOADERS.get(path.suffix.lower())
        if loader is None:
            continue
        file_docs = loader(path)
        docs.extend(file_docs)
        logger.info("Loaded %s (%d sections)", path.name, len(file_docs))
    return docs