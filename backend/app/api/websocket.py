"""
WebSocket API 路由
提供实时通信功能
"""
import json
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends

from app.services.websocket_service import ws_manager, ChatStreamHandler
from app.core.auth import decode_access_token
from app.services.rag_service import rag_service
from app.services.conversation_service import conversation_service
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: str = Query(..., description="JWT 认证令牌"),
    conversation_id: Optional[str] = Query(None, description="对话ID")
):
    """
    聊天 WebSocket 端点

    连接参数:
    - token: JWT 认证令牌
    - conversation_id: 可选的对话ID

    消息格式 (发送):
    {
        "type": "chat" | "ping",
        "content": "消息内容",
        "conversation_id": "对话ID (可选)"
    }

    消息格式 (接收):
    {
        "type": "token" | "source" | "complete" | "error" | "pong",
        "content": "...",
        "timestamp": "ISO时间戳"
    }
    """
    # 验证 token
    payload = decode_access_token(token)
    if payload is None:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "content": "Invalid or expired token"
        })
        await websocket.close(code=4001)
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.accept()
        await websocket.send_json({
            "type": "error",
            "content": "Invalid token payload"
        })
        await websocket.close(code=4001)
        return

    # 接受连接
    await ws_manager.connect(websocket, int(user_id), conversation_id)

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "ping":
                # 心跳响应
                await websocket.send_json({"type": "pong"})

            elif message_type == "chat":
                # 处理聊天消息
                content = data.get("content", "")
                conv_id = data.get("conversation_id", conversation_id)

                if not content:
                    await websocket.send_json({
                        "type": "error",
                        "content": "Message content is required"
                    })
                    continue

                try:
                    # 创建流式处理器
                    handler = ChatStreamHandler(websocket, conv_id or "default")

                    # 调用 RAG 服务进行流式响应
                    full_response = ""
                    sources = []

                    async for chunk in rag_service.stream_chat(content, conversation_id=conv_id):
                        if chunk.get("type") == "token":
                            token_text = chunk.get("content", "")
                            full_response += token_text
                            await handler.on_token(token_text)

                        elif chunk.get("type") == "source":
                            source = chunk.get("content", {})
                            sources.append(source)
                            await handler.on_source(source)

                    # 发送完成消息
                    await handler.on_complete(full_response)

                    # 保存对话
                    if conv_id:
                        async for db in get_db():
                            await conversation_service.add_message(
                                db, conv_id, "user", content
                            )
                            await conversation_service.add_message(
                                db, conv_id, "assistant", full_response,
                                metadata={"sources": sources}
                            )
                            break

                except Exception as e:
                    logger.error(f"Chat error: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "content": str(e)
                    })

            elif message_type == "typing":
                # 打字状态通知
                conv_id = data.get("conversation_id")
                if conv_id:
                    await ws_manager.send_to_session(conv_id, {
                        "type": "user_typing",
                        "user_id": user_id
                    })

            else:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected: user_id={user_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """
    系统状态 WebSocket 端点

    用于监控系统状态变化，如文档处理进度等
    """
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "active_connections": ws_manager.active_connections_count
                })

            elif message_type == "subscribe":
                # 订阅特定事件
                event_type = data.get("event_type")
                await websocket.send_json({
                    "type": "subscribed",
                    "event_type": event_type
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        logger.info("Status WebSocket disconnected")

    except Exception as e:
        logger.error(f"Status WebSocket error: {e}")


@router.get("/connections")
async def get_connections():
    """
    获取当前活跃连接数
    """
    return {
        "active_connections": ws_manager.active_connections_count
    }
