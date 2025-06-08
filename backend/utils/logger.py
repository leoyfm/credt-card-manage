"""
日志配置工具

提供统一的日志配置，确保所有日志都能正确记录到文件和控制台。
"""

import logging
import os
from pathlib import Path
from datetime import datetime


class LogConfig:
    """日志配置类"""
    
    # 日志格式
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # 日志文件设置
    LOG_DIR = 'logs'
    LOG_FILE = 'app.log'
    
    @classmethod
    def setup_logging(cls, log_level=logging.INFO):
        """
        设置日志配置
        
        Args:
            log_level: 日志级别，默认INFO
        """
        # 确保日志目录存在
        log_dir = Path(cls.LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # 清除现有的处理器，避免重复
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建格式化器
        formatter = logging.Formatter(
            fmt=cls.LOG_FORMAT,
            datefmt=cls.DATE_FORMAT
        )
        
        # 创建文件处理器
        log_file_path = log_dir / cls.LOG_FILE
        file_handler = logging.FileHandler(
            log_file_path, 
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        # 配置根日志器
        root_logger.setLevel(log_level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # 记录日志配置启动信息
        logger = logging.getLogger(__name__)
        logger.info("日志系统初始化完成")
        logger.info(f"日志文件: {log_file_path.absolute()}")
        logger.info(f"日志级别: {logging.getLevelName(log_level)}")
        
        return logger

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取日志器
        
        Args:
            name: 日志器名称
            
        Returns:
            logging.Logger: 日志器实例
        """
        return logging.getLogger(name)

    @classmethod
    def log_request(cls, method: str, url: str, status_code: int, duration: float = None):
        """
        记录HTTP请求日志
        
        Args:
            method: HTTP方法
            url: 请求URL
            status_code: 状态码
            duration: 请求耗时（秒）
        """
        logger = cls.get_logger('request')
        duration_str = f" - {duration:.3f}s" if duration else ""
        logger.info(f"{method} {url} - {status_code}{duration_str}")

    @classmethod
    def log_error(cls, error: Exception, context: str = None):
        """
        记录错误日志
        
        Args:
            error: 异常对象
            context: 错误上下文信息
        """
        logger = cls.get_logger('error')
        context_str = f" - 上下文: {context}" if context else ""
        logger.error(f"{type(error).__name__}: {str(error)}{context_str}", exc_info=True)

    @classmethod
    def log_business_operation(cls, operation: str, user_id: str = None, details: str = None):
        """
        记录业务操作日志
        
        Args:
            operation: 操作类型
            user_id: 用户ID
            details: 操作详情
        """
        logger = cls.get_logger('business')
        user_str = f" - 用户: {user_id}" if user_id else ""
        details_str = f" - 详情: {details}" if details else ""
        logger.info(f"业务操作: {operation}{user_str}{details_str}")


def setup_uvicorn_logging():
    """
    设置uvicorn的日志配置，防止覆盖我们的日志配置
    """
    # 禁用uvicorn的默认日志配置
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    
    # 让uvicorn使用我们的日志配置
    uvicorn_logger.propagate = True
    uvicorn_access_logger.propagate = True


# 初始化日志配置
def init_logging():
    """初始化日志系统"""
    LogConfig.setup_logging()
    setup_uvicorn_logging()
    
    # 记录初始化完成
    logger = LogConfig.get_logger(__name__)
    logger.info("日志系统已初始化") 