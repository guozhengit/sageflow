"""WebSocket service integration tests"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.websocket_service import ConnectionManager


class TestConnectionManager:
    """WebSocket ConnectionManager tests"""

    def setup_method(self):
        self.manager = ConnectionManager()

    def test_initial_state(self):
        """Test manager starts with no connections"""
        assert len(self.manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_connect(self):
        """Test adding a WebSocket connection"""
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()

        await self.manager.connect(mock_ws, user_id="user1", session_id="s1")

        mock_ws.accept.assert_called_once()
        assert len(self.manager.active_connections) == 1

    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test removing a WebSocket connection"""
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()

        await self.manager.connect(mock_ws, user_id="user1", session_id="s1")
        self.manager.disconnect(mock_ws)

        assert len(self.manager.active_connections) == 0

    @pytest.mark.asyncio
    async def test_multiple_connections_same_user(self):
        """Test multiple connections from same user"""
        ws1 = MagicMock()
        ws1.accept = AsyncMock()
        ws2 = MagicMock()
        ws2.accept = AsyncMock()

        await self.manager.connect(ws1, user_id="user1", session_id="s1")
        await self.manager.connect(ws2, user_id="user1", session_id="s2")

        assert len(self.manager.active_connections) == 2

    @pytest.mark.asyncio
    async def test_broadcast_to_user(self):
        """Test sending message to all connections of a user"""
        ws1 = MagicMock()
        ws1.accept = AsyncMock()
        ws1.send_json = AsyncMock()
        ws2 = MagicMock()
        ws2.accept = AsyncMock()
        ws2.send_json = AsyncMock()

        await self.manager.connect(ws1, user_id="user1", session_id="s1")
        await self.manager.connect(ws2, user_id="user1", session_id="s2")

        message = {"type": "notification", "data": "test"}
        await self.manager.broadcast_to_user("user1", message)

        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_get_connections_count(self):
        """Test getting active connection count"""
        ws1 = MagicMock()
        ws1.accept = AsyncMock()
        ws2 = MagicMock()
        ws2.accept = AsyncMock()

        await self.manager.connect(ws1, user_id="user1", session_id="s1")
        await self.manager.connect(ws2, user_id="user2", session_id="s2")

        assert self.manager.get_connections_count() == 2
