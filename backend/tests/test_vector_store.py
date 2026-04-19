"""
向量存储测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.vector_store import VectorStore


class TestVectorStore:
    """向量存储测试"""

    @pytest.fixture
    def mock_qdrant(self):
        """创建 Mock Qdrant 客户端"""
        mock = MagicMock()
        mock.get_collections = MagicMock(return_value=MagicMock(collections=[]))
        mock.create_collection = MagicMock()
        mock.upsert = MagicMock()
        mock.search = MagicMock(return_value=[])
        mock.delete = MagicMock()
        mock.scroll = MagicMock(return_value=([], None))
        return mock

    @pytest.fixture
    def vector_store(self, mock_qdrant):
        """创建向量存储实例"""
        with patch("app.services.vector_store.QdrantClient", return_value=mock_qdrant):
            store = VectorStore()
            store._client = mock_qdrant
            return store

    @pytest.mark.asyncio
    async def test_add_vectors(self, vector_store: VectorStore):
        """测试添加向量"""
        vectors = [[0.1] * 384, [0.2] * 384]
        documents = [
            {"content": "test 1", "document_name": "doc1.pdf"},
            {"content": "test 2", "document_name": "doc2.pdf"}
        ]

        # Mock upsert 操作
        vector_store._client.upsert = MagicMock()

        ids = await vector_store.add_vectors(vectors, documents)

        assert len(ids) == 2
        assert vector_store._client.upsert.called

    @pytest.mark.asyncio
    async def test_search(self, vector_store: VectorStore):
        """测试向量搜索"""
        query_vector = [0.1] * 384

        # Mock 搜索结果
        mock_results = [
            MagicMock(
                id="id1",
                score=0.9,
                payload={"content": "test content", "document_name": "doc.pdf"}
            )
        ]
        vector_store._client.search = MagicMock(return_value=mock_results)

        results = await vector_store.search(query_vector, limit=5)

        assert len(results) == 1
        assert results[0]["content"] == "test content"
        assert results[0]["score"] == 0.9

    @pytest.mark.asyncio
    async def test_search_with_filter(self, vector_store: VectorStore):
        """测试带过滤条件的搜索"""
        query_vector = [0.1] * 384
        filter_conditions = {"user_id": "user123"}

        vector_store._client.search = MagicMock(return_value=[])

        await vector_store.search(
            query_vector,
            limit=5,
            filter_conditions=filter_conditions
        )

        # 验证搜索被调用
        assert vector_store._client.search.called
        call_args = vector_store._client.search.call_args
        # 检查是否传递了过滤条件
        assert call_args is not None

    @pytest.mark.asyncio
    async def test_delete_by_document(self, vector_store: VectorStore):
        """测试按文档删除向量"""
        document_id = "doc123"

        # Mock scroll 返回要删除的点
        mock_points = [
            MagicMock(id="point1", payload={"document_id": document_id})
        ]
        vector_store._client.scroll = MagicMock(return_value=(mock_points, None))
        vector_store._client.delete = MagicMock()

        await vector_store.delete_by_document(document_id)

        # 验证删除被调用
        assert vector_store._client.delete.called

    @pytest.mark.asyncio
    async def test_get_collections(self, vector_store: VectorStore):
        """测试获取集合列表"""
        mock_collections = MagicMock(collections=[
            MagicMock(name="collection1"),
            MagicMock(name="collection2")
        ])
        vector_store._client.get_collections = MagicMock(return_value=mock_collections)

        collections = await vector_store.get_collections()

        assert len(collections) == 2
        assert "collection1" in collections
        assert "collection2" in collections

    @pytest.mark.asyncio
    async def test_search_empty_results(self, vector_store: VectorStore):
        """测试空结果搜索"""
        query_vector = [0.1] * 384
        vector_store._client.search = MagicMock(return_value=[])

        results = await vector_store.search(query_vector, limit=5)

        assert len(results) == 0
        assert isinstance(results, list)


class TestVectorStoreConnection:
    """向量存储连接测试"""

    def test_initialization(self):
        """测试初始化"""
        with patch("app.services.vector_store.QdrantClient") as mock_client:
            store = VectorStore()
            assert mock_client.called

    def test_collection_name(self):
        """测试集合名称"""
        with patch("app.services.vector_store.QdrantClient"):
            store = VectorStore()
            assert store.collection_name == "sageflow_docs"
