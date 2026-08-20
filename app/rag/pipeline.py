from app.domain.enums import Domain
from app.domain.models import Chunk
from app.rag.reranker import IdentityReranker
from app.rag.retriever import Retriever


class RagPipeline:
    def __init__(self, retriever: Retriever, reranker: IdentityReranker) -> None:
        self.retriever = retriever
        self.reranker = reranker

    def search(self, question: str, domain: Domain) -> list[Chunk]:
        return self.reranker.rerank(question, self.retriever.retrieve(question, domain))
