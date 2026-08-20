import re
import sqlite3
from datetime import datetime
from pathlib import Path

from app.domain.enums import Domain
from app.domain.models import Chunk, Document


class SQLiteKnowledgeRepository:
    """MVP 的持久化适配器；后续可在同一接口下替换为 Milvus + MySQL。"""
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        # 使用 FTS5 保存检索字段，避免 MVP 阶段先引入独立搜索服务。
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY, filename TEXT NOT NULL, stored_path TEXT NOT NULL,
                    domain TEXT NOT NULL, status TEXT NOT NULL, chunk_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    filename TEXT NOT NULL, page_number INTEGER NOT NULL, position INTEGER NOT NULL,
                    text TEXT NOT NULL, search_text TEXT NOT NULL
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED, search_text, tokenize='unicode61'
                );
                """
            )

    def add_document(self, document: Document, chunks: list[Chunk]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?)",
                (document.id, document.filename, document.stored_path, document.domain.value,
                 document.status, document.chunk_count, document.created_at.isoformat()),
            )
            for chunk in chunks:
                search_text = self._tokenize(chunk.text)
                connection.execute(
                    "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (chunk.id, chunk.document_id, chunk.filename, chunk.page_number,
                     chunk.position, chunk.text, search_text),
                )
                connection.execute("INSERT INTO chunks_fts VALUES (?, ?)", (chunk.id, search_text))

    def list_documents(self) -> list[Document]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
        return [self._to_document(row) for row in rows]

    def get_document(self, document_id: str) -> Document | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        return self._to_document(row) if row else None

    def delete_document(self, document_id: str) -> Document | None:
        document = self.get_document(document_id)
        if not document:
            return None
        with self._connect() as connection:
            chunk_ids = [row[0] for row in connection.execute("SELECT id FROM chunks WHERE document_id = ?", (document_id,))]
            connection.executemany("DELETE FROM chunks_fts WHERE chunk_id = ?", [(item,) for item in chunk_ids])
            connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        return document

    def search(self, query: str, top_k: int, domain: str | None = None) -> list[Chunk]:
        # 当前使用 BM25 做关键词召回；生产版本应增加向量召回并做 RRF 融合。
        terms = self._tokenize(query).split()
        if not terms:
            return []
        expression = " OR ".join(f'"{term}"' for term in dict.fromkeys(terms))
        sql = """
            SELECT c.*, bm25(chunks_fts) AS rank
            FROM chunks_fts JOIN chunks c ON c.id = chunks_fts.chunk_id
            JOIN documents d ON d.id = c.document_id
            WHERE chunks_fts MATCH ?
        """
        params: list[object] = [expression]
        if domain:
            sql += " AND d.domain = ?"
            params.append(domain)
        sql += " ORDER BY rank LIMIT ?"
        params.append(top_k)
        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [
            Chunk(row["id"], row["document_id"], row["filename"], row["page_number"],
                  row["position"], row["text"], round(1 / (1 + abs(row["rank"])), 4))
            for row in rows
        ]

    @staticmethod
    def _tokenize(text: str) -> str:
        # SQLite 默认分词对中文支持有限，因此将中文拆成单字以获得基础召回能力。
        latin = re.findall(r"[a-zA-Z0-9_]+", text.lower())
        chinese = [character for character in text if "\u4e00" <= character <= "\u9fff"]
        return " ".join(latin + chinese)

    @staticmethod
    def _to_document(row: sqlite3.Row) -> Document:
        return Document(row["id"], row["filename"], row["stored_path"], Domain(row["domain"]),
                        row["status"], row["chunk_count"], datetime.fromisoformat(row["created_at"]))
