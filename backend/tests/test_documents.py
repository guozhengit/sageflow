"""
文档 API 测试
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import io


class TestDocumentsAPI:
    """文档 API 测试"""

    @pytest.mark.asyncio
    async def test_list_documents_unauthorized(self, client: AsyncClient):
        """测试未认证访问文档列表"""
        response = await client.get("/api/documents/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_documents_authorized(self, client: AsyncClient, auth_headers: dict):
        """测试获取文档列表"""
        response = await client.get("/api/documents/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert isinstance(data["documents"], list)

    @pytest.mark.asyncio
    async def test_upload_document(self, client: AsyncClient, auth_headers: dict):
        """测试上传文档"""
        # 创建模拟文件
        file_content = b"Test document content for RAG testing."
        file = ("test.txt", io.BytesIO(file_content), "text/plain")

        with patch("app.api.documents.process_document_task") as mock_task:
            mock_task.delay.return_value = MagicMock(id="test-task-id")

            response = await client.post(
                "/api/documents/upload",
                files={"file": file},
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert "task_id" in data
        assert data["status"] == "processing"

    @pytest.mark.asyncio
    async def test_upload_document_no_file(self, client: AsyncClient, auth_headers: dict):
        """测试上传无文件"""
        response = await client.post(
            "/api/documents/upload",
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_task_status(self, client: AsyncClient):
        """测试获取任务状态"""
        task_id = "test-task-id"

        with patch("app.api.documents.celery_app") as mock_celery:
            mock_result = MagicMock()
            mock_result.status = "SUCCESS"
            mock_result.ready.return_value = True
            mock_result.result = {"status": "completed"}
            mock_celery.AsyncResult.return_value = mock_result

            response = await client.get(f"/api/documents/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert data["status"] == "SUCCESS"

    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试删除不存在的文档"""
        response = await client.delete(
            "/api/documents/non-existent-doc",
            headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_index_document_not_found(self, client: AsyncClient, auth_headers: dict):
        """测试索引不存在的文档"""
        response = await client.post(
            "/api/documents/non-existent-doc/index",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestDocumentsAuth:
    """文档认证测试"""

    @pytest.mark.asyncio
    async def test_all_endpoints_require_auth(self, client: AsyncClient):
        """测试所有端点需要认证"""
        endpoints = [
            ("GET", "/api/documents/"),
            ("POST", "/api/documents/upload"),
            ("DELETE", "/api/documents/test-doc"),
            ("POST", "/api/documents/test-doc/index"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint)
            elif method == "DELETE":
                response = await client.delete(endpoint)

            assert response.status_code == 401, f"{method} {endpoint} should require auth"
