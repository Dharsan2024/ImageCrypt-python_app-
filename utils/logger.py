"""
Logging configuration and utilities
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from config import Config

def setup_logger() -> logging.Logger:
    """
    Setup the main application logger
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Config.LOGS_DIR / f"image_encryptor_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    logger = logging.getLogger('ImageEncryptor')
    logger.info(f"Logging initialized - Log file: {log_file}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(f'ImageEncryptor.{name}')
