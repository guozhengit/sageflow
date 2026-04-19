"""API 限流服务"""
import time
from typing import Optional, Callable
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from app.core.config import get_settings
from app.core.logging_config import get_logger

settings = get_settings()
logger = get_logger("ratelimit")


class RateLimiter:
    """基于 Redis 的滑动窗口限流器"""

    def __init__(
        self,
        redis_url: str,
        prefix: str = "ratelimit:",
    ):
        self.redis_url = redis_url
        self.prefix = prefix
        self._client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        """获取 Redis 客户端"""
        if self._client is None:
            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        检查是否允许请求

        Returns:
            tuple: (是否允许, 剩余请求数, 重置时间秒数)
        """
        client = await self._get_client()
        now = time.time()
        window_start = now - window_seconds

        full_key = f"{self.prefix}{key}"

        # 使用 Lua 脚本保证原子性
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local max_requests = tonumber(ARGV[3])
        local window_seconds = tonumber(ARGV[4])

        -- 移除窗口外的请求
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

        -- 获取当前请求数
        local current = redis.call('ZCARD', key)

        if current < max_requests then
            -- 添加当前请求
            redis.call('ZADD', key, now, now .. '-' .. math.random())
            redis.call('EXPIRE', key, window_seconds)
            return {1, max_requests - current - 1, window_seconds}
        else
            -- 获取最早的请求时间，计算重置时间
            local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
            local reset_time = window_seconds
            if oldest[2] then
                reset_time = math.ceil(tonumber(oldest[2]) + window_seconds - now)
            end
            return {0, 0, reset_time}
        end
        """

        result = await client.eval(
            lua_script,
            1,
            full_key,
            now,
            window_start,
            max_requests,
            window_seconds
        )

        allowed = bool(result[0])
        remaining = int(result[1])
        reset_time = int(result[2])

        return allowed, remaining, reset_time


# 全局限流器
rate_limiter = RateLimiter(settings.REDIS_URL)


class RateLimitMiddleware:
    """FastAPI 限流中间件"""

    def __init__(
        self,
        app: FastAPI,
        default_limits: Optional[dict] = None
    ):
        self.app = app
        self.default_limits = default_limits or {
            "default": (100, 60),      # 默认: 100 请求/分钟
            "/api/chat": (20, 60),     # 聊天: 20 请求/分钟
            "/api/documents/upload": (10, 60),  # 上传: 10 请求/分钟
            "/api/users/login": (5, 60),        # 登录: 5 请求/分钟
        }

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # 获取客户端 IP
        client_ip = self._get_client_ip(request)

        # 查找匹配的限流规则
        path = scope["path"]
        limit_config = self._get_limit_config(path)

        if limit_config:
            max_requests, window_seconds = limit_config
            key = f"{client_ip}:{path}"

            allowed, remaining, reset_time = await rate_limiter.is_allowed(
                key=key,
                max_requests=max_requests,
                window_seconds=window_seconds
            )

            # 添加限流头
            headers = {
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
            }

            if not allowed:
                logger.warning(f"Rate limit exceeded: {client_ip} -> {path}")
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": {
                            "code": 429,
                            "message": "Too many requests. Please try again later.",
                            "retry_after": reset_time
                        }
                    },
                    headers=headers
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实 IP"""
        # 检查代理头
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 直接连接
        if request.client:
            return request.client.host

        return "unknown"

    def _get_limit_config(self, path: str) -> Optional[tuple]:
        """获取路径对应的限流配置"""
        # 精确匹配
        if path in self.default_limits:
            return self.default_limits[path]

        # 前缀匹配
        for pattern, config in self.default_limits.items():
            if path.startswith(pattern):
                return config

        # 使用默认配置
        return self.default_limits.get("default")


def rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60
):
    """
    限流装饰器 (用于单个路由)

    用法:
        @router.get("/api/limited")
        @rate_limit(max_requests=10, window_seconds=60)
        async def limited_endpoint():
            return {"message": "ok"}
    """
    def decorator(func):
        async def wrapper(*args, request: Request = None, **kwargs):
            # 从参数中获取 request
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request:
                client_ip = request.client.host if request.client else "unknown"
                key = f"{client_ip}:{request.url.path}"

                allowed, remaining, reset_time = await rate_limiter.is_allowed(
                    key=key,
                    max_requests=max_requests,
                    window_seconds=window_seconds
                )

                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Retry after {reset_time} seconds."
                    )

            return await func(*args, **kwargs)

        return wrapper
    return decorator
