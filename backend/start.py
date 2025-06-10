#!/usr/bin/env python3
"""系统启动脚本

用法:
python start.py [mode]

模式:
- dev: 开发模式 (默认)
- prod: 生产模式
- test: 测试模式
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_simple_app():
    """创建一个简单的FastAPI应用用于调试启动问题"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="信用卡管理系统",
        version="2.0.0",
        description="信用卡管理系统后端API",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "success": True,
            "code": 200,
            "message": "欢迎使用信用卡管理系统API v2.0",
            "data": {
                "version": "2.0.0",
                "status": "running",
                "docs_url": "/docs"
            }
        }
    
    @app.get("/health")
    async def health():
        """健康检查"""
        return {
            "success": True,
            "code": 200,
            "message": "系统运行正常",
            "data": {
                "status": "healthy",
                "timestamp": "2024-12-01T10:00:00Z"
            }
        }
    
    return app

def start_server(mode="dev"):
    """启动服务器"""
    import uvicorn
    
    # 创建简单应用
    app = create_simple_app()
    
    # 根据模式设置参数
    if mode == "dev":
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    elif mode == "prod":
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="warning"
        )
    elif mode == "test":
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="debug"
        )
    else:
        print(f"未知模式: {mode}")
        print("可用模式: dev, prod, test")
        sys.exit(1)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "dev"
    print(f"启动信用卡管理系统 - 模式: {mode}")
    start_server(mode) 