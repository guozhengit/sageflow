"""Rate limiter integration tests"""
import pytest
import time
from unittest.mock import MagicMock, patch


@pytest.mark.asyncio
class TestRateLimiter:
    """Rate limiter middleware tests"""

    def test_rate_limit_config_defaults(self):
        """Test rate limit configuration has sensible defaults"""
        from app.core.rate_limit import RateLimitMiddleware

        # Verify the middleware can be instantiated
        app = MagicMock()
        middleware = RateLimitMiddleware(app)
        assert middleware is not None

    @patch("app.core.rate_limit.redis_client")
    def test_rate_limit_allows_request_within_limit(self, mock_redis):
        """Test that requests within limit are allowed"""
        mock_redis.evalsha = MagicMock(return_value=0)

        from app.core.rate_limit import RateLimiter
        limiter = RateLimiter()

        # Within limit should return False (not limited)
        mock_redis.evalsha.return_value = 0
        result = limiter.is_limited("test-key", limit=10, window=60)
        assert result is False

    @patch("app.core.rate_limit.redis_client")
    def test_rate_limit_blocks_request_over_limit(self, mock_redis):
        """Test that requests over limit are blocked"""
        from app.core.rate_limit import RateLimiter
        limiter = RateLimiter()

        # Over limit should return True (limited)
        mock_redis.evalsha.return_value = 1
        result = limiter.is_limited("test-key", limit=10, window=60)
        assert result is True

    @patch("app.core.rate_limit.redis_client")
    def test_rate_limit_fail_open_on_redis_error(self, mock_redis):
        """Test that rate limiter fails open when Redis is unavailable"""
        from app.core.rate_limit import RateLimiter
        limiter = RateLimiter()

        # Redis error should fail open (allow request)
        mock_redis.evalsha.side_effect = Exception("Redis connection failed")
        result = limiter.is_limited("test-key", limit=10, window=60)
        assert result is False


@pytest.mark.asyncio
class TestRateLimitPerPath:
    """Test per-path rate limit configuration"""

    def test_path_limits_defined(self):
        """Test that rate limits are defined for key paths"""
        from app.core.rate_limit import PATH_LIMITS

        # Check that critical paths have rate limits
        assert "/api/chat/message" in PATH_LIMITS or "/api/chat/stream" in PATH_LIMITS
        assert "/api/documents/upload" in PATH_LIMITS
