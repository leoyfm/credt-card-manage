import logging
import logging.handlers
import os
from .formatters import ColoredFormatter, JsonFormatter

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

class ConsoleHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.setFormatter(ColoredFormatter('%(asctime)s %(levelname)s %(name)s %(message)s'))

class FileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self):
        super().__init__(LOG_FILE, when="midnight", backupCount=30, encoding="utf-8")
        self.setFormatter(JsonFormatter())

# 预留ELK、Slack等处理器 