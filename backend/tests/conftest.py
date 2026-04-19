"""测试配置 - Fixtures and Settings"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

# 设置测试环境变量
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["OLLAMA_URL"] = "http://localhost:11434"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-minimum-32-chars"
os.environ["LLM_MODEL"] = "test-model"


# 创建测试数据库引擎
from app.core.database import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """每个测试前创建表，测试后删除"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取测试数据库会话"""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """获取测试客户端"""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def auth_headers() -> dict:
    """获取认证头"""
    from app.core.auth import create_access_token

    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers() -> dict:
    """获取管理员认证头"""
    from app.core.auth import create_access_token

    token = create_access_token(data={"sub": "adminuser"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """创建测试用户"""
    from app.models.user import User
    from app.core.auth import get_password_hash

    user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        preferences={}
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession):
    """创建管理员用户"""
    from app.models.user import User
    from app.core.auth import get_password_hash

    user = User(
        id=uuid.uuid4(),
        username="adminuser",
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        is_admin=True,
        preferences={}
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_conversation(db_session: AsyncSession, test_user):
    """创建测试对话"""
    from app.models.chat import Conversation

    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Test Conversation"
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)
    return conversation
