from pydantic import BaseModel, Field

from app.domain.enums import Domain


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    domain: Domain = Domain.AUTO


class SourceResponse(BaseModel):
    document_id: str
    filename: str
    page_number: int
    excerpt: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    agent: str
    sources: list[SourceResponse]
    latency_ms: int
