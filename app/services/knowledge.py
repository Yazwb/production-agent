from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import Settings
from app.domain.enums import Domain
from app.domain.models import Document
from app.ports.repositories import KnowledgeRepository
from app.rag.chunking import TextChunker
from app.rag.parser import DocumentParser
#返回前端数据结构 
from app.schemas.documents import DocumentListResponse, DocumentResponse


class KnowledgeService:
    # 初始化服务
    def __init__(self, settings: Settings, repository: KnowledgeRepository) -> None:
            self.repository = repository
            self.settings = settings
            self.parser = DocumentParser()
            self.chunker = TextChunker(settings.chunk_size, settings.chunk_overlap)

    def ingest(self, filename: str, content: bytes, domain: Domain) -> DocumentResponse:
            """将文本进行解析，切片，并存储到向量数据库中。"""
            suffix = Path(filename).suffix.lower()
            # 检查文件类型
            if suffix not in self.parser.SUPPORTED_SUFFIXES:
                raise ValueError("仅支持 PDF,Word,TXT,Markdown文件")
            document_id = str(uuid4())
            stored_path = self.settings.upload_dir / f"{document_id}{suffix}"
            # 保存源文件
            stored_path.write_bytes(content)
            pages = self.parser.parse(stored_path)
            chunks= self.chunker.split(document_id, filename, pages)
            document = Document(
                 document_id,
                 filename,
                 str(stored_path),
                 domain,
                 # status当前状态
                 "indexed",
                 len(chunks),
                 datetime.now(UTC),
            )
            # 保存到数据库当中
            self.repository.add_document(document, chunks)
            return self._response(document)      

    def list_documents(self) -> DocumentListResponse:
            items = [self._response(item)
                     for item in self.repository.list_documents()
            ]
            return DocumentListResponse(
                  items=items,
                  total = len(items),
            )

    def delete(self, document_id: str) -> bool:
            document = self.repository.delete_document(document_id)
            if document and Path(document.stored_path).exists():
                Path(document.stored_path).unlink()
            return document is not None

    @staticmethod
    def _response(document: Document) -> DocumentResponse:
          return  DocumentResponse(id=document.id, filename=document.filename, domian=document.domain, 
                                   statuc=document.status, chunk_count=document.chunk_count, created_at=document.created_at)