"""
Configuration settings for the Image Encryption System
"""

import os
from pathlib import Path

class Config:
    """Application configuration"""
    
    # Base directories
    BASE_DIR = Path(__file__).parent
    IMAGES_DIR = BASE_DIR / "images"
    ORIGINAL_DIR = IMAGES_DIR / "original"
    ENCRYPTED_DIR = IMAGES_DIR / "encrypted"
    DECRYPTED_DIR = IMAGES_DIR / "decrypted"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Supported image formats
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp']
    
    # Encryption settings
    AES_KEY_SIZE = 32  # 256 bits
    AES_MODE = 'GCM'
    
    # GUI settings
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 650
    MIN_WINDOW_WIDTH = 800
    MIN_WINDOW_HEIGHT = 550
    
    # Colors (Dark theme)
    PRIMARY_COLOR = "#1f538d"
    SECONDARY_COLOR = "#14375e"
    ACCENT_COLOR = "#36719f"
    SUCCESS_COLOR = "#2d5a31"
    ERROR_COLOR = "#8b1538"
    WARNING_COLOR = "#8b6914"
    TEXT_COLOR = "#ffffff"
    BG_COLOR = "#212121"
    CARD_COLOR = "#2b2b2b"
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.IMAGES_DIR,
            cls.ORIGINAL_DIR,
            cls.ENCRYPTED_DIR,
            cls.DECRYPTED_DIR,
            cls.LOGS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
