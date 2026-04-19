"""全局异常处理器"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AppException(Exception):
    """应用基础异常"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class UnauthorizedException(AppException):
    """未授权异常"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AppException):
    """禁止访问异常"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403)


class BadRequestException(AppException):
    """错误请求异常"""
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, status_code=400)


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.error(f"AppException: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.message,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": exc.errors(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        logger.warning(f"Pydantic validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": exc.errors(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
