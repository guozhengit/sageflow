from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service
from app.services.conversation_service import conversation_service
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.chat import Conversation

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    conversation_id: Optional[str] = None
    use_stream: bool = True  # 是否使用流式响应


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str
    sources: List[dict] = []
    conversation_id: str


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送消息 - RAG 问答"""
    try:
        conversation_id = request.conversation_id
        
        # 如果没有对话 ID，创建新对话
        if not conversation_id:
            conversation = await conversation_service.create_conversation(
                db, 
                user_id=str(current_user.id),
                title=request.message[:50]
            )
            conversation_id = str(conversation.id)
        
        # 获取对话历史
        conversation_data = await conversation_service.get_conversation(
            db, conversation_id=conversation_id, user_id=str(current_user.id)
        )
        
        history = []
        if conversation_data:
            for msg in conversation_data.messages[:-6]:  # 保留最近 3 轮 (6 条消息)
                history.append({"role": msg.role, "content": msg.content})
        
        # 保存用户消息
        await conversation_service.add_message(
            db,
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        
        # 执行 RAG 查询 (带对话历史)
        result = await rag_service.query(
            question=request.message,
            user_id=str(current_user.id),
            conversation_history=history
        )
        
        # 保存助手消息
        await conversation_service.add_message(
            db,
            conversation_id=conversation_id,
            role="assistant",
            content=result["answer"],
            sources=result["sources"]
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            conversation_id=conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """流式发送消息 - RAG 流式响应 (SSE)"""
    from app.services.conversation_service import conversation_service
    
    async def generate():
        try:
            conversation_id = request.conversation_id
            
            if not conversation_id:
                conversation = await conversation_service.create_conversation(
                    db,
                    user_id=str(current_user.id),
                    title=request.message[:50]
                )
                conversation_id = str(conversation.id)
            
            # 发送对话 ID
            yield f"data: [CONVERSATION_ID]{conversation_id}\n\n"
            
            await conversation_service.add_message(
                db,
                conversation_id=conversation_id,
                role="user",
                content=request.message
            )
            
            # 1. 检索相关文档
            query_vector = await rag_service.embedding_service.encode(request.message)
            search_results = await rag_service._vector_store.search(
                query_vector=query_vector,
                limit=3
            )
            
            # 2. 构建上下文和 Prompt
            context = rag_service._build_context(search_results)
            prompt = rag_service._build_prompt(request.message, context)
            
            # 3. 发送来源信息
            sources = [
                {
                    "document": r.get("document_name", "Unknown"),
                    "page": r.get("page", 0),
                    "content": r.get("content", "")[:200] + "..."
                }
                for r in search_results
            ]
            import json
            yield f"data: [SOURCES]{json.dumps(sources, ensure_ascii=False)}\n\n"
            
            # 4. 流式生成回答
            full_answer = ""
            async for chunk in llm_service.generate_stream(prompt):
                full_answer += chunk
                yield f"data: {chunk}\n\n"
            
            # 5. 保存助手消息
            await conversation_service.add_message(
                db,
                conversation_id=conversation_id,
                role="assistant",
                content=full_answer,
                sources=sources
            )
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/conversations")
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的对话列表"""
    conversations = await conversation_service.get_user_conversations(
        db,
        user_id=str(current_user.id)
    )
    return {
        "conversations": [
            {
                "id": str(c.id),
                "title": c.title,
                "message_count": len(c.messages),
                "updated_at": c.updated_at.isoformat() if c.updated_at else None
            }
            for c in conversations
        ]
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取对话详情"""
    conversation = await conversation_service.get_conversation(
        db,
        conversation_id=conversation_id,
        user_id=str(current_user.id)
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "sources": m.sources,
                "created_at": m.created_at.isoformat() if m.created_at else None
            }
            for m in conversation.messages
        ]
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除对话"""
    deleted = await conversation_service.delete_conversation(
        db,
        conversation_id=conversation_id,
        user_id=str(current_user.id)
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted"}
