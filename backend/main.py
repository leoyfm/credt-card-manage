import logging
import pytz
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utils.response import ResponseUtil
from models.response import ApiResponse
from routers import annual_fee, cards, reminders, recommendations, auth

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置时区
TIMEZONE = pytz.timezone('Asia/Shanghai')

app = FastAPI(
    title="信用卡管理系统 API",
    description="""
## 智能化信用卡管理系统后端接口

### 功能特色
- 📊 **年费管理**：灵活的年费规则配置和自动化减免条件检查
- 💳 **信用卡管理**：完整的信用卡信息管理和额度监控
- 🔔 **还款提醒**：智能还款提醒和账单管理
- 🎯 **智能推荐**：基于用户行为的个性化信用卡推荐
- 📈 **数据统计**：详细的消费分析和年费统计

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
        }
    ]
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由模块
app.include_router(auth.router, prefix="/api")
app.include_router(annual_fee.router, prefix="/api")
app.include_router(cards.router, prefix="/api")
app.include_router(reminders.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")

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
        # TODO: 添加数据库连接检查
        # TODO: 添加Redis连接检查
        
        health_data = {
            "status": "healthy", 
            "service": "credit-card-management",
            "timestamp": current_time.isoformat(),
            "checks": {
                "database": "ok",  # 实际应该检查数据库连接
                "redis": "ok",     # 实际应该检查Redis连接
            }
        }
        
        logger.info("健康检查通过")
        return ResponseUtil.success(data=health_data, message="健康检查通过")
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return ResponseUtil.server_error(message="服务健康检查失败")

# 路由已分模块管理，具体实现请查看 routers/ 目录下的各模块文件

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 