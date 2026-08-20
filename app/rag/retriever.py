from app.domain.enums import Domain
from app.domain.models import Chunk
from app.ports.repositories import KnowledgeRepository


class Retriever:
    def __init__(self, repository: KnowledgeRepository, top_k: int) -> None:
        self.repository = repository
        self.top_k = top_k

    def retrieve(self, query: str, domain: Domain) -> list[Chunk]:
        domain_filter = None if domain is Domain.AUTO else domain.value
        return self.repository.search(query, self.top_k, domain_filter)
