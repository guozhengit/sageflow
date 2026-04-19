"""
WebSocket 连接管理器
处理实时通信，支持聊天流式响应
"""
import json
import asyncio
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket 连接管理器
    管理所有活跃的 WebSocket 连接
    """

    def __init__(self):
        # 用户ID -> WebSocket连接集合
        self._user_connections: Dict[int, Set[WebSocket]] = {}
        # 会话ID -> WebSocket连接 (用于聊天会话)
        self._session_connections: Dict[str, WebSocket] = {}
        # 连接元数据
        self._connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    @property
    def active_connections_count(self) -> int:
        """活跃连接总数"""
        return sum(len(conns) for conns in self._user_connections.values())

    async def connect(self, websocket: WebSocket, user_id: int, session_id: Optional[str] = None):
        """
        接受新的 WebSocket 连接

        Args:
            websocket: WebSocket 连接对象
            user_id: 用户ID
            session_id: 可选的会话ID
        """
        await websocket.accept()

        # 添加到用户连接集合
        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()
        self._user_connections[user_id].add(websocket)

        # 存储连接元数据
        self._connection_metadata[websocket] = {
            "user_id": user_id,
            "session_id": session_id,
            "connected_at": datetime.utcnow().isoformat()
        }

        # 如果有会话ID，添加到会话连接
        if session_id:
            self._session_connections[session_id] = websocket

        logger.info(f"WebSocket connected: user_id={user_id}, session_id={session_id}")

    def disconnect(self, websocket: WebSocket):
        """
        断开 WebSocket 连接

        Args:
            websocket: 要断开的 WebSocket 连接
        """
        metadata = self._connection_metadata.get(websocket, {})
        user_id = metadata.get("user_id")
        session_id = metadata.get("session_id")

        # 从用户连接集合中移除
        if user_id and user_id in self._user_connections:
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

        # 从会话连接中移除
        if session_id and session_id in self._session_connections:
            del self._session_connections[session_id]

        # 移除元数据
        if websocket in self._connection_metadata:
            del self._connection_metadata[websocket]

        logger.info(f"WebSocket disconnected: user_id={user_id}, session_id={session_id}")

    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        发送个人消息

        Args:
            websocket: 目标 WebSocket 连接
            message: 消息内容
        """
        try:
            await websocket.send_json({
                **message,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.disconnect(websocket)

    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """
        向用户的所有连接发送消息

        Args:
            user_id: 用户ID
            message: 消息内容
        """
        if user_id not in self._user_connections:
            return

        disconnected = []
        for websocket in self._user_connections[user_id]:
            try:
                await self.send_personal_message(websocket, message)
            except Exception:
                disconnected.append(websocket)

        # 清理断开的连接
        for ws in disconnected:
            self.disconnect(ws)

    async def send_to_session(self, session_id: str, message: Dict[str, Any]):
        """
        向特定会话发送消息

        Args:
            session_id: 会话ID
            message: 消息内容
        """
        if session_id not in self._session_connections:
            return

        websocket = self._session_connections[session_id]
        await self.send_personal_message(websocket, message)

    async def broadcast(self, message: Dict[str, Any], exclude: Optional[WebSocket] = None):
        """
        广播消息到所有连接

        Args:
            message: 消息内容
            exclude: 要排除的连接
        """
        disconnected = []
        for websocket in self._connection_metadata:
            if websocket == exclude:
                continue
            try:
                await self.send_personal_message(websocket, message)
            except Exception:
                disconnected.append(websocket)

        for ws in disconnected:
            self.disconnect(ws)

    def get_user_sessions(self, user_id: int) -> Set[str]:
        """
        获取用户的所有活跃会话ID

        Args:
            user_id: 用户ID

        Returns:
            会话ID集合
        """
        sessions = set()
        for ws, metadata in self._connection_metadata.items():
            if metadata.get("user_id") == user_id:
                session_id = metadata.get("session_id")
                if session_id:
                    sessions.add(session_id)
        return sessions


# 全局连接管理器
ws_manager = ConnectionManager()


class ChatStreamHandler:
    """
    聊天流式响应处理器
    通过 WebSocket 发送流式响应
    """

    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self._buffer = []

    async def on_token(self, token: str):
        """收到新 token 时调用"""
        await self.websocket.send_json({
            "type": "token",
            "content": token,
            "session_id": self.session_id
        })

    async def on_source(self, source: Dict[str, Any]):
        """收到来源信息时调用"""
        await self.websocket.send_json({
            "type": "source",
            "content": source,
            "session_id": self.session_id
        })

    async def on_complete(self, full_response: str):
        """响应完成时调用"""
        await self.websocket.send_json({
            "type": "complete",
            "content": full_response,
            "session_id": self.session_id
        })

    async def on_error(self, error: str):
        """发生错误时调用"""
        await self.websocket.send_json({
            "type": "error",
            "content": error,
            "session_id": self.session_id
        })
