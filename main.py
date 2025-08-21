#!/usr/bin/env python3

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.gui import ImageEncryptorGUI
from utils.logger import setup_logger
from config import Config

def main():
    try:
        # Setup logging
        logger = setup_logger()
        logger.info("Starting ImageCrypt Application")
        
        # Create necessary directories
        Config.create_directories()
        
        # Launch GUI
        app = ImageEncryptorGUI()
        app.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
