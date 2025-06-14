import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime, timedelta, timezone

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'logs')
LOG_DIR = os.path.abspath(LOG_DIR)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, 'app.log')

class JsonFormatter(logging.Formatter):
    def format(self, record):
        # 基础日志字段
        log_record = {
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        
        # 添加extra参数中的所有额外字段
        # 排除标准的LogRecord属性
        standard_attrs = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process', 'getMessage',
            'exc_info', 'exc_text', 'stack_info', 'message'
        }
        
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                # 确保值可以JSON序列化
                try:
                    json.dumps(value)
                    log_record[key] = value
                except (TypeError, ValueError):
                    # 如果不能序列化，转换为字符串
                    log_record[key] = str(value)
        
        return json.dumps(log_record, ensure_ascii=False)

class StructuredLogger:
    @staticmethod
    def get_logger(name: str = "app", level: int = logging.INFO) -> logging.Logger:
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger
        logger.setLevel(level)
        # 控制台
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)
        # 文件轮转
        file_handler = logging.handlers.TimedRotatingFileHandler(
            LOG_FILE, when="midnight", backupCount=30, encoding="utf-8"
        )
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        return logger

# 默认应用日志
app_logger = StructuredLogger.get_logger("app") 