"""
Key management for encryption and decryption operations
"""

import os
import base64
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from utils.logger import get_logger

logger = get_logger(__name__)

class KeyManager:
    """Manages encryption keys and key derivation"""
    
    def __init__(self):
        self.backend = default_backend()
        self.key_size = 32  # 256 bits for AES-256
    
    def generate_random_key(self) -> bytes:
        """
        Generate a cryptographically secure random key
        
        Returns:
            bytes: 32-byte random key for AES-256
        """
        try:
            key = secrets.token_bytes(self.key_size)
            logger.info("Generated new random encryption key")
            return key
            
        except Exception as e:
            logger.error(f"Failed to generate random key: {str(e)}")
            raise Exception(f"Failed to generate random key: {str(e)}")
    
    def derive_key_from_password(self, password: str, salt: bytes = None) -> tuple:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User-provided password
            salt: Salt for key derivation (generated if None)
            
        Returns:
            tuple: (derived_key, salt)
        """
        try:
            if salt is None:
                salt = os.urandom(16)
            
            # Create PBKDF2 instance
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.key_size,
                salt=salt,
                iterations=100000,  # OWASP recommended minimum
                backend=self.backend
            )
            
            # Derive key
            key = kdf.derive(password.encode('utf-8'))
            
            logger.info("Derived encryption key from password")
            return key, salt
            
        except Exception as e:
            logger.error(f"Failed to derive key from password: {str(e)}")
            raise Exception(f"Failed to derive key from password: {str(e)}")
    
    def key_to_string(self, key: bytes) -> str:
        """
        Convert key bytes to base64 string for display/storage
        
        Args:
            key: Key bytes
            
        Returns:
            str: Base64 encoded key string
        """
        try:
            key_string = base64.b64encode(key).decode('utf-8')
            logger.debug("Converted key to string format")
            return key_string
            
        except Exception as e:
            logger.error(f"Failed to convert key to string: {str(e)}")
            raise Exception(f"Failed to convert key to string: {str(e)}")
    
    def string_to_key(self, key_string: str) -> bytes:
        """
        Convert base64 string back to key bytes
        
        Args:
            key_string: Base64 encoded key string
            
        Returns:
            bytes: Key bytes
        """
        try:
            # Remove any whitespace
            key_string = key_string.strip()
            
            # Decode base64
            key = base64.b64decode(key_string.encode('utf-8'))
            
            # Validate key length
            if len(key) != self.key_size:
                raise ValueError(f"Invalid key length: {len(key)} bytes (expected {self.key_size})")
            
            logger.debug("Converted string to key format")
            return key
            
        except Exception as e:
            logger.error(f"Failed to convert string to key: {str(e)}")
            raise Exception(f"Invalid key format: {str(e)}")
    
    def validate_key(self, key: bytes) -> bool:
        """
        Validate that key is the correct size
        
        Args:
            key: Key bytes to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            is_valid = len(key) == self.key_size
            if is_valid:
                logger.debug("Key validation passed")
            else:
                logger.warning(f"Key validation failed: {len(key)} bytes (expected {self.key_size})")
            return is_valid
            
        except Exception as e:
            logger.error(f"Key validation error: {str(e)}")
            return False
