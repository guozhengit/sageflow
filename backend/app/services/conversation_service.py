"""对话服务"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.chat import Conversation, Message


class ConversationService:
    """对话服务类"""
    
    async def create_conversation(
        self, 
        db: AsyncSession, 
        user_id: str, 
        title: str = "New Conversation"
    ) -> Conversation:
        """创建新对话"""
        conversation = Conversation(user_id=user_id, title=title)
        db.add(conversation)
        await db.flush()
        await db.refresh(conversation)
        return conversation
    
    async def get_conversation(
        self, 
        db: AsyncSession, 
        conversation_id: str, 
        user_id: str
    ) -> Optional[Conversation]:
        """获取对话详情"""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .options(selectinload(Conversation.messages))
        )
        return result.scalar_one_or_none()
    
    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None
    ) -> Message:
        """添加消息"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources or []
        )
        db.add(message)
        await db.flush()
        await db.refresh(message)
        return message
    
    async def get_user_conversations(
        self, 
        db: AsyncSession, 
        user_id: str,
        limit: int = 20
    ) -> List[Conversation]:
        """获取用户的对话列表"""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def delete_conversation(
        self, 
        db: AsyncSession, 
        conversation_id: str, 
        user_id: str
    ) -> bool:
        """删除对话"""
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            await db.delete(conversation)
            return True
        return False


# 全局单例
conversation_service = ConversationService()
