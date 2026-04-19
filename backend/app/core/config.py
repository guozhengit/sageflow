from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os
import warnings


class Settings(BaseSettings):
    """应用配置"""

    # 应用
    APP_NAME: str = "SageFlow"
    APP_VERSION: str = "0.6.0"
    DEBUG: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # 数据库
    DATABASE_URL: str = "postgresql://sageflow:sageflow123@postgres:5432/sageflow"

    # Qdrant
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "sageflow_docs"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Ollama
    OLLAMA_URL: str = "http://ollama:11434"
    LLM_MODEL: str = "qwen2.5:3b"

    # JWT - 必须通过环境变量设置
    JWT_SECRET: str = ""  # 无默认值，强制从环境变量获取
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时

    # 文件上传
    MAX_FILE_SIZE: int = 52428800  # 50MB
    UPLOAD_DIR: str = "/app/uploads"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_config()

    def _validate_config(self):
        """验证配置安全性"""
        # 检查 JWT_SECRET
        if not self.JWT_SECRET:
            # 尝试从环境变量获取
            self.JWT_SECRET = os.getenv("JWT_SECRET", "")

        if not self.JWT_SECRET:
            raise ValueError(
                "JWT_SECRET 必须设置！请在 .env 文件或环境变量中配置:\n"
                "  JWT_SECRET=your-secure-secret-key-at-least-32-chars\n"
                "提示: 可以使用 'openssl rand -hex 32' 生成安全密钥"
            )

        # 检查密钥强度
        if len(self.JWT_SECRET) < 32:
            warnings.warn(
                "JWT_SECRET 长度不足 32 字符，建议使用更长的密钥以提高安全性",
                UserWarning
            )

        # 生产环境检查
        if not self.DEBUG:
            if "localhost" in str(self.ALLOWED_ORIGINS):
                warnings.warn(
                    "生产环境中 ALLOWED_ORIGINS 包含 localhost，请检查配置",
                    UserWarning
                )


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
