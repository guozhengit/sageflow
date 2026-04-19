"""混合检索服务 - BM25 + 向量检索"""
import re
import math
from typing import List, Dict, Any
from collections import Counter
from app.services.vector_store import vector_store


class BM25Search:
    """BM25 关键词检索"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1  # 词频饱和参数
        self.b = b    # 文档长度归一化参数
        self.documents: List[Dict[str, Any]] = []
        self.doc_freqs: List[Counter] = []
        self.avg_doc_length: float = 0
        self.total_docs: int = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词 (支持中英文)"""
        # 英文按空格和标点分词
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text.lower())
        # 中文逐字分词 (简单方案)
        tokens = []
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                tokens.append(char)
            elif char.strip():
                tokens.extend(char.split())
        return tokens
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """添加文档到索引"""
        for doc in documents:
            content = doc.get("content", "")
            tokens = self._tokenize(content)
            self.documents.append(doc)
            self.doc_freqs.append(Counter(tokens))
        
        self.total_docs = len(self.documents)
        if self.total_docs > 0:
            total_length = sum(len(df) for df in self.doc_freqs)
            self.avg_doc_length = total_length / self.total_docs
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """BM25 检索"""
        query_tokens = self._tokenize(query)
        scores = []
        
        for i, doc_freq in enumerate(self.doc_freqs):
            score = 0
            doc_length = len(doc_freq)
            
            for token in query_tokens:
                if token in doc_freq:
                    # 计算 IDF
                    df = sum(1 for df in self.doc_freqs if token in df)
                    idf = math.log((self.total_docs - df + 0.5) / (df + 0.5) + 1)
                    
                    # 计算 TF
                    tf = doc_freq[token]
                    tf_score = (self.k1 + 1) * tf / (self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length) + tf)
                    
                    score += idf * tf_score
            
            scores.append((i, score))
        
        # 按分数排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回 top_k
        results = []
        for idx, score in scores[:top_k]:
            if score > 0:
                result = self.documents[idx].copy()
                result["bm25_score"] = score
                results.append(result)
        
        return results


class HybridSearch:
    """混合检索: BM25 + 向量检索"""
    
    def __init__(self):
        self.bm25 = BM25Search()
        self._vector_store = vector_store
        self._index_built = False
    
    async def add_documents(self, documents: List[Dict[str, Any]], vectors: List[List[float]]):
        """添加文档 (同时构建 BM25 和向量索引)"""
        # 添加到向量数据库
        await self._vector_store.add_vectors(vectors, documents)
        
        # 添加到 BM25 索引
        self.bm25.add_documents(documents)
        self._index_built = True
    
    async def search(
        self,
        query: str,
        query_vector: List[float],
        top_k: int = 5,
        alpha: float = 0.7,  # 向量检索权重 (0-1)
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        混合检索
        
        Args:
            query: 查询文本
            query_vector: 查询向量
            top_k: 返回结果数
            alpha: 向量检索权重 (1-alpha 为 BM25 权重)
            score_threshold: 最低分数阈值
        """
        # 1. 向量检索
        vector_results = await self._vector_store.search(
            query_vector=query_vector,
            limit=top_k * 2  # 多召回一些用于融合
        )
        
        # 2. BM25 检索
        bm25_results = self.bm25.search(query, top_k=top_k * 2)
        
        # 3. 结果融合 (RRF - Reciprocal Rank Fusion)
        combined_scores: Dict[str, float] = {}
        result_map: Dict[str, Dict[str, Any]] = {}
        
        # 向量检索分数
        for rank, result in enumerate(vector_results, 1):
            doc_id = str(result.get("document_id", result.get("id", "")))
            normalized_score = result.get("score", 0) / max(r.get("score", 1) for r in vector_results) if vector_results else 0
            vector_score = alpha * normalized_score
            
            if doc_id not in combined_scores:
                combined_scores[doc_id] = 0
                result_map[doc_id] = result
            combined_scores[doc_id] += vector_score
        
        # BM25 分数
        for rank, result in enumerate(bm25_results, 1):
            doc_id = str(result.get("document_id", result.get("id", "")))
            max_bm25 = max(r.get("bm25_score", 1) for r in bm25_results) if bm25_results else 1
            normalized_score = result.get("bm25_score", 0) / max_bm25
            bm25_score = (1 - alpha) * normalized_score
            
            if doc_id not in combined_scores:
                combined_scores[doc_id] = 0
                result_map[doc_id] = result
            combined_scores[doc_id] += bm25_score
        
        # 4. 排序和过滤
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 5. 应用阈值
        final_results = []
        for doc_id, score in sorted_results[:top_k]:
            if score >= score_threshold:
                result = result_map[doc_id].copy()
                result["hybrid_score"] = score
                final_results.append(result)
        
        return final_results


# 全局单例
hybrid_search = HybridSearch()
