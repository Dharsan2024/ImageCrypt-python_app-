"""
Image utility functions for loading, saving, and processing images
"""

import os
from PIL import Image, ImageTk
import numpy as np
from pathlib import Path
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class ImageProcessor:
    """Handles image loading, conversion, and processing"""
    
    def __init__(self):
        self.supported_formats = Config.SUPPORTED_FORMATS
    
    def is_supported_format(self, file_path: str) -> bool:
        """
        Check if file format is supported
        
        Args:
            file_path: Path to image file
            
        Returns:
            bool: True if supported, False otherwise
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_formats
    
    def load_image(self, image_path: str) -> Image.Image:
        """
        Load image from file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            PIL.Image: Loaded image
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            if not self.is_supported_format(image_path):
                raise ValueError(f"Unsupported image format: {Path(image_path).suffix}")
            
            # Load and validate image
            image = Image.open(image_path)
            image.verify()  # Verify it's a valid image
            
            # Reload image after verification (PIL requirement)
            image = Image.open(image_path)
            
            logger.info(f"Loaded image: {image_path} ({image.size[0]}x{image.size[1]})")
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {str(e)}")
            raise Exception(f"Failed to load image: {str(e)}")
    
    def image_to_bytes(self, image: Image.Image) -> tuple:
        """
        Convert PIL Image to bytes
        
        Args:
            image: PIL Image object
            
        Returns:
            tuple: (image_bytes, image_shape)
        """
        try:
            # Convert to RGB if necessary (for consistency)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get image shape
            width, height = image.size
            channels = len(image.getbands())
            image_shape = (width, height, channels)
            
            # Convert to numpy array and then to bytes
            image_array = np.array(image)
            image_bytes = image_array.tobytes()
            
            logger.debug(f"Converted image to bytes: {len(image_bytes)} bytes")
            
            return image_bytes, image_shape
            
        except Exception as e:
            logger.error(f"Failed to convert image to bytes: {str(e)}")
            raise Exception(f"Failed to convert image to bytes: {str(e)}")
    
    def bytes_to_image(self, image_bytes: bytes, image_shape: tuple) -> Image.Image:
        """
        Convert bytes back to PIL Image
        
        Args:
            image_bytes: Raw image bytes
            image_shape: Image dimensions (width, height, channels)
            
        Returns:
            PIL.Image: Reconstructed image
        """
        try:
            width, height, channels = image_shape
            
            # Convert bytes to numpy array
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image_array = image_array.reshape((height, width, channels))
            
            # Convert to PIL Image
            image = Image.fromarray(image_array, 'RGB')
            
            logger.debug(f"Converted bytes to image: {width}x{height}")
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to convert bytes to image: {str(e)}")
            raise Exception(f"Failed to convert bytes to image: {str(e)}")
    
    def resize_for_display(self, image: Image.Image, max_size: tuple = (300, 300)) -> Image.Image:
        """
        Resize image for display while maintaining aspect ratio
        
        Args:
            image: PIL Image to resize
            max_size: Maximum dimensions (width, height)
            
        Returns:
            PIL.Image: Resized image
        """
        try:
            # Calculate scaling factor
            width_ratio = max_size[0] / image.size[0]
            height_ratio = max_size[1] / image.size[1]
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new size
            new_width = int(image.size[0] * scale_factor)
            new_height = int(image.size[1] * scale_factor)
            
            # Resize image
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            logger.debug(f"Resized image from {image.size} to {resized_image.size}")
            
            return resized_image
            
        except Exception as e:
            logger.error(f"Failed to resize image: {str(e)}")
            return image  # Return original if resize fails
    
    def create_thumbnail(self, image: Image.Image, size: tuple = (150, 150)) -> ImageTk.PhotoImage:
        """
        Create a thumbnail for GUI display
        
        Args:
            image: PIL Image
            size: Thumbnail size
            
        Returns:
            ImageTk.PhotoImage: Thumbnail for tkinter display
        """
        try:
            # Resize image
            thumbnail = self.resize_for_display(image, size)
            
            # Convert to PhotoImage for tkinter
            photo = ImageTk.PhotoImage(thumbnail)
            
            logger.debug(f"Created thumbnail: {thumbnail.size}")
            
            return photo
            
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {str(e)}")
            # Return a placeholder or None
            return None
    
    def save_image(self, image: Image.Image, output_path: str, quality: int = 95):
        """
        Save PIL Image to file
        
        Args:
            image: PIL Image to save
            output_path: Output file path
            quality: JPEG quality (0-100)
        """
        try:
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save image
            if Path(output_path).suffix.lower() in ['.jpg', '.jpeg']:
                image.save(output_path, 'JPEG', quality=quality)
            else:
                image.save(output_path)
            
            logger.info(f"Saved image to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save image to {output_path}: {str(e)}")
            raise Exception(f"Failed to save image: {str(e)}")
