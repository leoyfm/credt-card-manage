from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="信用卡管理系统 API",
    description="智能化信用卡管理系统后端接口",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "信用卡管理系统 API 服务正在运行"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "credit-card-management"}

# 信用卡相关路由
@app.get("/api/cards")
async def get_cards():
    return {"cards": [], "message": "获取信用卡列表"}

@app.post("/api/cards")
async def create_card():
    return {"message": "创建信用卡成功"}

# 还款提醒相关路由
@app.get("/api/reminders")
async def get_reminders():
    return {"reminders": [], "message": "获取还款提醒列表"}

# 智能推荐相关路由
@app.get("/api/recommendations")
async def get_recommendations():
    return {"recommendations": [], "message": "获取信用卡推荐"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 