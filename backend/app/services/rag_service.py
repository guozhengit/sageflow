"""RAG 服务 - 检索增强生成核心逻辑"""
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.services.embedding import embedding_service
from app.services.reranker import reranker_service
from app.services.cache_service import llm_cache, vector_cache


class RAGService:
    """RAG 服务类"""

    def __init__(self):
        self.embedding_service = embedding_service
        self._vector_store = vector_store
        self._llm_service = llm_service
        self._reranker = reranker_service
        self._llm_cache = llm_cache
        self._vector_cache = vector_cache

        # RAG 配置
        self.retrieval_top_k = 10  # 初始检索数量
        self.rerank_top_k = 3      # 重排序后保留数量
        self.score_threshold = 0.0 # 最低分数阈值
        self.use_reranker = True   # 是否启用重排序
        self.history_turns = 3     # 历史对话轮数
        self.enable_cache = True   # 是否启用缓存

    async def query(
        self,
        question: str,
        top_k: int = 3,
        user_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        执行 RAG 查询

        Args:
            question: 当前问题
            top_k: 返回结果数
            user_id: 用户 ID
            conversation_history: 对话历史 [{"role": "user/assistant", "content": "..."}]
        """

        # 1. 查询重写 (利用对话历史)
        rewritten_question = await self._rewrite_query(question, conversation_history)

        # 2. 将问题向量化
        query_vector = await self.embedding_service.encode(rewritten_question)

        # 3. 尝试从缓存获取检索结果
        search_results = None
        if self.enable_cache:
            cache_key = f"{rewritten_question}:{user_id or 'public'}"
            search_results = await self._vector_cache.get_search_results(
                query=cache_key,
                collection="sageflow_docs",
                top_k=self.retrieval_top_k
            )

        if not search_results:
            # 3.1 缓存未命中，执行检索
            filter_conditions = {"user_id": user_id} if user_id else None
            search_results = await self._vector_store.search(
                query_vector=query_vector,
                limit=self.retrieval_top_k,
                filter_conditions=filter_conditions
            )

            # 缓存检索结果
            if self.enable_cache and search_results:
                await self._vector_cache.set_search_results(
                    query=cache_key,
                    collection="sageflow_docs",
                    top_k=self.retrieval_top_k,
                    results=search_results
                )

        # 4. 重排序 (如果启用)
        if self.use_reranker and search_results:
            search_results = await self._reranker.rerank_with_threshold(
                query=rewritten_question,  # 使用重写后的问题
                documents=search_results,
                threshold=self.score_threshold,
                top_k=top_k
            )
        else:
            search_results = search_results[:top_k]

        # 5. 构建 Prompt (包含对话历史)
        context = self._build_context(search_results)
        prompt = self._build_prompt_with_history(
            question=rewritten_question,
            context=context,
            history=conversation_history
        )

        # 6. 尝试从缓存获取 LLM 响应
        answer = None
        if self.enable_cache:
            answer = await self._llm_cache.get_response(
                prompt=prompt,
                model=self._llm_service.model
            )

        if not answer:
            # 6.1 缓存未命中，调用 LLM
            answer = await self._llm_service.generate(prompt)

            # 缓存 LLM 响应
            if self.enable_cache and answer:
                await self._llm_cache.set_response(
                    prompt=prompt,
                    model=self._llm_service.model,
                    response=answer
                )

        # 7. 构建来源信息
        sources = [
            {
                "document": r.get("document_name", "Unknown"),
                "page": r.get("page", 0),
                "content": r.get("content", "")[:200] + "...",
                "score": r.get("rerank_score") or r.get("score", 0)
            }
            for r in search_results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "context": context,
            "rewritten_query": rewritten_question if rewritten_question != question else None,
            "cached": False  # 可以添加缓存命中标记
        }
    
    async def _rewrite_query(
        self,
        question: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        查询重写 - 利用对话历史理解上下文
        
        例如:
        用户: "什么是 RAG?"
        助手: "RAG 是检索增强生成..."
        用户: "它有什么优势?" -> 重写为 "RAG 有什么优势?"
        """
        if not history or len(history) == 0:
            return question
        
        # 获取最近几轮对话
        recent_history = history[-self.history_turns * 2:]
        
        # 构建重写 Prompt
        history_text = "\n".join([
            f"{'用户' if h['role'] == 'user' else '助手'}: {h['content']}"
            for h in recent_history
        ])
        
        rewrite_prompt = f"""请根据以下对话历史，理解用户当前问题的真实意图。
如果当前问题包含代词 (它、这个、那个等) 或省略了上下文，请补充完整。
如果当前问题已经完整清晰，请直接返回原问题。

对话历史:
{history_text}

当前问题: {question}

请返回重写后的问题 (只返回问题本身，不要解释):"""
        
        try:
            rewritten = await self._llm_service.generate(rewrite_prompt, max_tokens=100, temperature=0.3)
            return rewritten.strip()
        except Exception:
            # 重写失败，使用原问题
            return question
    
    def _build_prompt_with_history(
        self,
        question: str,
        context: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """构建包含对话历史的 Prompt"""
        
        history_text = ""
        if history:
            recent_history = history[-self.history_turns * 2:]
            history_text = "\n\n对话历史:\n" + "\n".join([
                f"{'用户' if h['role'] == 'user' else '助手'}: {h['content']}"
                for h in recent_history
            ])
        
        prompt = f"""你是一个智能助手 SageFlow。请基于以下参考文档回答用户的问题。

参考文档:
{context}
{history_text}

用户问题: {question}

请根据参考文档提供准确、详细的回答。如果参考文档中没有相关信息，请说明"根据现有文档，我无法找到相关信息"。

回答:"""
        return prompt
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """构建上下文"""
        if not search_results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            doc_name = result.get("document_name", "Unknown")
            content = result.get("content", "")
            context_parts.append(f"[Document {i}: {doc_name}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """构建 Prompt"""
        prompt = f"""你是一个智能助手 SageFlow。请基于以下参考文档回答用户的问题。

参考文档：
{context}

用户问题：{question}

请根据参考文档提供准确、详细的回答。如果参考文档中没有相关信息，请说明"根据现有文档，我无法找到相关信息"。

回答："""
        return prompt


    async def stream_chat(
        self,
        question: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式 RAG 聊天

        Args:
            question: 用户问题
            conversation_id: 对话ID
            user_id: 用户ID
            conversation_history: 对话历史

        Yields:
            流式响应块:
            - {"type": "token", "content": "..."} - 生成的token
            - {"type": "source", "content": {...}} - 来源信息
            - {"type": "done", "content": {...}} - 完成信息
        """
        # 1. 查询重写
        rewritten_question = await self._rewrite_query(question, conversation_history)

        # 2. 向量化查询
        query_vector = await self.embedding_service.encode(rewritten_question)

        # 3. 检索相关文档
        filter_conditions = {"user_id": user_id} if user_id else None
        search_results = await self._vector_store.search(
            query_vector=query_vector,
            limit=self.retrieval_top_k,
            filter_conditions=filter_conditions
        )

        # 4. 重排序
        if self.use_reranker and search_results:
            search_results = await self._reranker.rerank_with_threshold(
                query=rewritten_question,
                documents=search_results,
                threshold=self.score_threshold,
                top_k=self.rerank_top_k
            )
        else:
            search_results = search_results[:self.rerank_top_k]

        # 5. 发送来源信息
        for result in search_results:
            yield {
                "type": "source",
                "content": {
                    "document": result.get("document_name", "Unknown"),
                    "page": result.get("page", 0),
                    "score": result.get("rerank_score") or result.get("score", 0)
                }
            }

        # 6. 构建 Prompt
        context = self._build_context(search_results)
        prompt = self._build_prompt_with_history(
            question=rewritten_question,
            context=context,
            history=conversation_history
        )

        # 7. 流式生成回答
        try:
            async for token in self._llm_service.stream_generate(prompt):
                yield {"type": "token", "content": token}
        except Exception as e:
            yield {"type": "error", "content": str(e)}
            return

        # 8. 发送完成信号
        yield {
            "type": "done",
            "content": {
                "rewritten_query": rewritten_question if rewritten_question != question else None
            }
        }


# 全局单例
rag_service = RAGService()
