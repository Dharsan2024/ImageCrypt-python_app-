ImageCrypt-python_app

A modern desktop GUI application for secure image encryption and decryption with drag-and-drop interface and AES-256 encryption.

✨ Features

🎨 Modern GUI Interface
- Sleek dark-themed interface built with CustomTkinter
- Intuitive drag-and-drop functionality for easy file handling
- Clean card-based layout with smooth transitions
- Tabbed interface for encryption and decryption
- Save encrypted files to custom locations
- Real-time progress indicators during processing
- Before/after image comparison views

🔒 Security Features
- **AES-256 Encryption**: Military-grade encryption standard
- **Secure Key Generation**: Cryptographically secure random key generation
- **Key Management**: Safe key display with clipboard functionality
- **No Hardcoded Keys**: All keys are generated or user-provided
- **Memory Safety**: Data is properly cleared after operations

📁 File Support
- **Image Formats**: JPEG, PNG, BMP
- **Visual Preview**: Thumbnail previews for original and decrypted images
- **Organized Storage**: Automatic folder organization for different file types
- **Metadata Preservation**: Original filename and image properties preserved

🛡️ Security Considerations
- Keys are never embedded in encrypted files
- All encryption operations use secure random nonces
- Authentication tags prevent tampering
- Process logging for security auditing
- Error handling prevents information leakage

📋 Requirements

Python Dependencies
The application requires the following Python packages:
- `customtkinter` - Modern GUI framework
- `Pillow (PIL)` - Image processing
- `cryptography` - AES encryption implementation
- `pyperclip` - Clipboard operations
- `tkinterdnd2` - Drag and drop functionality
- `numpy` - Image data processing


🚀 Quick Start

Installation
1. Clone or download the project files
2. Install required dependencies:
   ```bash
   pip install customtkinter Pillow cryptography pyperclip tkinterdnd2 numpy
   ```

Running the Application
```bash
python main.py
