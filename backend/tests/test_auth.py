"""测试认证工具"""
import pytest
from datetime import timedelta

from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    get_current_user
)
from app.models.user import User


class TestPasswordHashing:
    """密码哈希测试"""

    def test_password_hash_creates_different_hashes(self):
        """测试相同密码生成不同哈希"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2  # bcrypt 会生成不同的盐

    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password("wrongpassword", hashed) is False


class TestJWTToken:
    """JWT Token 测试"""

    def test_create_access_token(self):
        """测试创建 Token"""
        token = create_access_token(data={"sub": "testuser"})
        assert token is not None
        assert isinstance(token, str)

    def test_create_access_token_with_expiry(self):
        """测试创建带过期时间的 Token"""
        token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(minutes=30)
        )
        assert token is not None

    def test_decode_access_token_valid(self):
        """测试解码有效 Token"""
        token = create_access_token(data={"sub": "testuser", "role": "admin"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    def test_decode_access_token_invalid(self):
        """测试解码无效 Token"""
        payload = decode_access_token("invalid-token")
        assert payload is None

    def test_decode_access_token_expired(self):
        """测试解码过期 Token"""
        # 创建一个已过期的 Token
        token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=-1)
        )
        # 由于时间已经过去，这个 Token 应该无法解码
        payload = decode_access_token(token)
        assert payload is None
