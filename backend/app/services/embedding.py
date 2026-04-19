"""Embedding 服务 - 文本向量化"""
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding 服务类 - 支持懒加载"""

    def __init__(self):
        self._model: Optional[SentenceTransformer] = None
        self._model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        self._dimension = 384

    @property
    def model(self) -> SentenceTransformer:
        """懒加载模型"""
        if self._model is None:
            logger.info(f"Loading embedding model: {self._model_name}")
            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded successfully")
        return self._model

    async def encode(self, text: str) -> List[float]:
        """单文本编码"""
        embedding = self.model.encode([text])[0]
        return embedding.tolist()

    async def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码"""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return [e.tolist() for e in embeddings]

    @property
    def dimension(self) -> int:
        """返回向量维度"""
        return self._dimension

    def preload(self):
        """预加载模型 (可选，用于启动时预热)"""
        _ = self.model
        return self


# 全局单例
embedding_service = EmbeddingService()
