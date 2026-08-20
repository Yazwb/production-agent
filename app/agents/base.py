from app.domain.enums import Domain
from app.domain.models import Chunk
from app.ports.llm import LanguageModel
from app.rag.pipeline import RagPipeline


class DomainAgent:
    """领域 Agent 的最小职责：检索本领域资料并生成回答。"""
    def __init__(self, domain: Domain, rag: RagPipeline, llm: LanguageModel) -> None:
        self.domain = domain
        self.rag = rag
        self.llm = llm

    def run(self, question: str) -> tuple[str, list[Chunk]]:
        # 先检索再生成，确保模型上下文来自知识库而不是凭空回答。
        chunks = self.rag.search(question, self.domain)
        return self.llm.answer(question, chunks), chunks
