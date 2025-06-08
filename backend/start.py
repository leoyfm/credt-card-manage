#!/usr/bin/env python3
"""
信用卡管理系统启动脚本

提供应用启动、数据库迁移、开发服务器等功能。
"""

import os
import sys
import argparse
import logging
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings, validate_config
from database import create_database, check_database_connection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """
    初始化数据库
    
    创建数据库表结构，用于首次部署。
    """
    logger.info("开始初始化数据库...")
    
    try:
        # 检查数据库连接
        if not check_database_connection():
            logger.error("数据库连接失败，请检查数据库配置")
            return False
        
        # 创建数据库表
        create_database()
        logger.info("数据库初始化成功")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False


def run_migrations():
    """
    运行数据库迁移
    
    使用Alembic执行数据库迁移。
    """
    logger.info("开始执行数据库迁移...")
    
    try:
        os.system("alembic upgrade head")
        logger.info("数据库迁移完成")
        return True
    except Exception as e:
        logger.error(f"数据库迁移失败: {str(e)}")
        return False


def create_migration(message: str):
    """
    创建新的数据库迁移
    
    Args:
        message: 迁移描述信息
    """
    logger.info(f"创建数据库迁移: {message}")
    
    try:
        os.system(f'alembic revision --autogenerate -m "{message}"')
        logger.info("迁移文件创建成功")
        return True
    except Exception as e:
        logger.error(f"创建迁移失败: {str(e)}")
        return False


def start_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1
):
    """
    启动Web服务器
    
    Args:
        host: 监听主机地址
        port: 监听端口
        reload: 是否启用热重载（开发模式）
        workers: 工作进程数（生产模式）
    """
    logger.info(f"启动Web服务器 - Host: {host}, Port: {port}")
    
    try:
        # 验证配置
        validate_config()
        logger.info("配置验证通过")
        
        # 检查数据库连接
        if not check_database_connection():
            logger.warning("数据库连接失败，但继续启动服务器")
        
        # 启动服务器
        if reload or settings.DEBUG:
            # 开发模式
            uvicorn.run(
                "main:app",
                host=host,
                port=port,
                reload=reload,
                log_level="info"
            )
        else:
            # 生产模式
            uvicorn.run(
                "main:app",
                host=host,
                port=port,
                workers=workers,
                log_level="info"
            )
            
    except Exception as e:
        logger.error(f"启动服务器失败: {str(e)}")
        sys.exit(1)


def main():
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description="信用卡管理系统启动脚本")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化数据库")
    
    # migrate 命令
    migrate_parser = subparsers.add_parser("migrate", help="运行数据库迁移")
    
    # makemigrations 命令
    makemigrations_parser = subparsers.add_parser("makemigrations", help="创建数据库迁移")
    makemigrations_parser.add_argument("-m", "--message", required=True, help="迁移描述")
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="启动Web服务器")
    run_parser.add_argument("--host", default="0.0.0.0", help="监听主机地址")
    run_parser.add_argument("--port", type=int, default=8000, help="监听端口")
    run_parser.add_argument("--reload", action="store_true", help="启用热重载")
    run_parser.add_argument("--workers", type=int, default=1, help="工作进程数")
    
    # dev 命令（开发模式快捷方式）
    dev_parser = subparsers.add_parser("dev", help="启动开发服务器")
    dev_parser.add_argument("--port", type=int, default=8000, help="监听端口")
    
    args = parser.parse_args()
    
    if args.command == "init":
        success = init_database()
        sys.exit(0 if success else 1)
        
    elif args.command == "migrate":
        success = run_migrations()
        sys.exit(0 if success else 1)
        
    elif args.command == "makemigrations":
        success = create_migration(args.message)
        sys.exit(0 if success else 1)
        
    elif args.command == "run":
        start_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers
        )
        
    elif args.command == "dev":
        logger.info("启动开发服务器...")
        start_server(
            host="127.0.0.1",
            port=args.port,
            reload=True
        )
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 