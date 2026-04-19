"""向量存储服务 - Qdrant 集成"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams, 
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)
from app.core.config import get_settings

settings = get_settings()


class VectorStore:
    """向量存储类"""
    
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            timeout=30
        )
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = 384  # MiniLM 模型维度
        self._ensure_collection()
    
    def _ensure_collection(self):
        """确保集合存在"""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
    
    async def add_vectors(
        self, 
        vectors: List[List[float]], 
        documents: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加向量"""
        points = []
        for i, (vector, doc) in enumerate(zip(vectors, documents)):
            point_id = ids[i] if ids else str(len(points) + 1)
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=doc
                )
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return [p.id for p in points]
    
    async def search(
        self, 
        query_vector: List[float], 
        limit: int = 5,
        filter_conditions: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """语义搜索"""
        search_filter = None
        if filter_conditions:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter_conditions.items()
            ]
            search_filter = Filter(must=conditions)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=search_filter,
            limit=limit,
            with_payload=True
        )
        
        return [
            {
                "id": r.id,
                "score": r.score,
                **r.payload
            }
            for r in results
        ]
    
    async def delete(self, ids: List[str]):
        """删除向量"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids
        )
    
    async def delete_by_document(self, document_id: str):
        """根据文档 ID 删除所有相关向量"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=self.client.query_points(
                collection_name=self.collection_name,
                query_filter=Filter(
                    must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
                )
            ).points
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        info = self.client.get_collection(self.collection_name)
        return {
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "indexed_vectors_count": info.indexed_vectors_count
        }


# 全局单例
vector_store = VectorStore()
