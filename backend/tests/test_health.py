"""Health check integration tests"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
class TestHealthCheck:
    """Health service integration tests"""

    @patch("app.services.health_service.vector_store")
    @patch("app.services.health_service.redis_client")
    @patch("app.services.health_service.llm_service")
    async def test_all_services_healthy(self, mock_llm, mock_redis, mock_vector):
        """Test health check when all services are up"""
        from app.services.health_service import health_service

        # Mock all dependencies as healthy
        mock_redis.ping = MagicMock(return_value=True)
        mock_vector.get_stats = AsyncMock(return_value={"vectors_count": 100})
        mock_llm.health_check = AsyncMock(return_value=True)

        with patch("app.services.health_service.check_database_health", new_callable=AsyncMock) as mock_db:
            mock_db.return_value = True
            result = await health_service.check_all()

        assert result["status"] == "healthy"
        assert result["services"]["database"] is True
        assert result["services"]["redis"] is True
        assert result["services"]["qdrant"] is True
        assert result["services"]["ollama"] is True

    @patch("app.services.health_service.vector_store")
    @patch("app.services.health_service.redis_client")
    @patch("app.services.health_service.llm_service")
    async def test_partial_failure(self, mock_llm, mock_redis, mock_vector):
        """Test health check when some services are down"""
        from app.services.health_service import health_service

        mock_redis.ping = MagicMock(side_effect=Exception("Connection refused"))
        mock_vector.get_stats = AsyncMock(return_value={"vectors_count": 100})
        mock_llm.health_check = AsyncMock(return_value=False)

        with patch("app.services.health_service.check_database_health", new_callable=AsyncMock) as mock_db:
            mock_db.return_value = True
            result = await health_service.check_all()

        assert result["status"] == "degraded"
        assert result["services"]["redis"] is False
        assert result["services"]["ollama"] is False
        assert result["services"]["database"] is True

    async def test_database_health_check(self):
        """Test database health check with test DB"""
        from app.services.health_service import check_database_health

        result = await check_database_health()
        # Should work with test SQLite DB
        assert result is True
