import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.services.vector_store import vector_store
from app.workers.celery_app import celery_app
from app.workers.tasks import process_document_task

settings = get_settings()
router = APIRouter()
logger = logging.getLogger(__name__)


def _build_stored_filename(user_id: str, document_id: str, suffix: str) -> str:
    return f"{user_id}__{document_id}{suffix}"


@router.get("/", summary="获取文档列表")
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户上传的所有文档"""
    stmt = (
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    result = await db.execute(stmt)
    documents = result.scalars().all()

    return {
        "documents": [
            {
                "id": str(doc.id),
                "name": doc.name,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "status": doc.status,
                "chunk_count": doc.chunk_count,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
            }
            for doc in documents
        ]
    }


@router.post("/upload", summary="上传文档")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传文档并进行向量索引"""
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        document_id = str(uuid.uuid4())
        ext = Path(file.filename or "").suffix
        stored_name = _build_stored_filename(str(current_user.id), document_id, ext)
        file_path = upload_dir / stored_name

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 创建数据库记录
        doc = Document(
            id=document_id,
            user_id=current_user.id,
            name=file.filename or stored_name,
            file_path=str(file_path),
            file_type=ext.lstrip("."),
            file_size=len(content),
            status="processing",
        )
        db.add(doc)
        await db.flush()

        task = process_document_task.delay(
            file_path=str(file_path),
            file_name=file.filename or stored_name,
            user_id=str(current_user.id),
            document_id=document_id,
        )

        logger.info("Document uploaded: %s by user %s", file.filename, current_user.username)

        return {
            "message": "Document uploaded successfully",
            "document_id": document_id,
            "filename": file.filename,
            "task_id": task.id,
            "status": "processing",
        }
    except Exception as e:
        logger.error("Document upload failed: %s", e)
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


@router.delete("/{doc_id}", summary="删除文档")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文档及其向量索引"""
    stmt = select(Document).where(
        Document.id == doc_id,
        Document.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 删除文件
    file_path = Path(doc.file_path)
    if file_path.exists():
        file_path.unlink()
        logger.info("File deleted: %s by user %s", doc_id, current_user.username)

    # 删除数据库记录
    await db.delete(doc)

    # 删除向量
    try:
        await vector_store.delete_by_document(doc_id, user_id=str(current_user.id))
        logger.info("Vectors deleted for document: %s", doc_id)
    except Exception as e:
        logger.error("Failed to delete vectors for document %s: %s", doc_id, e)
        return {
            "message": f"Document {doc_id} deleted (vector cleanup may be incomplete)",
            "warning": "Vector deletion failed, manual cleanup may be required",
        }

    return {"message": f"Document {doc_id} deleted"}


@router.post("/{doc_id}/index", summary="索引文档")
async def index_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """重新索引指定文档"""
    stmt = select(Document).where(
        Document.id == doc_id,
        Document.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(doc.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")

    # 更新状态为 processing
    doc.status = "processing"
    await db.flush()

    task = process_document_task.delay(
        file_path=str(file_path),
        file_name=doc.name,
        user_id=str(current_user.id),
        document_id=doc_id,
    )

    logger.info("Document indexing started: %s by user %s", doc_id, current_user.username)

    return {
        "message": f"Document {doc_id} indexing started",
        "task_id": task.id,
    }
