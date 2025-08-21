"""
Modern GUI for Image Encryption & Decryption System using CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import shutil
from pathlib import Path
from PIL import Image, ImageTk
import pyperclip

# Try to import tkinterdnd2 for drag and drop, fallback gracefully
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False

from config import Config
from core.encryption import ImageEncryptor
from core.decryption import ImageDecryptor
from core.key_manager import KeyManager
from utils.image_utils import ImageProcessor
from utils.logger import get_logger

logger = get_logger(__name__)

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DragDropFrame(ctk.CTkFrame):
    """Custom frame that supports drag and drop functionality"""
    
    def __init__(self, parent, drop_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.drop_callback = drop_callback
        self.is_drag_over = False
        
        # Enable drag and drop if available
        if DRAG_DROP_AVAILABLE and hasattr(parent, 'tk') and hasattr(parent.tk, 'call'):
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self._on_drop)
                self.dnd_bind('<<DragEnter>>', self._on_drag_enter)
                self.dnd_bind('<<DragLeave>>', self._on_drag_leave)
            except Exception as e:
                logger.warning(f"Drag and drop setup failed: {e}")
        
        # Visual feedback bindings
        self.bind('<Button-1>', self._on_click)
    
    def _on_drop(self, event):
        """Handle file drop event"""
        if self.drop_callback and hasattr(event, 'data'):
            files = self.tk.splitlist(event.data)
            if files:
                self.drop_callback(files[0])
    
    def _on_drag_enter(self, event):
        """Visual feedback when dragging over"""
        self.is_drag_over = True
        self.configure(border_color=Config.ACCENT_COLOR, border_width=2)
    
    def _on_drag_leave(self, event):
        """Remove visual feedback when leaving"""
        self.is_drag_over = False
        self.configure(border_color="transparent", border_width=0)
    
    def _on_click(self, event):
        """Handle click event for manual file selection"""
        if self.drop_callback:
            self.drop_callback(None)  # Signal for manual file selection

class ProgressDialog(ctk.CTkToplevel):
    """Progress dialog for long-running operations"""
    
    def __init__(self, parent, title="Processing..."):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.winfo_screenheight() // 2) - (150 // 2)
        self.geometry(f"400x150+{x}+{y}")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self, width=350, height=20)
        self.progress.pack(pady=20)
        self.progress.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(self, text="Initializing...")
        self.status_label.pack(pady=10)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self, text="Cancel", command=self.destroy,
            width=100, height=30
        )
        self.cancel_button.pack(pady=10)
        
        self.cancelled = False
    
    def update_progress(self, value, status=""):
        """Update progress bar and status"""
        self.progress.set(value)
        if status:
            self.status_label.configure(text=status)
        self.update()
    
    def set_cancelled(self):
        """Mark as cancelled"""
        self.cancelled = True
        self.destroy()

class ImageEncryptorGUI:
    """Main GUI application for image encryption and decryption"""
    
    def __init__(self):
        # Initialize components
        self.encryptor = ImageEncryptor()
        self.decryptor = ImageDecryptor()
        self.key_manager = KeyManager()
        self.image_processor = ImageProcessor()
        
        # GUI state
        self.current_image = None
        self.current_image_path = None
        self.encryption_key = None
        self.current_key_string = ""
        self.encrypted_file_path = None
        
        # Setup main window
        self.setup_window()
        self.create_widgets()
        
        logger.info("GUI initialized successfully")
    
    def setup_window(self):
        """Setup the main application window"""
        # Use TkinterDnD if available
        if DRAG_DROP_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = ctk.CTk()
        
        self.root.title("ImageCrypt - Secure Image Encryption")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.minsize(Config.MIN_WINDOW_WIDTH, Config.MIN_WINDOW_HEIGHT)
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🔐 ImageCrypt",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 30))
        
        # Create tabs
        self.create_tabs()
    
    def create_tabs(self):
        """Create tabbed interface for encryption and decryption"""
        self.tabview = ctk.CTkTabview(self.main_frame, width=950, height=600)
        self.tabview.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
        
        # Encryption tab
        self.encrypt_tab = self.tabview.add("🔒 Encrypt Image")
        self.create_encryption_tab()
        
        # Decryption tab
        self.decrypt_tab = self.tabview.add("🔓 Decrypt Image")
        self.create_decryption_tab()
    
    def create_encryption_tab(self):
        """Create the encryption interface"""
        # Configure grid
        self.encrypt_tab.grid_columnconfigure(0, weight=1)
        self.encrypt_tab.grid_columnconfigure(1, weight=1)
        
        # Left side - Image selection and preview
        left_frame = ctk.CTkFrame(self.encrypt_tab)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Image drop area
        self.image_drop_frame = DragDropFrame(
            left_frame, 
            drop_callback=self.handle_image_drop,
            height=200
        )
        self.image_drop_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Drop area instructions
        drop_text = "📁 Drag & Drop Image Here\nor Click to Browse"
        if not DRAG_DROP_AVAILABLE:
            drop_text = "📁 Click to Browse for Image"
        
        self.drop_label = ctk.CTkLabel(
            self.image_drop_frame,
            text=drop_text,
            font=ctk.CTkFont(size=16),
            height=150
        )
        self.drop_label.grid(row=0, column=0, pady=50)
        
        # Browse button
        browse_btn = ctk.CTkButton(
            left_frame,
            text="Browse for Image",
            command=self.browse_image,
            width=200, height=40
        )
        browse_btn.grid(row=1, column=0, pady=10)
        
        # Image preview
        self.image_preview_frame = ctk.CTkFrame(left_frame)
        self.image_preview_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        
        self.preview_label = ctk.CTkLabel(
            self.image_preview_frame,
            text="No image selected",
            height=200
        )
        self.preview_label.grid(row=0, column=0, pady=20)
        
        # Right side - Encryption controls
        right_frame = ctk.CTkFrame(self.encrypt_tab)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Encryption options
        encrypt_title = ctk.CTkLabel(
            right_frame,
            text="🔐 Encryption Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        encrypt_title.grid(row=0, column=0, pady=(20, 10))
        
        # Key generation
        key_frame = ctk.CTkFrame(right_frame)
        key_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        key_frame.grid_columnconfigure(0, weight=1)
        
        key_label = ctk.CTkLabel(key_frame, text="Encryption Key:")
        key_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Key display area
        self.key_display = ctk.CTkTextbox(key_frame, height=80, wrap="word")
        self.key_display.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Key buttons
        key_buttons_frame = ctk.CTkFrame(key_frame, fg_color="transparent")
        key_buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        key_buttons_frame.grid_columnconfigure(0, weight=1)
        key_buttons_frame.grid_columnconfigure(1, weight=1)
        
        generate_key_btn = ctk.CTkButton(
            key_buttons_frame,
            text="Generate Key",
            command=self.generate_key,
            width=120, height=30
        )
        generate_key_btn.grid(row=0, column=0, padx=(0, 5))
        
        copy_key_btn = ctk.CTkButton(
            key_buttons_frame,
            text="Copy Key",
            command=self.copy_key,
            width=120, height=30
        )
        copy_key_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Encrypt button
        self.encrypt_btn = ctk.CTkButton(
            right_frame,
            text="🔒 Encrypt Image",
            command=self.encrypt_image,
            width=200, height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled"
        )
        self.encrypt_btn.grid(row=2, column=0, pady=30)
        
        # Status display
        self.encrypt_status = ctk.CTkLabel(
            right_frame,
            text="Select an image and generate a key to begin",
            wraplength=300
        )
        self.encrypt_status.grid(row=3, column=0, pady=10)
    
    def create_decryption_tab(self):
        """Create the decryption interface"""
        # Configure grid
        self.decrypt_tab.grid_columnconfigure(0, weight=1)
        self.decrypt_tab.grid_columnconfigure(1, weight=1)
        
        # Left side - Encrypted file selection
        left_frame = ctk.CTkFrame(self.decrypt_tab)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Encrypted file drop area
        self.encrypted_drop_frame = DragDropFrame(
            left_frame, 
            drop_callback=self.handle_encrypted_drop,
            height=200
        )
        self.encrypted_drop_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Drop area instructions
        drop_text = "🔒 Drop Encrypted File Here\nor Click to Browse"
        if not DRAG_DROP_AVAILABLE:
            drop_text = "🔒 Click to Browse for Encrypted File"
        
        self.encrypted_drop_label = ctk.CTkLabel(
            self.encrypted_drop_frame,
            text=drop_text,
            font=ctk.CTkFont(size=16),
            height=150
        )
        self.encrypted_drop_label.grid(row=0, column=0, pady=50)
        
        # Browse encrypted file button
        browse_encrypted_btn = ctk.CTkButton(
            left_frame,
            text="Browse Encrypted File",
            command=self.browse_encrypted_file,
            width=200, height=40
        )
        browse_encrypted_btn.grid(row=1, column=0, pady=10)
        
        # File info display
        self.file_info_frame = ctk.CTkFrame(left_frame)
        self.file_info_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        
        self.file_info_label = ctk.CTkLabel(
            self.file_info_frame,
            text="No encrypted file selected",
            height=200
        )
        self.file_info_label.grid(row=0, column=0, pady=20)
        
        # Right side - Decryption controls
        right_frame = ctk.CTkFrame(self.decrypt_tab)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Decryption options
        decrypt_title = ctk.CTkLabel(
            right_frame,
            text="🔓 Decryption Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        decrypt_title.grid(row=0, column=0, pady=(20, 10))
        
        # Key input
        key_input_frame = ctk.CTkFrame(right_frame)
        key_input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        key_input_frame.grid_columnconfigure(0, weight=1)
        
        key_input_label = ctk.CTkLabel(key_input_frame, text="Enter Decryption Key:")
        key_input_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Key input area
        self.key_input = ctk.CTkTextbox(key_input_frame, height=80, wrap="word")
        self.key_input.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Paste key button
        paste_key_btn = ctk.CTkButton(
            key_input_frame,
            text="Paste Key",
            command=self.paste_key,
            width=120, height=30
        )
        paste_key_btn.grid(row=2, column=0, pady=10)
        
        # Decrypt button
        self.decrypt_btn = ctk.CTkButton(
            right_frame,
            text="🔓 Decrypt Image",
            command=self.decrypt_image,
            width=200, height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled"
        )
        self.decrypt_btn.grid(row=2, column=0, pady=30)
        
        # Status display
        self.decrypt_status = ctk.CTkLabel(
            right_frame,
            text="Select an encrypted file and enter the key to begin",
            wraplength=300
        )
        self.decrypt_status.grid(row=3, column=0, pady=10)
        
        # Decrypted image preview
        self.decrypted_preview_frame = ctk.CTkFrame(right_frame)
        self.decrypted_preview_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=20)
        
        self.decrypted_preview_label = ctk.CTkLabel(
            self.decrypted_preview_frame,
            text="Decrypted image will appear here",
            height=150
        )
        self.decrypted_preview_label.grid(row=0, column=0, pady=20)
    

    
    def handle_image_drop(self, file_path):
        """Handle image drop or click event"""
        if file_path is None:
            # Manual file selection
            self.browse_image()
        else:
            # File dropped
            self.load_image(file_path)
    
    def handle_encrypted_drop(self, file_path):
        """Handle encrypted file drop or click event"""
        if file_path is None:
            # Manual file selection
            self.browse_encrypted_file()
        else:
            # File dropped
            self.load_encrypted_file(file_path)
    
    def browse_image(self):
        """Open file browser to select an image"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Image to Encrypt",
            filetypes=filetypes
        )
        
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        """Load and display the selected image"""
        try:
            # Load image
            self.current_image = self.image_processor.load_image(file_path)
            self.current_image_path = file_path
            
            # Update preview
            thumbnail = self.image_processor.create_thumbnail(self.current_image, (250, 250))
            if thumbnail:
                self.preview_label.configure(image=thumbnail, text="")
                # Keep reference to prevent garbage collection
                self.preview_label._image_ref = thumbnail
            
            # Update drop label
            filename = Path(file_path).name
            self.drop_label.configure(text=f"Selected: {filename}")
            
            # Update status
            size = self.current_image.size
            self.encrypt_status.configure(
                text=f"Image loaded: {filename}\nSize: {size[0]}x{size[1]} pixels\nGenerate a key to encrypt"
            )
            
            # Enable encrypt button if key is available
            self.update_encrypt_button_state()
            
            logger.info(f"Image loaded for encryption: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")
            logger.error(f"Failed to load image {file_path}: {str(e)}")
    
    def generate_key(self):
        """Generate a new encryption key"""
        try:
            self.encryption_key = self.key_manager.generate_random_key()
            self.current_key_string = self.key_manager.key_to_string(self.encryption_key)
            
            # Display key
            self.key_display.delete("1.0", "end")
            self.key_display.insert("1.0", self.current_key_string)
            
            # Update status
            self.encrypt_status.configure(
                text="✅ Encryption key generated!\nYou can now encrypt the image.\n\n⚠️ IMPORTANT: Save this key - you'll need it to decrypt!"
            )
            
            # Enable encrypt button if image is loaded
            self.update_encrypt_button_state()
            
            logger.info("New encryption key generated")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate key:\n{str(e)}")
            logger.error(f"Key generation failed: {str(e)}")
    
    def copy_key(self):
        """Copy the encryption key to clipboard"""
        if self.current_key_string:
            try:
                pyperclip.copy(self.current_key_string)
                messagebox.showinfo("Success", "Encryption key copied to clipboard!")
                logger.info("Encryption key copied to clipboard")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy key:\n{str(e)}")
        else:
            messagebox.showwarning("Warning", "No key to copy. Generate a key first.")
    
    def update_encrypt_button_state(self):
        """Update the encrypt button state based on current conditions"""
        if self.current_image and self.encryption_key:
            self.encrypt_btn.configure(state="normal")
        else:
            self.encrypt_btn.configure(state="disabled")
    
    def encrypt_image(self):
        """Encrypt the current image"""
        if not self.current_image or not self.encryption_key or not self.current_image_path:
            messagebox.showwarning("Warning", "Please select an image and generate a key first.")
            return
        
        def encryption_task():
            """Background encryption task"""
            try:
                progress_dialog.update_progress(0.1, "Converting image to bytes...")
                
                # Convert image to bytes
                image_bytes, image_shape = self.image_processor.image_to_bytes(self.current_image)
                
                progress_dialog.update_progress(0.3, "Encrypting image data...")
                
                # Create encrypted package
                filename = Path(self.current_image_path).name
                package_bytes = self.encryptor.create_encrypted_package(
                    image_bytes, self.encryption_key, filename, image_shape
                )
                
                progress_dialog.update_progress(0.7, "Saving encrypted file...")
                
                # Save encrypted file
                encrypted_filename = f"encrypted_{filename}.enc"
                encrypted_path = Config.ENCRYPTED_DIR / encrypted_filename
                
                self.encryptor.save_encrypted_file(package_bytes, str(encrypted_path))
                
                progress_dialog.update_progress(1.0, "Encryption completed!")
                
                # Show success message
                self.root.after(0, lambda: self.show_encryption_success(encrypted_path, filename))
                
            except Exception as e:
                logger.error(f"Encryption failed: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Encryption Failed", str(e)))
            finally:
                if hasattr(self, 'progress_dialog') and not progress_dialog.cancelled:
                    progress_dialog.destroy()
        
        # Show progress dialog
        progress_dialog = ProgressDialog(self.root, "Encrypting Image...")
        
        # Start encryption in background thread
        thread = threading.Thread(target=encryption_task, daemon=True)
        thread.start()
    
    def show_encryption_success(self, encrypted_path, original_filename):
        """Show encryption success message and offer save options"""
        # Ask user if they want to save the encrypted file somewhere else
        result = messagebox.askyesno(
            "Encryption Successful", 
            f"✅ Image encrypted successfully!\n\n"
            f"Original: {original_filename}\n"
            f"Encrypted file: {encrypted_path.name}\n\n"
            f"⚠️ IMPORTANT: Save your encryption key!\n"
            f"You'll need it to decrypt the image.\n\n"
            f"Would you like to save the encrypted file to a different location?"
        )
        
        if result:
            self.save_encrypted_file_as(encrypted_path)
        
        # Update status
        self.encrypt_status.configure(
            text=f"✅ Encryption completed!\nFile saved: {encrypted_path.name}"
        )
        
        logger.info(f"Encryption completed: {encrypted_path}")
    
    def save_encrypted_file_as(self, encrypted_path):
        """Save encrypted file to a user-selected location"""
        try:
            # Get save location from user
            save_path = filedialog.asksaveasfilename(
                title="Save Encrypted File As",
                defaultextension=".enc",
                filetypes=[
                    ("Encrypted files", "*.enc"),
                    ("All files", "*.*")
                ],
                initialfile=encrypted_path.name
            )
            
            if save_path:
                # Copy the encrypted file to the new location
                shutil.copy2(encrypted_path, save_path)
                messagebox.showinfo(
                    "File Saved", 
                    f"Encrypted file saved to:\n{save_path}"
                )
                logger.info(f"Encrypted file copied to: {save_path}")
                
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{str(e)}")
            logger.error(f"Failed to save encrypted file: {str(e)}")
    
    def browse_encrypted_file(self):
        """Browse for encrypted file to decrypt"""
        filetypes = [
            ("Encrypted files", "*.enc"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Encrypted File",
            filetypes=filetypes,
            initialdir=str(Config.ENCRYPTED_DIR)
        )
        
        if file_path:
            self.load_encrypted_file(file_path)
    
    def load_encrypted_file(self, file_path):
        """Load encrypted file information"""
        try:
            self.encrypted_file_path = file_path
            
            # Try to load basic file info
            file_size = os.path.getsize(file_path) / 1024  # KB
            filename = Path(file_path).name
            
            # Update display
            self.encrypted_drop_label.configure(text=f"Selected: {filename}")
            
            info_text = f"Encrypted File: {filename}\n"
            info_text += f"Size: {file_size:.1f} KB\n"
            info_text += f"Path: {file_path}\n\n"
            info_text += "Enter the decryption key to decrypt this file."
            
            self.file_info_label.configure(text=info_text)
            
            # Update status
            self.decrypt_status.configure(text="Encrypted file loaded. Enter the decryption key.")
            
            # Enable decrypt button if key is entered
            self.update_decrypt_button_state()
            
            logger.info(f"Encrypted file loaded: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load encrypted file:\n{str(e)}")
            logger.error(f"Failed to load encrypted file {file_path}: {str(e)}")
    
    def paste_key(self):
        """Paste key from clipboard"""
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content:
                self.key_input.delete("1.0", "end")
                self.key_input.insert("1.0", clipboard_content)
                self.update_decrypt_button_state()
                logger.info("Key pasted from clipboard")
            else:
                messagebox.showinfo("Info", "Clipboard is empty.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard:\n{str(e)}")
    
    def update_decrypt_button_state(self):
        """Update decrypt button state"""
        key_text = self.key_input.get("1.0", "end").strip()
        if hasattr(self, 'encrypted_file_path') and key_text:
            self.decrypt_btn.configure(state="normal")
        else:
            self.decrypt_btn.configure(state="disabled")
    
    def decrypt_image(self):
        """Decrypt the selected encrypted image"""
        if not hasattr(self, 'encrypted_file_path'):
            messagebox.showwarning("Warning", "Please select an encrypted file first.")
            return
        
        key_text = self.key_input.get("1.0", "end").strip()
        if not key_text:
            messagebox.showwarning("Warning", "Please enter the decryption key.")
            return
        
        def decryption_task():
            """Background decryption task"""
            try:
                progress_dialog.update_progress(0.1, "Validating decryption key...")
                
                # Convert key string to bytes
                decryption_key = self.key_manager.string_to_key(key_text)
                
                progress_dialog.update_progress(0.3, "Loading encrypted file...")
                
                # Decrypt the package
                image_data, metadata = self.decryptor.decrypt_package(
                    self.encrypted_file_path, decryption_key
                )
                
                progress_dialog.update_progress(0.6, "Reconstructing image...")
                
                # Convert bytes back to image
                image_shape = tuple(metadata['image_shape'])
                decrypted_image = self.image_processor.bytes_to_image(image_data, image_shape)
                
                progress_dialog.update_progress(0.8, "Saving decrypted image...")
                
                # Save decrypted image
                original_name = metadata['original_filename']
                name_parts = Path(original_name).stem, Path(original_name).suffix
                decrypted_filename = f"decrypted_{name_parts[0]}{name_parts[1]}"
                decrypted_path = Config.DECRYPTED_DIR / decrypted_filename
                
                self.image_processor.save_image(decrypted_image, str(decrypted_path))
                
                progress_dialog.update_progress(1.0, "Decryption completed!")
                
                # Show success and preview
                self.root.after(0, lambda: self.show_decryption_success(
                    decrypted_image, decrypted_path, original_name
                ))
                
            except Exception as e:
                logger.error(f"Decryption failed: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Decryption Failed", str(e)))
            finally:
                if not progress_dialog.cancelled:
                    progress_dialog.destroy()
        
        # Show progress dialog
        progress_dialog = ProgressDialog(self.root, "Decrypting Image...")
        
        # Start decryption in background thread
        thread = threading.Thread(target=decryption_task, daemon=True)
        thread.start()
    
    def show_decryption_success(self, decrypted_image, decrypted_path, original_name):
        """Show decryption success and preview"""
        try:
            # Update preview
            thumbnail = self.image_processor.create_thumbnail(decrypted_image, (200, 200))
            if thumbnail:
                self.decrypted_preview_label.configure(image=thumbnail, text="")
                # Keep reference to prevent garbage collection
                self.decrypted_preview_label._image_ref = thumbnail
            
            # Update status
            self.decrypt_status.configure(
                text=f"✅ Decryption successful!\nOriginal: {original_name}\nSaved: {decrypted_path.name}"
            )
            
            # Show success message
            message = f"✅ Image decrypted successfully!\n\n"
            message += f"Original filename: {original_name}\n"
            message += f"Decrypted file: {decrypted_path.name}\n"
            message += f"Location: {decrypted_path.parent}"
            
            messagebox.showinfo("Decryption Successful", message)
            
            logger.info(f"Decryption completed: {decrypted_path}")
            
        except Exception as e:
            logger.error(f"Error showing decryption success: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        try:
            # Bind key input events
            self.key_input.bind('<KeyRelease>', lambda e: self.update_decrypt_button_state())
            
            # Start main loop
            logger.info("Starting GUI main loop")
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"GUI error: {str(e)}")
            raise

if __name__ == "__main__":
    app = ImageEncryptorGUI()
    app.run()
