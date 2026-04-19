"""Redis 缓存服务"""
import json
import hashlib
from typing import Optional, Any, List
from datetime import timedelta
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()


class CacheService:
    """Redis 缓存服务"""

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._prefix = "sageflow:cache:"
        self._default_ttl = 3600  # 1 hour

    async def _get_client(self) -> redis.Redis:
        """获取 Redis 客户端 (懒加载)"""
        if self._client is None:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._client

    def _make_key(self, *parts: str) -> str:
        """生成缓存键"""
        return f"{self._prefix}{''.join(parts)}"

    def _hash_key(self, data: str) -> str:
        """生成哈希键 (用于长文本)"""
        return hashlib.md5(data.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            client = await self._get_client()
            value = await client.get(self._make_key(key))
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        try:
            client = await self._get_client()
            cache_key = self._make_key(key)
            cache_value = json.dumps(value, ensure_ascii=False)
            await client.setex(
                cache_key,
                ttl or self._default_ttl,
                cache_value
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            client = await self._get_client()
            await client.delete(self._make_key(key))
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的所有缓存"""
        try:
            client = await self._get_client()
            keys = await client.keys(self._make_key(pattern))
            if keys:
                return await client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            client = await self._get_client()
            return await client.exists(self._make_key(key)) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    async def get_ttl(self, key: str) -> int:
        """获取缓存剩余 TTL (秒)"""
        try:
            client = await self._get_client()
            return await client.ttl(self._make_key(key))
        except Exception as e:
            print(f"Cache get TTL error: {e}")
            return -1


class LLMCacheService:
    """LLM 响应缓存服务"""

    def __init__(self, cache: CacheService):
        self.cache = cache
        self._prefix = "llm:"
        self._ttl = 7200  # 2 hours

    def _make_cache_key(self, prompt: str, model: str) -> str:
        """生成 LLM 缓存键"""
        # 使用 prompt 和 model 生成唯一键
        prompt_hash = self.cache._hash_key(f"{model}:{prompt}")
        return f"{self._prefix}{model}:{prompt_hash}"

    async def get_response(self, prompt: str, model: str) -> Optional[str]:
        """获取缓存的 LLM 响应"""
        key = self._make_cache_key(prompt, model)
        return await self.cache.get(key)

    async def set_response(
        self,
        prompt: str,
        model: str,
        response: str
    ) -> bool:
        """缓存 LLM 响应"""
        key = self._make_cache_key(prompt, model)
        return await self.cache.set(key, response, self._ttl)

    async def clear_model_cache(self, model: str) -> int:
        """清除指定模型的所有缓存"""
        return await self.cache.delete_pattern(f"{self._prefix}{model}:*")


class VectorCacheService:
    """向量检索缓存服务"""

    def __init__(self, cache: CacheService):
        self.cache = cache
        self._prefix = "vector:"
        self._ttl = 3600  # 1 hour

    def _make_cache_key(
        self,
        query: str,
        collection: str,
        top_k: int
    ) -> str:
        """生成向量检索缓存键"""
        query_hash = self.cache._hash_key(f"{collection}:{query}:{top_k}")
        return f"{self._prefix}{collection}:{query_hash}"

    async def get_search_results(
        self,
        query: str,
        collection: str,
        top_k: int
    ) -> Optional[List[dict]]:
        """获取缓存的检索结果"""
        key = self._make_cache_key(query, collection, top_k)
        return await self.cache.get(key)

    async def set_search_results(
        self,
        query: str,
        collection: str,
        top_k: int,
        results: List[dict]
    ) -> bool:
        """缓存检索结果"""
        key = self._make_cache_key(query, collection, top_k)
        return await self.cache.set(key, results, self._ttl)

    async def invalidate_document(self, document_id: str) -> int:
        """使文档相关的所有缓存失效"""
        # 简单实现：清除所有向量缓存
        return await self.cache.delete_pattern(f"{self._prefix}*")


# 全局单例
cache_service = CacheService()
llm_cache = LLMCacheService(cache_service)
vector_cache = VectorCacheService(cache_service)
