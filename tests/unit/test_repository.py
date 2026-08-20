from pathlib import Path

from app.domain.enums import Domain
from app.domain.models import Chunk, Document
from app.infrastructure.repositories.sqlite import SQLiteKnowledgeRepository


def test_sqlite_search(tmp_path: Path) -> None:
    repo = SQLiteKnowledgeRepository(tmp_path / "test.db")
    repo.initialize()
    document = Document("d1", "manual.txt", "manual.txt", Domain.EQUIPMENT, "indexed", 1, __import__("datetime").datetime.now(__import__("datetime").UTC))
    repo.add_document(document, [Chunk("c1", "d1", "manual.txt", 2, 0, "主轴振动过高时检查轴承")])
    results = repo.search("振动 轴承", 5)
    assert results and results[0].document_id == "d1"
