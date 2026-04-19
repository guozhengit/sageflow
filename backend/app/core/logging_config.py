"""日志配置 - 结构化日志和请求追踪"""
import logging
import sys
import json
from datetime import datetime
from typing import Optional
from contextvars import ContextVar
from functools import wraps

from app.core.config import get_settings

settings = get_settings()

# 请求 ID 上下文变量
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON 格式化器 - 结构化日志"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加请求 ID
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        # 添加额外字段
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """彩色格式化器 - 开发环境使用"""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        # 添加颜色
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        # 添加请求 ID
        request_id = request_id_var.get()
        if request_id:
            record.msg = f"[{request_id[:8]}] {record.msg}"

        return super().format(record)


def setup_logging() -> None:
    """设置日志配置"""
    # 根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    if settings.DEBUG:
        # 开发环境：彩色输出
        console_handler.setFormatter(
            ColoredFormatter(
                fmt="%(levelname)s | %(asctime)s | %(name)s:%(lineno)d - %(message)s",
                datefmt="%H:%M:%S"
            )
        )
    else:
        # 生产环境：JSON 格式
        console_handler.setFormatter(JSONFormatter())

    root_logger.addHandler(console_handler)

    # 降低第三方库日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    return logging.getLogger(name)


# 模块日志器
logger = get_logger("sageflow")


class LoggingMiddleware:
    """FastAPI 日志中间件"""

    def __init__(self, app):
        self.app = app
        self.logger = get_logger("http")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 生成请求 ID
        import uuid
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        # 记录请求
        method = scope["method"]
        path = scope["path"]
        query = scope.get("query_string", b"").decode()

        self.logger.info(f"--> {method} {path}?{query}")

        # 计时
        start_time = datetime.utcnow()

        # 包装 send 以记录响应
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                self.logger.info(f"<-- {method} {path} {status_code} ({duration:.2f}ms)")
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            self.logger.error(f"!!! {method} {path} - {e}")
            raise


def log_function_call(func):
    """函数调用日志装饰器"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        func_logger = get_logger(func.__module__)
        func_logger.debug(f"Calling {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            func_logger.debug(f"Finished {func.__name__}")
            return result
        except Exception as e:
            func_logger.error(f"Error in {func.__name__}: {e}")
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        func_logger = get_logger(func.__module__)
        func_logger.debug(f"Calling {func.__name__}")
        try:
            result = func(*args, **kwargs)
            func_logger.debug(f"Finished {func.__name__}")
            return result
        except Exception as e:
            func_logger.error(f"Error in {func.__name__}: {e}")
            raise

    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
