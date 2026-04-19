"""
RAG 服务测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.rag_service import RAGService


class TestRAGService:
    """RAG 服务测试"""

    @pytest.fixture
    def rag_service(self):
        """创建 RAG 服务实例"""
        service = RAGService()
        # Mock 依赖服务
        service._vector_store = MagicMock()
        service._llm_service = MagicMock()
        service._reranker = MagicMock()
        service.embedding_service = MagicMock()
        service._llm_cache = MagicMock()
        service._vector_cache = MagicMock()
        return service

    @pytest.mark.asyncio
    async def test_query_basic(self, rag_service: RAGService):
        """测试基本查询"""
        # Mock 嵌入服务
        rag_service.embedding_service.encode = AsyncMock(return_value=[0.1] * 384)

        # Mock 向量搜索
        rag_service._vector_store.search = AsyncMock(return_value=[
            {
                "content": "RAG 是检索增强生成技术",
                "document_name": "rag_intro.pdf",
                "page": 1,
                "score": 0.9
            }
        ])

        # Mock 重排序
        rag_service._reranker.rerank_with_threshold = AsyncMock(return_value=[
            {
                "content": "RAG 是检索增强生成技术",
                "document_name": "rag_intro.pdf",
                "page": 1,
                "rerank_score": 0.95
            }
        ])

        # Mock LLM 缓存 (未命中)
        rag_service._llm_cache.get_response = AsyncMock(return_value=None)
        rag_service._llm_cache.set_response = AsyncMock(return_value=True)

        # Mock LLM 生成
        rag_service._llm_service.generate = AsyncMock(
            return_value="RAG 是一种检索增强生成技术，结合了检索和生成的优势。"
        )
        rag_service._llm_service.model = "test-model"

        # Mock 向量缓存
        rag_service._vector_cache.get_search_results = AsyncMock(return_value=None)
        rag_service._vector_cache.set_search_results = AsyncMock(return_value=True)

        # 执行查询
        result = await rag_service.query("什么是 RAG？")

        # 验证结果
        assert "answer" in result
        assert "sources" in result
        assert len(result["sources"]) == 1
        assert result["sources"][0]["document"] == "rag_intro.pdf"

    @pytest.mark.asyncio
    async def test_query_with_cache_hit(self, rag_service: RAGService):
        """测试缓存命中"""
        rag_service.enable_cache = True

        # Mock 向量缓存
        rag_service._vector_cache.get_search_results = AsyncMock(return_value=[
            {"content": "Cached result", "document_name": "doc.pdf", "score": 0.9}
        ])

        # Mock 嵌入服务
        rag_service.embedding_service.encode = AsyncMock(return_value=[0.1] * 384)

        # Mock 重排序
        rag_service._reranker.rerank_with_threshold = AsyncMock(return_value=[
            {"content": "Cached result", "document_name": "doc.pdf", "rerank_score": 0.9}
        ])

        # Mock LLM 缓存命中
        rag_service._llm_cache.get_response = AsyncMock(
            return_value="Cached answer"
        )
        rag_service._llm_service.model = "test-model"

        result = await rag_service.query("test query")

        assert result["answer"] == "Cached answer"

    @pytest.mark.asyncio
    async def test_query_rewrite(self, rag_service: RAGService):
        """测试查询重写"""
        rag_service.embedding_service.encode = AsyncMock(return_value=[0.1] * 384)
        rag_service._vector_store.search = AsyncMock(return_value=[])
        rag_service._reranker.rerank_with_threshold = AsyncMock(return_value=[])
        rag_service._llm_cache.get_response = AsyncMock(return_value=None)
        rag_service._llm_service.model = "test-model"

        # Mock 查询重写
        rag_service._llm_service.generate = AsyncMock(
            return_value="RAG 技术有什么优势？"
        )

        # Mock 向量缓存
        rag_service._vector_cache.get_search_results = AsyncMock(return_value=None)
        rag_service._vector_cache.set_search_results = AsyncMock(return_value=True)
        rag_service._llm_cache.set_response = AsyncMock(return_value=True)

        history = [
            {"role": "user", "content": "什么是 RAG？"},
            {"role": "assistant", "content": "RAG 是检索增强生成..."}
        ]

        result = await rag_service.query(
            "它有什么优势？",
            conversation_history=history
        )

        # 查询重写应该被调用
        assert rag_service._llm_service.generate.called


class TestRAGPromptBuilding:
    """RAG Prompt 构建测试"""

    @pytest.fixture
    def rag_service(self):
        return RAGService()

    def test_build_prompt_basic(self, rag_service: RAGService):
        """测试基本 Prompt 构建"""
        prompt = rag_service._build_prompt(
            question="什么是 RAG？",
            context="RAG 是检索增强生成技术。"
        )

        assert "什么是 RAG？" in prompt
        assert "RAG 是检索增强生成技术" in prompt

    def test_build_prompt_with_history(self, rag_service: RAGService):
        """测试带历史的 Prompt 构建"""
        history = [
            {"role": "user", "content": "什么是 RAG？"},
            {"role": "assistant", "content": "RAG 是检索增强生成技术。"}
        ]

        prompt = rag_service._build_prompt_with_history(
            question="它有什么优势？",
            context="RAG 的优势包括...",
            history=history
        )

        assert "它有什么优势？" in prompt
        assert "对话历史" in prompt
        assert "什么是 RAG？" in prompt

    def test_build_context(self, rag_service: RAGService):
        """测试上下文构建"""
        search_results = [
            {"document_name": "doc1.pdf", "content": "内容1"},
            {"document_name": "doc2.pdf", "content": "内容2"}
        ]

        context = rag_service._build_context(search_results)

        assert "doc1.pdf" in context
        assert "doc2.pdf" in context
        assert "内容1" in context
        assert "内容2" in context
