"""Celery 异步任务"""
import os
import uuid
import asyncio
from pathlib import Path
from celery import current_app

from app.workers.celery_app import celery_app
from app.services.document_processor import document_processor
from app.core.config import get_settings

settings = get_settings()


def run_async(coro):
    """运行异步协程的辅助函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(bind=True)
def process_document_task(
    self,
    file_path: str,
    file_name: str,
    user_id: str = "demo_user"
):
    """异步处理文档任务"""
    try:
        # 使用 asyncio.run() 运行异步方法
        result = asyncio.run(document_processor.process_file(
            file_path=file_path,
            file_name=file_name,
            user_id=user_id
        ))
        return {
            "status": "completed",
            "result": result
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task(bind=True)
def index_document_task(
    self,
    document_id: str,
    user_id: str = "demo_user"
):
    """索引文档任务"""
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        file_path = upload_dir / f"{document_id}"

        if not file_path.exists():
            return {"status": "failed", "error": "File not found"}

        file_name = f"document_{document_id}"
        result = asyncio.run(document_processor.process_file(
            file_path=str(file_path),
            file_name=file_name,
            user_id=user_id
        ))
        return {"status": "completed", "result": result}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
