from app.agents.base import DomainAgent
from app.agents.router import IntentRouter
from app.domain.enums import Domain
from app.domain.models import Chunk
from app.ports.llm import LanguageModel
from app.rag.pipeline import RagPipeline


class AgentOrchestrator:
    """统一编排入口，后续可替换成 LangGraph 状态图。"""
    def __init__(self, rag: RagPipeline, llm: LanguageModel) -> None:
        self.router = IntentRouter()
        self.agents = {domain: DomainAgent(domain, rag, llm) for domain in Domain if domain is not Domain.AUTO}

    def run(self, question: str, requested: Domain) -> tuple[Domain, str, list[Chunk]]:
        # 先确定领域，再调用对应 Agent；返回领域便于 API 展示实际路由结果。
        domain = self.router.route(question, requested)
        answer, chunks = self.agents[domain].run(question)
        return domain, answer, chunks
