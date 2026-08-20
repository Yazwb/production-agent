from functools import lru_cache

from app.agents.orchestrator import AgentOrchestrator
from app.core.config import get_settings
from app.infrastructure.llm.vllm import ExtractiveLanguageModel, OpenAICompatibleLanguageModel
from app.infrastructure.repositories.sqlite import SQLiteKnowledgeRepository
from app.rag.pipeline import RagPipeline
from app.rag.reranker import IdentityReranker
from app.rag.retriever import Retriever
from app.services.chat import ChatService
from app.services.knowledge import KnowledgeService


class Container:
    def __init__(self) -> None:
        settings = get_settings()
        settings.prepare_directories()
        self.repository = SQLiteKnowledgeRepository(settings.database_path)
        self.repository.initialize()
        self.retriever = Retriever(self.repository, settings.retrieval_top_k)
        self.rag = RagPipeline(self.retriever, IdentityReranker())
        if settings.llm_base_url:
            llm = OpenAICompatibleLanguageModel(settings.llm_base_url, settings.llm_api_key, settings.llm_model)
        else:
            llm = ExtractiveLanguageModel()
        self.orchestrator = AgentOrchestrator(self.rag, llm)
        self.chat = ChatService(self.orchestrator)
        self.knowledge = KnowledgeService(settings, self.repository)


@lru_cache
def get_container() -> Container:
    return Container()
