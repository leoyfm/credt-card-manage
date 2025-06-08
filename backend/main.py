import logging
import pytz
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utils.response import ResponseUtil
from models.response import ApiResponse
from routers import annual_fee, cards, reminders, recommendations, auth, transactions
from database import create_database, get_db_health
from config import settings, validate_config, get_environment_info

# 配置日志
from utils.logger import init_logging, LogConfig

# 初始化日志系统
init_logging()
logger = LogConfig.get_logger(__name__)

# 配置时区
TIMEZONE = pytz.timezone('Asia/Shanghai')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    替换deprecated的on_event装饰器，使用现代的lifespan上下文管理器
    """
    # 启动事件
    logger.info("信用卡管理系统正在启动...")
    
    try:
        # 验证配置
        validate_config()
        logger.info("配置验证通过")
        
        # 创建数据库表
        create_database()
        logger.info("数据库初始化完成")
        
        # 打印环境信息
        env_info = get_environment_info()
        logger.info(f"环境信息: {env_info}")
        
        logger.info("系统启动完成")
    except Exception as e:
        logger.error(f"系统启动失败: {str(e)}")
        raise
    
    yield
    
    # 关闭事件
    logger.info("信用卡管理系统正在关闭...")


app = FastAPI(
    title="信用卡管理系统 API",
    lifespan=lifespan,
    description="""
## 智能化信用卡管理系统后端接口

### 功能特色
- 📊 **年费管理**：灵活的年费规则配置和自动化减免条件检查
- 💳 **信用卡管理**：完整的信用卡信息管理和额度监控
- 🔔 **还款提醒**：智能还款提醒和账单管理
- 🎯 **智能推荐**：基于用户行为的个性化信用卡推荐
- 💰 **交易记录**：完整的交易记录管理和多维度查询分析
- 📈 **数据统计**：详细的消费分析、年费统计和交易趋势

### API特点
- 统一的响应格式，包含success、code、message、data字段
- 完整的分页支持，所有列表接口统一分页参数
- 模糊搜索功能，关键词搜索相关内容
- 详细的错误处理和状态码
- 完善的数据验证和类型安全
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "LEO",
        "email": "leoyfm@gmail.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "系统",
            "description": "系统基础接口，包括健康检查、状态监控等功能"
        },
        {
            "name": "年费管理", 
            "description": "年费规则配置、年费记录管理、减免条件检查等功能"
        },
        {
            "name": "信用卡",
            "description": "信用卡信息管理、额度监控、卡片状态管理等功能"
        },
        {
            "name": "还款提醒",
            "description": "还款提醒设置、通知管理、账单提醒等功能"
        },
        {
            "name": "智能推荐",
            "description": "个性化信用卡推荐、用户画像分析、推荐反馈等功能"
        },
        {
            "name": "用户认证",
            "description": "用户注册、登录、密码管理、微信登录、验证码等认证功能"
        },
        {
            "name": "交易记录",
            "description": "交易记录管理、CRUD操作、交易查询和筛选等功能"
        },
        {
            "name": "交易统计",
            "description": "交易数据统计分析、分类统计、月度趋势、消费概览等功能"
        }
    ]
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    
    记录所有HTTP请求的详细信息
    """
    start_time = datetime.now()
    
    # 记录请求开始
    LogConfig.log_request(
        method=request.method,
        url=str(request.url),
        status_code=0,  # 请求开始时还没有状态码
    )
    
    try:
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        duration = (datetime.now() - start_time).total_seconds()
        
        # 记录请求完成
        LogConfig.log_request(
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            duration=duration
        )
        
        return response
        
    except Exception as e:
        # 记录请求异常
        duration = (datetime.now() - start_time).total_seconds()
        LogConfig.log_error(e, f"处理请求时发生异常: {request.method} {request.url}")
        LogConfig.log_request(
            method=request.method,
            url=str(request.url),
            status_code=500,
            duration=duration
        )
        raise

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    
    捕获所有未处理的异常并记录到日志中
    """
    LogConfig.log_error(exc, f"全局异常处理器: {request.method} {request.url}")
    
    return ResponseUtil.error(
        message="服务器内部错误",
        code=500
    )

# 挂载路由模块
app.include_router(auth.router, prefix="/api")
app.include_router(annual_fee.router, prefix="/api")
app.include_router(cards.router, prefix="/api")
app.include_router(reminders.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(transactions.router, prefix="/api/transactions")

@app.get(
    "/", 
    response_model=ApiResponse[str],
    tags=["系统"],
    summary="服务状态检查",
    response_description="返回服务运行状态信息"
)
async def root():
    """
    获取服务运行状态
    
    返回API服务的基本运行状态信息，用于确认服务是否正常启动。
    """
    logger.info("服务状态检查请求")
    current_time = datetime.now(TIMEZONE)
    return ResponseUtil.success(
        data={
            "message": "信用卡管理系统 API 服务正在运行",
            "timestamp": current_time.isoformat(),
            "timezone": "Asia/Shanghai"
        },
        message="服务运行正常"
    )

@app.get(
    "/health", 
    response_model=ApiResponse[dict],
    tags=["系统"],
    summary="健康检查",
    response_description="返回系统健康状态信息"
)
async def health_check():
    """
    系统健康检查
    
    检查系统各组件的运行状态，包括数据库连接、缓存服务等。
    返回详细的健康状态信息。
    """
    logger.info("健康检查请求")
    current_time = datetime.now(TIMEZONE)
    
    try:
        # 检查数据库连接
        db_health = get_db_health()
        
        # 检查各个组件状态
        checks = {
            "database": db_health.get("database", "unknown"),
            "redis": "not_configured",  # Redis暂未实现
            "config": "ok"
        }
        
        # 判断整体健康状态
        is_healthy = all(status in ["ok", "connected", "not_configured"] for status in checks.values())
        
        health_data = {
            "status": "healthy" if is_healthy else "unhealthy", 
            "service": "credit-card-management",
            "timestamp": current_time.isoformat(),
            "checks": checks,
            "environment": get_environment_info()
        }
        
        if is_healthy:
            logger.info("健康检查通过")
            return ResponseUtil.success(data=health_data, message="健康检查通过")
        else:
            logger.warning("健康检查发现问题")
            return ResponseUtil.error(data=health_data, message="服务健康检查发现问题")
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return ResponseUtil.server_error(message=f"服务健康检查失败: {str(e)}")

# 路由已分模块管理，具体实现请查看 routers/ 目录下的各模块文件

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 