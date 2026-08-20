from dataclasses import dataclass
from datetime import datetime

from app.domain.enums import Domain


@dataclass(slots=True)
class ParsedPage:
    page_number: int
    text: str


@dataclass(slots=True)
class Document:
    id: str
    filename: str
    stored_path: str
    domain: Domain
    status: str
    chunk_count: int
    created_at: datetime


@dataclass(slots=True)
class Chunk:
    id: str
    document_id: str
    filename: str
    page_number: int
    position: int
    text: str
    score: float = 0.0
