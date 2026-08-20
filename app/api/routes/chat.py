from fastapi import APIRouter, Depends

from app.api.dependencies import get_app_container
from app.core.container import Container
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, container: Container = Depends(get_app_container)) -> ChatResponse:
    return container.chat.ask(request)
