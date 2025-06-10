"""日志系统初始化"""

import logging.config
import os
from ..config import settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": "%(message)s"
        },
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_FILE_PATH,
            "maxBytes": 50 * 1024 * 1024,  # 50MB
            "backupCount": 30,
            "formatter": "json",
            "level": settings.LOG_LEVEL
        }
    },
    "root": {
        "level": settings.LOG_LEVEL,
        "handlers": ["console", "file"]
    }
}

def setup_logging():
    """设置日志配置"""
    os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)

# 自动初始化
setup_logging() 