"""统计 API 路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.stats_service import stats_service

router = APIRouter()


@router.get("/system")
async def get_system_stats(db: AsyncSession = Depends(get_db)):
    """获取系统统计信息 (管理员)"""
    stats = await stats_service.get_system_stats(db)
    return stats


@router.get("/user")
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户统计信息"""
    stats = await stats_service.get_user_stats(db, str(current_user.id))
    return stats
