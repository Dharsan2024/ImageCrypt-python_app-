"""
Image encryption module using AES-256 encryption
"""

import os
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from utils.logger import get_logger

logger = get_logger(__name__)

class ImageEncryptor:
    """Handles image encryption using AES-256"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def encrypt_image_data(self, image_data: bytes, key: bytes) -> tuple:
        """
        Encrypt image data using AES-256-GCM
        
        Args:
            image_data: Raw image bytes
            key: 32-byte encryption key
            
        Returns:
            tuple: (encrypted_data, nonce, tag)
        """
        try:
            # Generate a random nonce for GCM mode
            nonce = os.urandom(12)  # GCM uses 12-byte nonce
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce),
                backend=self.backend
            )
            
            # Encrypt the data
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(image_data) + encryptor.finalize()
            
            logger.info(f"Successfully encrypted {len(image_data)} bytes of image data")
            
            return ciphertext, nonce, encryptor.tag
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise Exception(f"Encryption failed: {str(e)}")
    
    def create_encrypted_package(self, image_data: bytes, key: bytes, 
                                original_filename: str, image_shape: tuple) -> bytes:
        """
        Create an encrypted package containing image data and metadata
        
        Args:
            image_data: Raw image bytes
            key: Encryption key
            original_filename: Original image filename
            image_shape: Image dimensions (width, height, channels)
            
        Returns:
            bytes: Complete encrypted package
        """
        try:
            # Encrypt the image data
            ciphertext, nonce, tag = self.encrypt_image_data(image_data, key)
            
            # Create metadata
            metadata = {
                'original_filename': original_filename,
                'image_shape': image_shape,
                'version': '1.0'
            }
            
            # Create the package
            package = {
                'metadata': metadata,
                'nonce': base64.b64encode(nonce).decode('utf-8'),
                'tag': base64.b64encode(tag).decode('utf-8'),
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
            }
            
            # Convert to JSON and encode
            package_json = json.dumps(package, indent=2)
            package_bytes = package_json.encode('utf-8')
            
            logger.info(f"Created encrypted package for {original_filename}")
            
            return package_bytes
            
        except Exception as e:
            logger.error(f"Failed to create encrypted package: {str(e)}")
            raise Exception(f"Failed to create encrypted package: {str(e)}")
    
    def save_encrypted_file(self, package_bytes: bytes, output_path: str):
        """
        Save encrypted package to file
        
        Args:
            package_bytes: Encrypted package data
            output_path: Output file path
        """
        try:
            with open(output_path, 'wb') as f:
                f.write(package_bytes)
            
            logger.info(f"Encrypted file saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save encrypted file: {str(e)}")
            raise Exception(f"Failed to save encrypted file: {str(e)}")
