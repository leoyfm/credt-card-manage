"""异常处理器"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from .custom import BaseAPIException
from ..logging.logger import get_logger

logger = get_logger("exception.handler")

async def base_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """处理自定义API异常"""
    
    # 记录异常日志
    logger.error(
        f"API异常: {exc.message}",
        error_code=exc.error_code,
        trace_id=exc.trace_id,
        url=str(request.url),
        method=request.method,
        error_detail=exc.error_detail
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.error_code,
            "message": exc.message,
            "error_detail": exc.error_detail,
            "trace_id": exc.trace_id,
            "timestamp": "2024-12-10T21:20:00.000Z"
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理HTTP异常"""
    
    logger.warning(
        f"HTTP异常: {exc.detail}",
        status_code=exc.status_code,
        url=str(request.url),
        method=request.method
    )
    
    # 映射HTTP状态码到业务错误码
    error_code_mapping = {
        400: 4000,
        401: 4010,
        403: 4030,
        404: 4040,
        405: 4050,
        422: 4220,
        429: 4290,
        500: 5000,
        502: 5020,
        503: 5030
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": error_code_mapping.get(exc.status_code, 5000),
            "message": exc.detail,
            "error_detail": {},
            "trace_id": None,
            "timestamp": "2024-12-10T21:20:00.000Z"
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未知异常"""
    
    logger.error(
        f"未知异常: {str(exc)}",
        exception_type=type(exc).__name__,
        url=str(request.url),
        method=request.method,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": 5000,
            "message": "系统内部错误",
            "error_detail": {"exception_type": type(exc).__name__},
            "trace_id": None,
            "timestamp": "2024-12-10T21:20:00.000Z"
        }
    ) 