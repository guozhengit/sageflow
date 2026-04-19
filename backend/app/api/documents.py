from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import os
import uuid
import logging
from pathlib import Path
from app.core.config import get_settings
from app.core.auth import get_current_user
from app.workers.tasks import process_document_task
from app.workers.celery_app import celery_app
from app.services.vector_store import vector_store
from app.models.user import User

settings = get_settings()
router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", summary="获取文档列表", description="获取当前用户上传的所有文档")
async def list_documents(current_user: User = Depends(get_current_user)):
    """获取文档列表"""
    upload_dir = Path(settings.UPLOAD_DIR)
    documents = []

    if upload_dir.exists():
        for file in upload_dir.iterdir():
            if file.is_file():
                documents.append({
                    "id": file.stem,
                    "name": file.name,
                    "status": "indexed",
                    "file_type": file.suffix,
                    "file_size": file.stat().st_size
                })

    return {"documents": documents}


@router.post("/upload", summary="上传文档", description="上传文档并进行向量索引")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传文档"""
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix if file.filename else ""
        file_name = f"{file_id}{ext}"
        file_path = Path(settings.UPLOAD_DIR) / file_name

        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 异步处理文档
        task = process_document_task.delay(
            file_path=str(file_path),
            file_name=file.filename or "unknown",
            user_id=str(current_user.id)
        )

        logger.info(f"Document uploaded: {file.filename} by user {current_user.username}")

        return {
            "message": "Document uploaded successfully",
            "document_id": file_id,
            "filename": file.filename,
            "task_id": task.id,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    result = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": result.status,
    }
    
    if result.ready():
        response["result"] = result.result
    elif result.failed():
        response["error"] = str(result.result)
    
    return response


@router.delete("/{doc_id}", summary="删除文档", description="删除文档及其向量索引")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除文档（同步删除向量）"""
    file_path = Path(settings.UPLOAD_DIR) / doc_id

    if file_path.exists():
        # 删除文件
        file_path.unlink()
        logger.info(f"File deleted: {doc_id} by user {current_user.username}")

        # 同步删除向量数据库中的相关向量
        try:
            await vector_store.delete_by_document(doc_id)
            logger.info(f"Vectors deleted for document: {doc_id}")
        except Exception as e:
            # 向量删除失败记录日志，但文件已删除
            logger.error(f"Failed to delete vectors for document {doc_id}: {e}")
            return {
                "message": f"Document {doc_id} deleted (vector cleanup may be incomplete)",
                "warning": "Vector deletion failed, manual cleanup may be required"
            }

        return {"message": f"Document {doc_id} deleted"}

    raise HTTPException(status_code=404, detail="Document not found")


@router.post("/{doc_id}/index", summary="索引文档", description="重新索引指定文档")
async def index_document(
    doc_id: str,
    current_user: User = Depends(get_current_user)
):
    """索引文档"""
    file_path = Path(settings.UPLOAD_DIR) / doc_id

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    task = process_document_task.delay(
        file_path=str(file_path),
        file_name=doc_id,
        user_id=str(current_user.id)
    )

    logger.info(f"Document indexing started: {doc_id} by user {current_user.username}")

    return {
        "message": f"Document {doc_id} indexing started",
        "task_id": task.id
    }
