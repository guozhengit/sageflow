"""测试用户 API"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestUserRegistration:
    """用户注册测试"""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """测试成功注册"""
        response = await client.post(
            "/api/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """测试重复用户名注册"""
        response = await client.post(
            "/api/users/register",
            json={
                "username": "testuser",  # 已存在的用户名
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """测试无效邮箱注册"""
        response = await client.post(
            "/api/users/register",
            json={
                "username": "newuser",
                "email": "invalid-email",
                "password": "password123"
            }
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """测试密码太短"""
        response = await client.post(
            "/api/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "123"  # 太短
            }
        )
        assert response.status_code == 422


class TestUserLogin:
    """用户登录测试"""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user):
        """测试成功登录"""
        response = await client.post(
            "/api/users/login",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """测试错误密码"""
        response = await client.post(
            "/api/users/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """测试不存在的用户"""
        response = await client.post(
            "/api/users/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401


class TestUserProfile:
    """用户画像测试"""

    @pytest.mark.asyncio
    async def test_get_profile_authenticated(
        self,
        client: AsyncClient,
        test_user,
        auth_headers: dict
    ):
        """测试获取用户画像 (已认证)"""
        response = await client.get(
            "/api/users/profile",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_profile_unauthenticated(self, client: AsyncClient):
        """测试获取用户画像 (未认证)"""
        response = await client.get("/api/users/profile")
        assert response.status_code == 403  # No auth header

    @pytest.mark.asyncio
    async def test_get_profile_invalid_token(self, client: AsyncClient):
        """测试获取用户画像 (无效 Token)"""
        response = await client.get(
            "/api/users/profile",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
