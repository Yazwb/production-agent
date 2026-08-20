import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.dependencies import get_app_container
from app.core.container import Container
from app.domain.enums import Domain
from app.schemas.documents import DocumentListResponse, DocumentResponse

router = APIRouter()
logger = logging.getLogger(__name__)

#post /upload 接口用于上传文档，支持多种文件格式，上传后会被解析为向量存储在 Milvus 中。
@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload(
    #参数来自上传文件
    file: UploadFile = File(...),
    domain: Domain = Form(Domain.PROCESS),
    container: Container = Depends(get_app_container),
) -> DocumentResponse:
    # 文件读取和解析放在应用服务中，路由层只负责 HTTP 参数和错误码转换。
    try:
        content = await file.read()
        logger.info("Received document upload: %s (%d bytes)", file.filename or "upload.txt", len(content))
        return container.knowledge.ingest(file.filename or "upload.txt", content, domain)
    except ValueError as exc:
        logger.warning("Rejected document upload %s: %s", file.filename or "upload.txt", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc 


@router.get("", response_model=DocumentListResponse)
def list_documents(container: Container = Depends(get_app_container)) -> DocumentListResponse:
    # 前端用这个接口刷新知识库文档列表。
    return container.knowledge.list_documents()


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: str, container: Container = Depends(get_app_container)) -> None:
    # 前端用这个接口删除知识库文档。
    if not container.knowledge.delete(document_id):
        logger.warning("Document not found for deletion: %s", document_id)
        raise HTTPException(status_code=404, detail="Document not found")
    logger.info("Deleted document: %s", document_id)
