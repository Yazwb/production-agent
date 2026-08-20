from fastapi import APIRouter

from app.api.routes import chat, documents, health

router = APIRouter()
#健康检查接口
router.include_router(health.router, tags=["system"])
#文档管理接口
router.include_router(documents.router, prefix="/documents", tags=["documents"])
#聊天接口
router.include_router(chat.router, prefix="/chat", tags=["chat"])
