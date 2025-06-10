"""结构化日志记录器"""

import logging
import json
from datetime import datetime
from typing import Dict, Any
from ..config import settings

class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
    def _format_message(self, level: str, message: str, extra: Dict[str, Any] = None) -> str:
        """格式化日志消息为JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.logger.name,
            "message": message,
            "extra": extra or {}
        }
        return json.dumps(log_entry, ensure_ascii=False)
    
    def info(self, message: str, **kwargs):
        """记录INFO级别日志"""
        self.logger.info(self._format_message("INFO", message, kwargs))
    
    def error(self, message: str, **kwargs):
        """记录ERROR级别日志"""
        self.logger.error(self._format_message("ERROR", message, kwargs))
    
    def warning(self, message: str, **kwargs):
        """记录WARNING级别日志"""
        self.logger.warning(self._format_message("WARNING", message, kwargs))
    
    def debug(self, message: str, **kwargs):
        """记录DEBUG级别日志"""
        self.logger.debug(self._format_message("DEBUG", message, kwargs))

def get_logger(name: str) -> StructuredLogger:
    """获取结构化日志记录器"""
    return StructuredLogger(name) 