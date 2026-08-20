from time import perf_counter

from app.agents.orchestrator import AgentOrchestrator
from app.schemas.chat import ChatRequest, ChatResponse, SourceResponse


class ChatService:
    def __init__(self, orchestrator: AgentOrchestrator) -> None:
        self.orchestrator = orchestrator

    def ask(self, request: ChatRequest) -> ChatResponse:
        # 这里记录端到端耗时，后续可替换为 OpenTelemetry span。
        started = perf_counter()
        domain, answer, chunks = self.orchestrator.run(request.question, request.domain)
        sources = [
            SourceResponse(document_id=c.document_id, filename=c.filename, page_number=c.page_number,
                           excerpt=c.text[:240], score=c.score)
            for c in chunks
        ]
        return ChatResponse(answer=answer, agent=f"{domain.value}-agent", sources=sources,
                            latency_ms=int((perf_counter() - started) * 1000))
