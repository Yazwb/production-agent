from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import Domain


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    domain: Domain
    status: str
    chunk_count: int
    created_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
