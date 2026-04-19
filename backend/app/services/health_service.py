"""
健康检查服务
检查所有依赖服务的状态
"""
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime

import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import async_session_maker

settings = get_settings()


class HealthChecker:
    """健康检查器 - 检查所有依赖服务状态"""

    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None

    async def get_redis_client(self) -> redis.Redis:
        """获取 Redis 客户端 (懒加载)"""
        if self._redis_client is None:
            self._redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis_client

    async def check_database(self) -> Dict[str, Any]:
        """检查 PostgreSQL 数据库状态"""
        start_time = time.time()
        try:
            async with async_session_maker() as session:
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                latency = (time.time() - start_time) * 1000
                return {
                    "status": "healthy",
                    "latency_ms": round(latency, 2),
                    "message": "Database connection successful"
                }
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "latency_ms": round(latency, 2),
                "error": str(e),
                "message": "Database connection failed"
            }

    async def check_redis(self) -> Dict[str, Any]:
        """检查 Redis 状态"""
        start_time = time.time()
        try:
            client = await self.get_redis_client()
            await client.ping()
            latency = (time.time() - start_time) * 1000

            # 获取 Redis 信息
            info = await client.info("memory")
            used_memory = info.get("used_memory_human", "unknown")

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "used_memory": used_memory,
                "message": "Redis connection successful"
            }
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "latency_ms": round(latency, 2),
                "error": str(e),
                "message": "Redis connection failed"
            }

    async def check_qdrant(self) -> Dict[str, Any]:
        """检查 Qdrant 向量数据库状态"""
        start_time = time.time()
        try:
            from app.services.vector_store import vector_store

            # 尝试获取集合信息
            collections = await vector_store.get_collections()
            latency = (time.time() - start_time) * 1000

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "collections_count": len(collections),
                "message": "Qdrant connection successful"
            }
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "latency_ms": round(latency, 2),
                "error": str(e),
                "message": "Qdrant connection failed"
            }

    async def check_ollama(self) -> Dict[str, Any]:
        """检查 Ollama LLM 服务状态"""
        start_time = time.time()
        try:
            import httpx

            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
                response.raise_for_status()
                data = response.json()
                latency = (time.time() - start_time) * 1000

                models = data.get("models", [])
                model_names = [m.get("name", "unknown") for m in models]

                return {
                    "status": "healthy",
                    "latency_ms": round(latency, 2),
                    "models_available": len(models),
                    "models": model_names[:5] if model_names else [],  # 只显示前5个
                    "message": "Ollama connection successful"
                }
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return {
                "status": "unhealthy",
                "latency_ms": round(latency, 2),
                "error": str(e),
                "message": "Ollama connection failed"
            }

    async def check_all(self, detailed: bool = False) -> Dict[str, Any]:
        """
        检查所有服务状态

        Args:
            detailed: 是否返回详细信息

        Returns:
            健康状态字典
        """
        checks = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_qdrant(),
            self.check_ollama(),
            return_exceptions=True
        )

        # 处理异常结果
        service_results = {}
        service_names = ["database", "redis", "qdrant", "ollama"]

        all_healthy = True
        for name, result in zip(service_names, checks):
            if isinstance(result, Exception):
                service_results[name] = {
                    "status": "unhealthy",
                    "error": str(result),
                    "message": f"{name} check failed with exception"
                }
                all_healthy = False
            else:
                service_results[name] = result
                if result.get("status") != "healthy":
                    all_healthy = False

        response = {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION
        }

        if detailed:
            response["services"] = service_results
            response["checks_passed"] = sum(
                1 for r in service_results.values() if r.get("status") == "healthy"
            )
            response["checks_failed"] = sum(
                1 for r in service_results.values() if r.get("status") != "healthy"
            )

        return response

    async def close(self):
        """关闭连接"""
        if self._redis_client:
            await self._redis_client.close()


# 单例实例
health_checker = HealthChecker()
