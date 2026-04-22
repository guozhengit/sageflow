"""Integration tests for document workflow: upload → process → index → delete"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.user import User


@pytest.mark.asyncio
class TestDocumentWorkflow:
    """Document full-lifecycle integration tests"""

    async def test_create_and_query_document(self, db_session: AsyncSession, test_user: User):
        """Test creating a Document ORM record and querying it back"""
        doc = Document(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="test.pdf",
            file_path="/tmp/test.pdf",
            file_type="pdf",
            file_size=1024,
            status="pending",
            chunk_count=0,
        )
        db_session.add(doc)
        await db_session.commit()
        await db_session.refresh(doc)

        # Query back
        stmt = select(Document).where(Document.id == doc.id)
        result = await db_session.execute(stmt)
        fetched = result.scalar_one()

        assert fetched.name == "test.pdf"
        assert fetched.status == "pending"
        assert fetched.user_id == test_user.id
        assert fetched.chunk_count == 0

    async def test_update_document_status(self, db_session: AsyncSession, test_user: User):
        """Test updating document status after processing"""
        doc = Document(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="report.docx",
            file_path="/tmp/report.docx",
            file_type="docx",
            file_size=2048,
            status="processing",
        )
        db_session.add(doc)
        await db_session.commit()

        # Simulate processing completion
        doc.status = "indexed"
        doc.chunk_count = 12
        await db_session.commit()
        await db_session.refresh(doc)

        assert doc.status == "indexed"
        assert doc.chunk_count == 12

    async def test_delete_document_cascade(self, db_session: AsyncSession, test_user: User):
        """Test deleting document record"""
        doc = Document(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="delete-me.txt",
            file_path="/tmp/delete-me.txt",
            file_type="txt",
            file_size=512,
            status="indexed",
            chunk_count=3,
        )
        db_session.add(doc)
        await db_session.commit()
        doc_id = doc.id

        await db_session.delete(doc)
        await db_session.commit()

        stmt = select(Document).where(Document.id == doc_id)
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None

    async def test_list_user_documents(self, db_session: AsyncSession, test_user: User):
        """Test listing documents for a specific user"""
        for i in range(3):
            db_session.add(Document(
                id=uuid.uuid4(),
                user_id=test_user.id,
                name=f"doc_{i}.pdf",
                file_path=f"/tmp/doc_{i}.pdf",
                file_type="pdf",
                file_size=1024 * (i + 1),
                status="indexed",
                chunk_count=i + 1,
            ))
        await db_session.commit()

        stmt = select(Document).where(Document.user_id == test_user.id)
        result = await db_session.execute(stmt)
        docs = result.scalars().all()

        assert len(docs) == 3
        assert all(d.user_id == test_user.id for d in docs)

    async def test_failed_document_status(self, db_session: AsyncSession, test_user: User):
        """Test marking document as failed"""
        doc = Document(
            id=uuid.uuid4(),
            user_id=test_user.id,
            name="corrupt.pdf",
            file_path="/tmp/corrupt.pdf",
            file_type="pdf",
            file_size=100,
            status="processing",
        )
        db_session.add(doc)
        await db_session.commit()

        doc.status = "failed"
        await db_session.commit()
        await db_session.refresh(doc)

        assert doc.status == "failed"
