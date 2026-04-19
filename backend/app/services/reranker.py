"""重排序服务 - Cross-Encoder 精排"""
from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder
import torch
import logging

logger = logging.getLogger(__name__)


class RerankerService:
    """重排序服务 (Cross-Encoder) - 支持懒加载"""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        初始化重排序服务

        Args:
            model_name: Cross-Encoder 模型名称
                - cross-encoder/ms-marco-MiniLM-L-6-v2 (轻量，~80MB)
                - cross-encoder/ms-marco-MiniLM-L-12-v2 (中等)
                - BAAI/bge-reranker-base (中文友好)
        """
        self._model: Optional[CrossEncoder] = None
        self._model_name = model_name
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

    @property
    def model(self) -> CrossEncoder:
        """懒加载模型"""
        if self._model is None:
            logger.info(f"Loading reranker model: {self._model_name} on {self._device}")
            self._model = CrossEncoder(self._model_name, device=self._device)
            logger.info("Reranker model loaded successfully")
        return self._model

    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        对检索结果进行重排序

        Args:
            query: 用户查询
            documents: 待排序文档列表 (需包含 content 字段)
            top_k: 返回结果数

        Returns:
            重排序后的文档列表 (包含 rerank_score)
        """
        if not documents:
            return []

        # 构建 query-doc 对
        pairs = [(query, doc.get("content", "")) for doc in documents]

        # 计算相关性分数
        scores = self.model.predict(pairs, show_progress_bar=False)

        # 附加分数到文档
        scored_docs = []
        for doc, score in zip(documents, scores):
            doc_copy = doc.copy()
            doc_copy["rerank_score"] = float(score)
            scored_docs.append(doc_copy)

        # 按分数排序
        scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)

        # 返回 top_k
        return scored_docs[:top_k]

    async def rerank_with_threshold(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        threshold: float = 0.0,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        带阈值的重排序

        Args:
            query: 用户查询
            documents: 待排序文档列表
            threshold: 最低分数阈值
            top_k: 返回结果数
        """
        reranked = await self.rerank(query, documents, top_k=len(documents))

        # 过滤低于阈值的文档
        filtered = [doc for doc in reranked if doc.get("rerank_score", 0) >= threshold]

        return filtered[:top_k]

    def preload(self):
        """预加载模型 (可选，用于启动时预热)"""
        _ = self.model
        return self


# 全局单例 (使用轻量级模型)
reranker_service = RerankerService(
    model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
)
