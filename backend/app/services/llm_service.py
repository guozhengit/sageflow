"""LLM 服务 - Ollama 集成"""
import httpx
from typing import AsyncGenerator
from app.core.config import get_settings

settings = get_settings()


class LLMService:
    """LLM 服务类"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_URL.rstrip('/')
        self.model = settings.LLM_MODEL
    
    async def generate(
        self, 
        prompt: str, 
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        """生成回答"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
            )
            response.raise_for_status()
            return response.json().get("response", "")
    
    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """流式生成回答"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        import json
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue

    # 别名，保持兼容性
    stream_generate = generate_stream
    
    async def check_health(self) -> bool:
        """检查 Ollama 服务健康状态"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


# 全局单例
llm_service = LLMService()
