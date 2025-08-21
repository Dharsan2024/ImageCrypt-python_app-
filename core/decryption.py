"""
Image decryption module for AES-256 encrypted images
"""

import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from utils.logger import get_logger

logger = get_logger(__name__)

class ImageDecryptor:
    """Handles image decryption using AES-256"""
    
    def __init__(self):
        self.backend = default_backend()
    
    def load_encrypted_package(self, encrypted_file_path: str) -> dict:
        """
        Load and parse encrypted package from file
        
        Args:
            encrypted_file_path: Path to encrypted file
            
        Returns:
            dict: Parsed package data
        """
        try:
            with open(encrypted_file_path, 'rb') as f:
                package_bytes = f.read()
            
            # Decode JSON
            package_json = package_bytes.decode('utf-8')
            package = json.loads(package_json)
            
            logger.info(f"Loaded encrypted package from: {encrypted_file_path}")
            
            return package
            
        except Exception as e:
            logger.error(f"Failed to load encrypted package: {str(e)}")
            raise Exception(f"Failed to load encrypted package: {str(e)}")
    
    def decrypt_image_data(self, ciphertext: bytes, key: bytes, 
                          nonce: bytes, tag: bytes) -> bytes:
        """
        Decrypt image data using AES-256-GCM
        
        Args:
            ciphertext: Encrypted image data
            key: 32-byte decryption key
            nonce: Nonce used during encryption
            tag: Authentication tag
            
        Returns:
            bytes: Decrypted image data
        """
        try:
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=self.backend
            )
            
            # Decrypt the data
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            logger.info(f"Successfully decrypted {len(plaintext)} bytes of image data")
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise Exception(f"Decryption failed - Invalid key or corrupted data: {str(e)}")
    
    def decrypt_package(self, encrypted_file_path: str, key: bytes) -> tuple:
        """
        Decrypt a complete encrypted package
        
        Args:
            encrypted_file_path: Path to encrypted file
            key: Decryption key
            
        Returns:
            tuple: (image_data, metadata)
        """
        try:
            # Load the encrypted package
            package = self.load_encrypted_package(encrypted_file_path)
            
            # Extract components
            metadata = package['metadata']
            nonce = base64.b64decode(package['nonce'].encode('utf-8'))
            tag = base64.b64decode(package['tag'].encode('utf-8'))
            ciphertext = base64.b64decode(package['ciphertext'].encode('utf-8'))
            
            # Decrypt the image data
            image_data = self.decrypt_image_data(ciphertext, key, nonce, tag)
            
            logger.info(f"Successfully decrypted package: {metadata['original_filename']}")
            
            return image_data, metadata
            
        except Exception as e:
            logger.error(f"Failed to decrypt package: {str(e)}")
            raise Exception(f"Failed to decrypt package: {str(e)}")
    
    def save_decrypted_image(self, image_data: bytes, output_path: str):
        """
        Save decrypted image data to file
        
        Args:
            image_data: Decrypted image bytes
            output_path: Output file path
        """
        try:
            with open(output_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Decrypted image saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save decrypted image: {str(e)}")
            raise Exception(f"Failed to save decrypted image: {str(e)}")
