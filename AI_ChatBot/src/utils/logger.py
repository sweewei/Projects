import logging
import sys
from pathlib import Path
from config.settings import settings

def setup_logger(name: str = __name__) -> logging.Logger:
    """設置標準化日誌"""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # 格式化器
    formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger

# 全域日誌實例
logger = setup_logger(__name__)