from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger("database")

# 创建异步引擎 (优化配置)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    # 连接池配置
    pool_pre_ping=True,      # 连接前检查可用性
    pool_size=10,            # 连接池大小
    max_overflow=20,         # 最大溢出连接数
    pool_recycle=3600,       # 连接回收时间 (1小时)
    pool_timeout=30,         # 获取连接超时
    # 执行配置
    execution_options={
        "isolation_level": "READ COMMITTED"
    }
)

# 创建会话工厂
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 连接池事件监听
@event.listens_for(engine.sync_engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """连接建立事件"""
    logger.debug(f"Database connection established: {id(dbapi_connection)}")


@event.listens_for(engine.sync_engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """连接检出事件"""
    logger.debug(f"Connection checkout: {id(dbapi_connection)}")


@event.listens_for(engine.sync_engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """连接归还事件"""
    logger.debug(f"Connection checkin: {id(dbapi_connection)}")


async def get_db_stats() -> dict:
    """获取数据库连接池统计"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "checked_in": pool.checkedin(),
    }
