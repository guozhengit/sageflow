"""测试 Chat API"""
import pytest
from httpx import AsyncClient


class TestChatEndpoints:
    """Chat API 端点测试"""

    @pytest.mark.asyncio
    async def test_send_message_unauthenticated(self, client: AsyncClient):
        """测试未认证发送消息"""
        response = await client.post(
            "/api/chat/message",
            json={"message": "Hello"}
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_conversations_unauthenticated(self, client: AsyncClient):
        """测试未认证获取对话列表"""
        response = await client.get("/api/chat/conversations")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """测试获取不存在的对话"""
        response = await client.get(
            "/api/chat/conversations/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestHealthCheck:
    """健康检查测试"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查端点"""
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """测试根端点"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
