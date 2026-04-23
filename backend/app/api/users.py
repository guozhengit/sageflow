"""用户 API 路由"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.services.user_service import user_service

router = APIRouter()


class UserRegister(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码 (最少6位)")


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class UserProfile(BaseModel):
    """用户画像响应"""
    id: str = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    preferences: dict = Field(default={}, description="用户偏好设置")
    created_at: Optional[datetime] = Field(None, description="创建时间")


@router.post("/register", response_model=UserProfile, summary="用户注册", description="创建新用户账号")
async def register(request: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    existing = await user_service.get_by_username(db, request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing = await user_service.get_by_email(db, request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = await user_service.create_user(
        db,
        username=request.username,
        email=request.email,
        password=request.password
    )

    return UserProfile(
        id=str(user.id),
        username=user.username,
        email=user.email,
        preferences=user.preferences or {},
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse, summary="用户登录", description="用户登录获取 JWT 令牌")
async def login(request: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    user = await user_service.authenticate(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    token = create_access_token(data={"sub": user.username})
    return TokenResponse(access_token=token)


@router.get("/profile", response_model=UserProfile, summary="获取用户信息", description="获取当前登录用户的详细信息")
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户画像"""
    return UserProfile(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        preferences=current_user.preferences or {},
        created_at=current_user.created_at,
    )


@router.get("/", dependencies=[Depends(require_admin)], summary="获取用户列表", description="获取所有用户列表 (需要管理员权限)")
async def list_users(db: AsyncSession = Depends(get_db)):
    """获取用户列表 (管理员)"""
    from sqlalchemy import select

    result = await db.execute(select(User))
    users = result.scalars().all()
    return {
        "users": [
            {
                "id": str(u.id),
                "username": u.username,
                "email": u.email,
                "is_active": u.is_active,
                "is_admin": getattr(u, "is_admin", False),
            }
            for u in users
        ]
    }
