from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from app.core.config import get_settings
from app.api import chat, documents, users, stats, llm, websocket
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging, LoggingMiddleware
from app.core.rate_limit import RateLimitMiddleware
from app.services.health_service import health_checker
from app.services.metrics_service import metrics, RequestMetricsMiddleware

settings = get_settings()

# 初始化日志
setup_logging()


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
## SageFlow API

智慧如流，洞察如光 - 智能问答解决方案

### 核心功能

- **RAG 问答**: 基于检索增强生成的智能问答
- **知识库管理**: 文档上传、解析、向量化
- **多轮对话**: 上下文感知的连续对话
- **混合检索**: BM25 + 向量检索融合

### 认证方式

使用 JWT Bearer Token 认证:
```
Authorization: Bearer <your_token>
```

### WebSocket 端点

- `/ws/chat`: 实时聊天流式响应
- `/ws/status`: 系统状态监控
        """,
        openapi_url="/api/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {
                "name": "users",
                "description": "用户认证与管理"
            },
            {
                "name": "documents",
                "description": "知识库文档管理"
            },
            {
                "name": "chat",
                "description": "RAG 问答与对话管理"
            },
            {
                "name": "stats",
                "description": "系统与用户统计"
            },
            {
                "name": "llm",
                "description": "LLM 模型管理"
            },
            {
                "name": "websocket",
                "description": "WebSocket 实时通信"
            }
        ]
    )

    # 注册全局异常处理器
    register_exception_handlers(app)

    # 添加请求指标中间件
    app.add_middleware(RequestMetricsMiddleware)

    # 添加日志中间件
    app.add_middleware(LoggingMiddleware)

    # 添加限流中间件
    app.add_middleware(
        RateLimitMiddleware,
        default_limits={
            "default": (100, 60),           # 默认: 100 请求/分钟
            "/api/chat": (30, 60),          # 聊天: 30 请求/分钟
            "/api/documents/upload": (10, 60),  # 上传: 10 请求/分钟
            "/api/users/login": (5, 60),        # 登录: 5 请求/分钟
            "/api/users/register": (3, 60),     # 注册: 3 请求/分钟
        }
    )

    # CORS 配置 - 使用环境变量控制
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=3600,
    )

    # 注册路由
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
    app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
    app.include_router(websocket.router, tags=["websocket"])

    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "message": "Welcome to SageFlow API"
        }

    @app.get("/health")
    async def health_check(
        detailed: bool = Query(False, description="是否返回详细信息")
    ):
        """
        健康检查端点

        - detailed=False: 简单检查，返回整体状态
        - detailed=True: 详细检查，返回所有服务状态
        """
        return await health_checker.check_all(detailed=detailed)

    @app.get("/metrics", response_class=PlainTextResponse)
    async def get_metrics():
        """
        Prometheus 监控指标端点

        返回 Prometheus 格式的监控指标
        """
        # 添加当前系统指标
        import psutil
        metrics.gauge("process_memory_bytes", psutil.Process().memory_info().rss)
        metrics.gauge("process_cpu_percent", psutil.cpu_percent())

        return metrics.export_prometheus()

    return app


app = create_app()
