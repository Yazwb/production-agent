from app.domain.models import Chunk


class IdentityReranker:
    """MVP placeholder; replace with BGE-Reranker after retrieval evaluation."""

    def rerank(self, _: str, chunks: list[Chunk]) -> list[Chunk]:
        return chunks
