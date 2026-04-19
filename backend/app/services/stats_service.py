"""统计数据服务"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User
from app.models.chat import Conversation, Message
from app.services.vector_store import vector_store


class StatsService:
    """统计数据服务类"""
    
    async def get_system_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """获取系统统计信息"""
        # 用户统计
        user_count = await db.execute(select(func.count(User.id)))
        
        # 对话统计
        conversation_count = await db.execute(select(func.count(Conversation.id)))
        
        # 消息统计
        message_count = await db.execute(select(func.count(Message.id)))
        
        # 向量数据库统计
        vector_stats = await vector_store.get_stats()
        
        return {
            "users": user_count.scalar() or 0,
            "conversations": conversation_count.scalar() or 0,
            "messages": message_count.scalar() or 0,
            "vectors": vector_stats.get("points_count", 0),
        }
    
    async def get_user_stats(self, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """获取用户统计信息"""
        # 用户对话数
        conversation_count = await db.execute(
            select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
        )
        
        # 用户消息数
        message_count = await db.execute(
            select(func.count(Message.id))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .where(Conversation.user_id == user_id)
        )
        
        return {
            "conversations": conversation_count.scalar() or 0,
            "messages": message_count.scalar() or 0,
        }


# 全局单例
stats_service = StatsService()
