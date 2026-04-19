# SageFlow API 文档

## 概述

SageFlow API 提供智能问答、知识库管理、用户认证等功能。

- **Base URL**: `http://localhost:8000`
- **文档**: [Swagger UI](/docs) | [ReDoc](/redoc)
- **版本**: v0.7.0

---

## 认证

API 使用 JWT Bearer Token 认证。

### 获取 Token

```http
POST /api/users/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 使用 Token

```http
GET /api/users/profile
Authorization: Bearer <your_token>
```

---

## 用户 API

### 注册用户

```http
POST /api/users/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "secure_password"
}
```

**响应**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "newuser",
  "email": "user@example.com",
  "preferences": {}
}
```

### 获取用户信息

```http
GET /api/users/profile
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "newuser",
  "email": "user@example.com",
  "preferences": {}
}
```

### 获取用户列表 (管理员)

```http
GET /api/users/
Authorization: Bearer <admin_token>
```

**响应**: `200 OK`
```json
{
  "users": [
    {
      "id": "...",
      "username": "user1",
      "email": "user1@example.com",
      "is_active": true,
      "is_admin": false
    }
  ]
}
```

---

## 文档 API

### 获取文档列表

```http
GET /api/documents/
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "documents": [
    {
      "id": "doc_001",
      "name": "report.pdf",
      "status": "indexed",
      "file_type": ".pdf",
      "file_size": 1024000
    }
  ]
}
```

### 上传文档

```http
POST /api/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
```

**响应**: `200 OK`
```json
{
  "message": "Document uploaded successfully",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "report.pdf",
  "task_id": "celery_task_id",
  "status": "processing"
}
```

### 查询处理状态

```http
GET /api/documents/tasks/{task_id}
```

**响应**: `200 OK`
```json
{
  "task_id": "celery_task_id",
  "status": "SUCCESS",
  "result": {
    "status": "completed",
    "result": {
      "document_name": "report.pdf",
      "chunks_count": 42
    }
  }
}
```

### 删除文档

```http
DELETE /api/documents/{doc_id}
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "message": "Document doc_001 deleted"
}
```

### 重新索引文档

```http
POST /api/documents/{doc_id}/index
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "message": "Document doc_001 indexing started",
  "task_id": "celery_task_id"
}
```

---

## 聊天 API

### 发送消息 (非流式)

```http
POST /api/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "什么是 RAG？",
  "conversation_id": "optional_conversation_id"
}
```

**响应**: `200 OK`
```json
{
  "answer": "RAG (Retrieval Augmented Generation) 是一种...",
  "sources": [
    {
      "document": "rag_intro.pdf",
      "page": 1,
      "content": "RAG 是检索增强生成...",
      "score": 0.85
    }
  ],
  "conversation_id": "conv_001"
}
```

### 发送消息 (流式 SSE)

```http
POST /api/chat/stream
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "什么是 RAG？",
  "conversation_id": "optional_conversation_id"
}
```

**响应**: `text/event-stream`

```
data: [CONVERSATION_ID]conv_001

data: [SOURCES][{"document": "rag_intro.pdf", "page": 1}]

data: RAG

data: (

data: Retrieval

data: ...

data: [DONE]
```

### 获取对话列表

```http
GET /api/chat/conversations
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "conversations": [
    {
      "id": "conv_001",
      "title": "什么是 RAG？",
      "message_count": 5,
      "updated_at": "2026-04-17T10:30:00"
    }
  ]
}
```

### 获取对话详情

```http
GET /api/chat/conversations/{conversation_id}
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "id": "conv_001",
  "title": "什么是 RAG？",
  "messages": [
    {
      "id": "msg_001",
      "role": "user",
      "content": "什么是 RAG？",
      "created_at": "2026-04-17T10:00:00"
    },
    {
      "id": "msg_002",
      "role": "assistant",
      "content": "RAG 是...",
      "sources": [...],
      "created_at": "2026-04-17T10:00:05"
    }
  ]
}
```

### 删除对话

```http
DELETE /api/chat/conversations/{conversation_id}
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "message": "Conversation deleted"
}
```

---

## 统计 API

### 获取系统统计

```http
GET /api/stats/system
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "users": 100,
  "conversations": 500,
  "messages": 2500,
  "vectors": 10000
}
```

### 获取用户统计

```http
GET /api/stats/user
Authorization: Bearer <token>
```

**响应**: `200 OK`
```json
{
  "conversations": 10,
  "messages": 50
}
```

---

## LLM API

### 获取可用模型

```http
GET /api/llm/models
```

**响应**: `200 OK`
```json
{
  "models": [
    {
      "name": "qwen2.5:3b",
      "display_name": "Qwen 2.5 3B",
      "description": "通义千问 2.5 3B 参数版本",
      "parameters": "3B",
      "context_length": 32768
    }
  ],
  "current_model": "qwen2.5:3b"
}
```

### 切换模型

```http
POST /api/llm/switch
Content-Type: application/json

{
  "model_name": "llama3:8b"
}
```

**响应**: `200 OK`
```json
{
  "message": "Model switched successfully",
  "current_model": "llama3:8b"
}
```

---

## WebSocket API

### 聊天 WebSocket

**端点**: `ws://localhost:8000/ws/chat?token=<jwt_token>&conversation_id=<optional>`

**发送消息**:
```json
{
  "type": "chat",
  "content": "什么是 RAG？",
  "conversation_id": "optional_id"
}
```

**接收消息**:
```json
{"type": "token", "content": "RAG", "timestamp": "..."}
{"type": "token", "content": "是", "timestamp": "..."}
{"type": "source", "content": {"document": "rag.pdf", "page": 1}, "timestamp": "..."}
{"type": "complete", "content": "RAG 是...", "timestamp": "..."}
```

**心跳**:
```json
// 发送
{"type": "ping"}

// 响应
{"type": "pong"}
```

---

## 监控 API

### 健康检查

```http
GET /health
```

**响应**: `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-04-17T10:00:00",
  "version": "0.7.0"
}
```

### 详细健康检查

```http
GET /health?detailed=true
```

**响应**: `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-04-17T10:00:00",
  "version": "0.7.0",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.2,
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.5,
      "used_memory": "128M"
    },
    "qdrant": {
      "status": "healthy",
      "latency_ms": 3.0,
      "collections_count": 1
    },
    "ollama": {
      "status": "healthy",
      "latency_ms": 10.5,
      "models_available": 2,
      "models": ["qwen2.5:3b", "llama3:8b"]
    }
  },
  "checks_passed": 4,
  "checks_failed": 0
}
```

### Prometheus 指标

```http
GET /metrics
```

**响应**: `text/plain` (Prometheus 格式)

```
# HELP sageflow_info SageFlow application info
# TYPE sageflow_info gauge
sageflow_info{version="0.7.0"} 1

# TYPE sageflow_http_requests_total counter
sageflow_http_requests_total{method="GET",path="/api/chat",status="200"} 150

# TYPE sageflow_http_request_duration_seconds histogram
sageflow_http_request_duration_seconds_bucket{le="0.1",method="GET",path="/api/chat"} 120
...
```

---

## 错误响应

所有错误响应遵循统一格式：

```json
{
  "detail": "Error message description"
}
```

### 常见错误码

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 请求体验证失败 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

---

## 限流规则

| 端点 | 限制 |
|------|------|
| 默认 | 100 请求/分钟 |
| `/api/chat` | 30 请求/分钟 |
| `/api/documents/upload` | 10 请求/分钟 |
| `/api/users/login` | 5 请求/分钟 |
| `/api/users/register` | 3 请求/分钟 |

超过限制返回 `429 Too Many Requests`。

---

*最后更新: 2026-04-17*
