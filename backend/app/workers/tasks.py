"""Celery async tasks"""
import asyncio
import logging
from pathlib import Path

from app.core.config import get_settings
from app.services.document_processor import document_processor
from app.workers.celery_app import celery_app

settings = get_settings()
logger = logging.getLogger(__name__)


async def _update_document_status(document_id: str, status: str, chunk_count: int = 0):
    """Update document status in database"""
    from app.core.database import async_session
    from app.models.document import Document

    async with async_session() as session:
        try:
            stmt = "UPDATE documents SET status = :status, chunk_count = :chunk_count WHERE id = :id"
            from sqlalchemy import text
            await session.execute(
                text(stmt),
                {"status": status, "chunk_count": chunk_count, "id": document_id},
            )
            await session.commit()
        except Exception as e:
            logger.error("Failed to update document status: %s", e)
            await session.rollback()


@celery_app.task(bind=True)
def process_document_task(
    self,
    file_path: str,
    file_name: str,
    user_id: str = "demo_user",
    document_id: str | None = None,
):
    """Process document: extract, chunk, embed, and index"""
    try:
        result = asyncio.run(document_processor.process_file(
            file_path=file_path,
            file_name=file_name,
            user_id=user_id,
            document_id=document_id,
        ))

        # Update document status in DB
        chunks_count = result.get("chunks_count", 0)
        if document_id:
            asyncio.run(_update_document_status(document_id, "indexed", chunks_count))

        return {"status": "completed", "result": result}
    except Exception as e:
        if document_id:
            asyncio.run(_update_document_status(document_id, "failed"))
        return {"status": "failed", "error": str(e)}


@celery_app.task(bind=True)
def index_document_task(
    self,
    document_id: str,
    file_path: str | None = None,
    file_name: str | None = None,
    user_id: str = "demo_user",
):
    """Index document task"""
    try:
        resolved_file_path = Path(file_path) if file_path else (Path(settings.UPLOAD_DIR) / document_id)

        if not resolved_file_path.exists():
            return {"status": "failed", "error": "File not found"}

        resolved_file_name = file_name or resolved_file_path.name
        result = asyncio.run(document_processor.process_file(
            file_path=str(resolved_file_path),
            file_name=resolved_file_name,
            user_id=user_id,
            document_id=document_id,
        ))

        chunks_count = result.get("chunks_count", 0)
        asyncio.run(_update_document_status(document_id, "indexed", chunks_count))

        return {"status": "completed", "result": result}
    except Exception as e:
        asyncio.run(_update_document_status(document_id, "failed"))
        return {"status": "failed", "error": str(e)}
