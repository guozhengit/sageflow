"""用户服务"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.auth import get_password_hash, verify_password


class UserService:
    """用户服务类"""
    
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(
        self, 
        db: AsyncSession, 
        username: str, 
        email: str, 
        password: str
    ) -> User:
        """创建用户"""
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password)
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
    
    async def authenticate(
        self, 
        db: AsyncSession, 
        username: str, 
        password: str
    ) -> Optional[User]:
        """用户认证"""
        user = await self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


# 全局单例
user_service = UserService()
