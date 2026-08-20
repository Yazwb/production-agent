from app.rag.chunking import TextChunker
from app.domain.models import ParsedPage


def test_chunker_keeps_page_number() -> None:
    chunks = TextChunker(chunk_size=10, overlap=2).split("doc", "manual.txt", [ParsedPage(3, "abcdefghijklmno")])
    assert len(chunks) == 2
    assert all(chunk.page_number == 3 for chunk in chunks)
