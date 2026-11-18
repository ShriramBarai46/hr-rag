from app.services.ingestion.chunker import chunk_documents
from app.services.ingestion.loaders import load_directory, load_markdown


def test_markdown_sections_keep_heading_path(tmp_path):
    md = tmp_path / "handbook.md"
    md.write_text(
        "# Handbook\n## Leave\n### Sick leave\n8 days per year.\n## Salary\nPaid monthly.\n",
        encoding="utf-8",
    )
    docs = load_markdown(md)
    assert [d.section for d in docs] == ["Handbook > Leave > Sick leave", "Handbook > Salary"]
    assert docs[0].text == "8 days per year."


def test_load_directory_skips_unsupported_files(tmp_path):
    (tmp_path / "notes.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    docs = load_directory(tmp_path)
    assert len(docs) == 1 and docs[0].source == "notes.txt"


def test_chunks_have_context_header(tmp_path):
    md = tmp_path / "h.md"
    md.write_text("# H\n## Leave\n" + "word " * 300, encoding="utf-8")
    chunks = chunk_documents(load_markdown(md), chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 1
    assert all(c.embed_text.startswith("h.md > H > Leave: ") for c in chunks)
    assert [c.id for c in chunks] == list(range(len(chunks)))