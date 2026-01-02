"""Настройка логирования."""
import logging
import sys
from datetime import datetime

def setup_logger(name: str = "race_info_bot") -> logging.Logger:
    """Настраивает и возвращает логгер."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Если логгер уже настроен, возвращаем его
    if logger.handlers:
        return logger
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger

