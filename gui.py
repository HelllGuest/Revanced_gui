import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import subprocess
import threading
import os
import sys
import webbrowser
import json
from pathlib import Path
import re
import logging
from datetime import datetime
import time

# Version information
__version__ = "1.3.1"
__author__ = "ReVanced Community"
__license__ = "MIT"

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Try to import drag & drop support
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

class ReVancedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ReVanced Patcher")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        self.root.resizable(True, True)
        
        # Check dependencies before initializing
        if not self.check_dependencies():
            root.quit()
            return
            
        # Variables
        self.cli_jar_path = tk.StringVar()
        self.patches_rvp_path = tk.StringVar()
        self.apk_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.output_filename = tk.StringVar()
        self.java_version = tk.StringVar(value="Checking...")
        self.system_status = tk.StringVar(value="Checking system...")
        
        # Configuration options
        self.save_logs_enabled = True  # Default: save logs
        self.save_config_enabled = True  # Default: save configuration
        
        # Get script directory
        try:
            self.script_dir = Path(__file__).parent.resolve()
        except (NameError, AttributeError):
            # Fallback to current working directory if __file__ is not available
            self.script_dir = Path.cwd()
        
        # Configuration file path (in script directory)
        self.config_file = self.script_dir / "revanced_gui_config.json"
        
        # Monitoring
        self.monitoring = False
        
        # Retry mechanism
        self.retry_count = 0
        self.max_retries = 3
        
        self.setup_logging()
        self.create_menu()
        self.setup_ui()
        
        # Bind events for dynamic scaling
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Setup drag & drop if available
        if DND_AVAILABLE:
            self.setup_drag_drop()
        
        # Check system requirements
        self.root.after(100, self.validate_system_requirements)
        
        # Start system monitoring
        self.start_system_monitor()
        
    def check_dependencies(self):
        """Check and handle missing dependencies"""
        missing_deps = []
        
        if not PSUTIL_AVAILABLE:
            missing_deps.append("psutil")
        
        if missing_deps:
            dep_list = ", ".join(missing_deps)
            error_msg = f"Missing recommended packages: {dep_list}\n\nInstall with: pip install {' '.join(missing_deps)}\n\nContinue without advanced features?"
            if not messagebox.askyesno("Optional Dependencies", error_msg):
                return False
        
        return True
        
    def setup_logging(self):
        """Configure logging to file"""
        handlers = [logging.StreamHandler()]  # Always log to console
        
        if self.save_logs_enabled:
            # Create logs directory in script directory
            log_dir = self.script_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"revanced_gui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        
        if self.save_logs_enabled:
            logging.info(f"ReVanced GUI v{__version__} started - Logs saved to: {log_dir}")
        else:
            logging.info(f"ReVanced GUI v{__version__} started - Logging to console only")
        
    def create_menu(self):
        # Create a menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Create File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Log", command=self.clear_log)
        file_menu.add_separator()
        file_menu.add_command(label="Export Log", command=self.export_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        

        

        
        # Create Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="Help Contents", command=self.show_help_dialog)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        

        
    def setup_drag_drop(self):
        """Enable drag and drop for file inputs"""
        if DND_AVAILABLE:
            # Register as drop target
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.handle_drop)
            
            # Make entry widgets accept drops
            for widget in [self.cli_entry, self.patches_entry, self.apk_entry]:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        """Handle dropped files for drag & drop support"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0]
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.jar':
                    self.cli_jar_path.set(file_path)
                elif ext == '.rvp':
                    self.patches_rvp_path.set(file_path)
                elif ext == '.apk':
                    self.apk_path.set(file_path)
                self.log_message(f"Dropped file: {os.path.basename(file_path)}")
        except Exception as e:
            self.log_message(f"Drag & drop error: {e}")


    

            
    def get_disk_usage(self, path=None):
        """Get disk usage for specific path, cross-platform compatible"""
        if not PSUTIL_AVAILABLE:
            return 0, 0
            
        try:
            if path and os.path.exists(path):
                check_path = path
            else:
                check_path = os.getcwd()
            
            # On Windows, ensure we check the drive root
            if os.name == 'nt':
                drive = os.path.splitdrive(check_path)[0]
                if drive:
                    check_path = drive + '\\'
            
            disk = psutil.disk_usage(check_path)
            return disk.free // (1024**3), disk.total // (1024**3)
        except Exception as e:
            self.log_message(f"Warning: Could not check disk usage: {e}")
            return 0, 0


    


    def update_preferences(self):
        """Update preferences when checkboxes change"""
        self.save_logs_enabled = self.logs_var.get()
        self.save_config_enabled = self.config_var.get()
        
        # Save preferences to config if config saving is enabled
        if self.save_config_enabled:
            self.save_config()
        
        self.log_message(f"Settings updated - Logs: {'ON' if self.save_logs_enabled else 'OFF'}, Config: {'ON' if self.save_config_enabled else 'OFF'}")

    def show_settings_info(self):
        """Show settings information dialog"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Settings Information")
        info_window.geometry("500x300")
        info_window.resizable(False, False)
        info_window.transient(self.root)
        info_window.grab_set()

        # Center the window
        info_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - info_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - info_window.winfo_height()) // 2
        info_window.geometry(f"+{x}+{y}")

        # Info content
        info_frame = ttk.Frame(info_window, padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(info_frame, text="Settings Information", font=("Arial", 14, "bold")).pack(pady=(0, 15))

        # Settings explanation
        explanation_text = tk.Text(info_frame, wrap=tk.WORD, font=("Arial", 10), height=12)
        explanation_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        explanation_content = f"""SETTINGS EXPLANATION:

Logs checkbox:
• When ON: Logs are saved to '{self.script_dir / 'logs'}' folder
• When OFF: Logs only appear in the console/terminal
• Default: ON

Config checkbox:
• When ON: Remembers window size, file paths, and settings
• When OFF: Starts fresh each time (no memory of previous session)
• Default: ON

LOCATION: Settings are located in the top-right corner of the main window
for easy access without taking up extra space.

FILE LOCATIONS:
• Script directory: {self.script_dir}
• Configuration file: {self.config_file}
• Logs directory: {self.script_dir / 'logs'}

BENEFITS:
• All files stay with the application (portable)
• No hidden files in system directories
• Easy to backup or move the entire application
• Full user control over file creation
• Compact interface - settings don't clutter the main workspace"""

        explanation_text.insert(tk.END, explanation_content)
        explanation_text.config(state=tk.DISABLED)

        # Close button
        ttk.Button(info_frame, text="Close", command=info_window.destroy).pack()

    def show_documentation(self):
        """Open documentation in browser"""
        webbrowser.open("https://github.com/revanced/revanced-documentation")  
  
    def show_help_dialog(self):
        """Show comprehensive help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("ReVanced GUI Help")
        help_window.geometry("700x550")
        help_window.resizable(True, True)
        
        # Center the window
        help_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - help_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - help_window.winfo_height()) // 2
        help_window.geometry(f"+{x}+{y}")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Requirements tab
        req_frame = ttk.Frame(notebook, padding=10)
        notebook.add(req_frame, text="Requirements")
        
        req_text = tk.Text(req_frame, wrap=tk.WORD, font=("Arial", 10))
        req_text.pack(fill=tk.BOTH, expand=True)
        
        req_content = """
REQUIREMENTS:

• Java 8+ (Java 11+ recommended for best compatibility)
• ReVanced CLI JAR file (download from GitHub releases)
• ReVanced patches RVP file (download from GitHub releases)
• APK file to patch (original app from trusted source)

Ensure all files are from official ReVanced sources to avoid security issues.
"""
        req_text.insert(tk.END, req_content)
        req_text.config(state=tk.DISABLED)
        
        # Usage tab
        usage_frame = ttk.Frame(notebook, padding=10)
        notebook.add(usage_frame, text="Usage")
        
        usage_text = tk.Text(usage_frame, wrap=tk.WORD, font=("Arial", 10))
        usage_text.pack(fill=tk.BOTH, expand=True)
        
        usage_content = """
USAGE INSTRUCTIONS:

1. Select ReVanced CLI JAR file (browse or drag & drop)
2. Select patches RVP file (browse or drag & drop)
3. Choose APK file to patch (browse or drag & drop)
4. Select output directory and verify filename
5. Click 'Patch APK' to start the process
6. Monitor progress in the log area

Use the menu bar to access log export and application settings.
"""
        usage_text.insert(tk.END, usage_content)
        usage_text.config(state=tk.DISABLED)
        
        # Troubleshooting tab
        trouble_frame = ttk.Frame(notebook, padding=10)
        notebook.add(trouble_frame, text="Troubleshooting")
        
        trouble_text = tk.Text(trouble_frame, wrap=tk.WORD, font=("Arial", 10))
        trouble_text.pack(fill=tk.BOTH, expand=True)
        
        trouble_content = """
TROUBLESHOOTING:

COMMON ISSUES:
• Java not found: Install Java and ensure it's in PATH
• File not found: Check file paths and permissions
• Patching failed: Ensure APK version matches patches
• Out of memory: Close other applications or use smaller APK

VALIDATION CHECKS:
• Use 'Validate Setup' to check system readiness
• Check disk space (2GB+ recommended)

For more help, visit: https://github.com/revanced/revanced-documentation
"""
        trouble_text.insert(tk.END, trouble_content)
        trouble_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)
    
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About ReVanced Patcher")
        about_window.geometry("500x350")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Center the about window
        about_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - about_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
        
        # About content
        about_frame = ttk.Frame(about_window, padding="20")
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(about_frame, text="ReVanced Patcher GUI", font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # Version info
        version_frame = ttk.Frame(about_frame)
        version_frame.pack(fill=tk.X, pady=5)
        ttk.Label(version_frame, text="Version:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(version_frame, text=f"v{__version__}", font=("Arial", 10)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Author info
        author_frame = ttk.Frame(about_frame)
        author_frame.pack(fill=tk.X, pady=5)
        ttk.Label(author_frame, text="Author:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(author_frame, text=__author__, font=("Arial", 10)).pack(side=tk.LEFT, padx=(5, 0))
        
        # License info
        license_frame = ttk.Frame(about_frame)
        license_frame.pack(fill=tk.X, pady=5)
        ttk.Label(license_frame, text="License:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(license_frame, text=__license__, font=("Arial", 10)).pack(side=tk.LEFT, padx=(5, 0))
        
        # GitHub link
        github_frame = ttk.Frame(about_frame)
        github_frame.pack(fill=tk.X, pady=5)
        ttk.Label(github_frame, text="GitHub:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        github_link = ttk.Label(github_frame, text="https://github.com/revanced", font=("Arial", 10), foreground="blue", cursor="hand2")
        github_link.pack(side=tk.LEFT, padx=(5, 0))
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/revanced"))
        
        # Description
        desc_text = tk.Text(about_frame, height=10, wrap=tk.WORD, font=("Arial", 9), relief=tk.FLAT)
        desc_text.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        desc_text.insert(tk.END, 
            "This is a GUI wrapper for the ReVanced CLI tool. It provides an easy-to-use interface \n"
            "for patching APK files with ReVanced patches.\n\n"
            "This software is provided under the MIT License, which permits modification and \n"
            "redistribution under certain conditions. See the LICENSE file for details.\n\n"
            "ReVanced is a community-driven project that provides tools for customizing \n"
            "and enhancing Android applications."
        )
        desc_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(about_frame, text="Close", command=about_window.destroy).pack(pady=(15, 0))
        
    def setup_ui(self):
        # Configure grid weights for dynamic scaling
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        
        # Status bar with settings
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        status_frame.columnconfigure(1, weight=1)  # Make middle column expandable
        
        # Left side - System status
        status_left = ttk.Frame(status_frame)
        status_left.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(status_left, text="Status:").pack(side=tk.LEFT)
        ttk.Label(status_left, textvariable=self.system_status, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(status_left, text="Java:").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Label(status_left, textvariable=self.java_version).pack(side=tk.LEFT, padx=(5, 0))
        
        # Right side - Settings
        status_right = ttk.Frame(status_frame)
        status_right.grid(row=0, column=2, sticky=tk.E)
        
        # Create variables for checkboxes
        self.logs_var = tk.BooleanVar(value=self.save_logs_enabled)
        self.config_var = tk.BooleanVar(value=self.save_config_enabled)
        
        # Settings label
        ttk.Label(status_right, text="Settings:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Save logs checkbox (compact)
        logs_check = ttk.Checkbutton(
            status_right, 
            text="Logs", 
            variable=self.logs_var,
            command=self.update_preferences
        )
        logs_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save config checkbox (compact)
        config_check = ttk.Checkbutton(
            status_right, 
            text="Config", 
            variable=self.config_var,
            command=self.update_preferences
        )
        config_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Settings info button (small)
        info_button = ttk.Button(
            status_right, 
            text="?", 
            command=self.show_settings_info,
            width=3
        )
        info_button.pack(side=tk.LEFT)
        
        # CLI JAR file selection
        ttk.Label(main_frame, text="ReVanced CLI JAR:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.cli_entry = ttk.Entry(main_frame, textvariable=self.cli_jar_path)
        self.cli_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        ttk.Button(main_frame, text="Browse", command=self.browse_cli_jar).grid(row=2, column=2, padx=5, pady=8)
        
        # Patches file selection
        ttk.Label(main_frame, text="Patches RVP:").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.patches_entry = ttk.Entry(main_frame, textvariable=self.patches_rvp_path)
        self.patches_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        ttk.Button(main_frame, text="Browse", command=self.browse_patches).grid(row=3, column=2, padx=5, pady=8)
        
        # APK file selection
        ttk.Label(main_frame, text="APK File:").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.apk_entry = ttk.Entry(main_frame, textvariable=self.apk_path)
        self.apk_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        ttk.Button(main_frame, text="Browse", command=self.browse_apk).grid(row=4, column=2, padx=5, pady=8)
        # Bind the APK path change to update output filename
        self.apk_path.trace_add('write', self.update_output_filename)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=5, column=0, sticky=tk.W, pady=8)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path)
        output_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=5, column=2, padx=5, pady=8)
        
        # Output filename
        ttk.Label(main_frame, text="Output Filename:").grid(row=6, column=0, sticky=tk.W, pady=8)
        self.output_filename_entry = ttk.Entry(main_frame, textvariable=self.output_filename)
        self.output_filename_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        
        # Progress area
        ttk.Label(main_frame, text="Progress:").grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=(20, 5), padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.grid(row=7, column=2, sticky=tk.W, pady=(20, 5))
        
        # Progress frame with text and scrollbar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=8)
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)
        
        self.progress_text = tk.Text(progress_frame, height=15, width=70, font=("Consolas", 10))
        self.progress_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for progress text
        scrollbar = ttk.Scrollbar(progress_frame, orient=tk.VERTICAL, command=self.progress_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.progress_text.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Patch APK", command=self.patch_apk).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="Validate Setup", command=self.validate_system_requirements).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=8)
        
        # Configure row weights for proper resizing
        main_frame.rowconfigure(8, weight=1)
        
        # Set initial focus
        self.cli_entry.focus()
        
        # Load saved configuration
        self.load_config()
        

        
    def on_window_resize(self, event):
        # Adjust font sizes based on window dimensions
        width = self.root.winfo_width()
        if width > 800:
            self.progress_text.configure(font=("Consolas", 10))
        else:
            self.progress_text.configure(font=("Consolas", 9))
            
    def parse_java_version(self, version_string):
        """Parse Java version handling both old and new formats"""
        try:
            # Remove quotes and extra whitespace
            version = version_string.strip().strip('"')
            
            # Handle old format (1.8.0_291) vs new format (11.0.1)
            if version.startswith('1.'):
                # Old format: 1.8.0_291 -> 8
                return int(version.split('.')[1])
            else:
                # New format: 11.0.1 -> 11
                return int(version.split('.')[0])
        except (ValueError, IndexError):
            return 0
            
    def check_java_installation(self):
        """Improved Java detection with better parsing"""
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            
            version_output = result.stderr.split('\n')[0] if result.stderr else ""
            version_match = re.search(r'version\s+"([^"]+)"', version_output)
            
            if version_match:
                version_str = version_match.group(1)
                major_version = self.parse_java_version(version_str)
                
                if major_version >= 8:
                    return True, f"{version_str} (Java {major_version})"
                else:
                    return False, f"Unsupported: {version_str} (need Java 8+)"
            
            return False, "Version format not recognized"
            
        except subprocess.TimeoutExpired:
            return False, "Java check timeout"
        except FileNotFoundError:
            return False, "Java not found in PATH"
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def validate_java_version_compatibility(self):
        """Check if Java version is compatible with ReVanced CLI"""
        java_ok, java_info = self.check_java_installation()
        if java_ok:
            version_num = self.parse_java_version(java_info)
            if version_num < 11:  # ReVanced may require Java 11+
                return False, f"Java {version_num} detected. ReVanced CLI may require Java 11+"
        return java_ok, java_info
    
    def validate_system_requirements(self):
        """Comprehensive system check"""
        self.system_status.set("Checking system requirements...")
        
        # Check Java
        java_ok, java_info = self.validate_java_version_compatibility()
        self.java_version.set(java_info)
        
        if not java_ok:
            self.system_status.set("Java not found or incompatible")
            self.log_message(f"ERROR: Java requirement not met: {java_info}")
            return False
        
        # Check disk space
        if PSUTIL_AVAILABLE:
            free_gb, total_gb = self.get_disk_usage(self.output_path.get())
            if free_gb > 0:
                if free_gb < 2:
                    self.system_status.set(f"Low disk space: {free_gb}GB free")
                    self.log_message(f"WARNING: Low disk space: {free_gb}GB of {total_gb}GB free")
                else:
                    self.system_status.set("System ready")
        else:
            self.system_status.set("System ready (limited info)")
        
        self.log_message(f"System check: Java {java_info}")
        if PSUTIL_AVAILABLE:
            free_gb, total_gb = self.get_disk_usage(self.output_path.get())
            self.log_message(f"Disk: {free_gb}GB free of {total_gb}GB")
        return True
    
    def load_config(self):
        """Load configuration with validation"""
        if not self.save_config_enabled:
            logging.info("Configuration loading disabled")
            return
            
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Validate config structure
                if not isinstance(config, dict):
                    raise ValueError("Invalid config format")
                
                # Load preferences
                self.save_logs_enabled = config.get('save_logs_enabled', True)
                self.save_config_enabled = config.get('save_config_enabled', True)
                
                # Update checkbox variables if they exist
                if hasattr(self, 'logs_var'):
                    self.logs_var.set(self.save_logs_enabled)
                if hasattr(self, 'config_var'):
                    self.config_var.set(self.save_config_enabled)
                
                # Safely load values with defaults
                self.cli_jar_path.set(str(config.get('last_cli_path', '')))
                self.patches_rvp_path.set(str(config.get('last_patches_path', '')))
                self.output_path.set(str(config.get('last_output_dir', '')))
                
                # Validate geometry string
                geometry = config.get('window_geometry', '')
                if geometry and re.match(r'\d+x\d+\+\d+\+\d+', geometry):
                    self.root.geometry(geometry)
                
                logging.info("Configuration loaded successfully")
                
        except (json.JSONDecodeError, ValueError, OSError) as e:
            logging.warning(f"Config load error (using defaults): {e}")
        except Exception as e:
            logging.error(f"Unexpected config error: {e}")
    
    def save_config(self):
        """Save configuration with error handling"""
        if not self.save_config_enabled:
            return  # Don't save if disabled
            
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(exist_ok=True)
            
            config = {
                'save_logs_enabled': self.save_logs_enabled,
                'save_config_enabled': self.save_config_enabled,
                'last_cli_path': self.cli_jar_path.get(),
                'last_patches_path': self.patches_rvp_path.get(),
                'last_output_dir': self.output_path.get(),
                'window_geometry': self.root.geometry(),
                'version': __version__,
            }
            
            # Write atomically
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Atomic move
            temp_file.replace(self.config_file)
            
        except Exception as e:
            logging.error(f"Failed to save config: {e}")



    def start_progress(self, message="Processing..."):
        """Start progress bar with status message"""
        self.progress_bar.start(10)
        self.status_label.config(text=message, foreground="blue")
        
    def stop_progress(self, message="Ready", color="green"):
        """Stop progress bar with final status"""
        self.progress_bar.stop()
        self.status_label.config(text=message, foreground=color)
        
    def start_system_monitor(self):
        """Start background system monitoring"""
        def monitor():
            while getattr(self, 'monitoring', False):
                if PSUTIL_AVAILABLE:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    if cpu_percent > 80:
                        self.root.after(0, lambda: self.log_message(f"High CPU usage: {cpu_percent}%"))
                time.sleep(5)
        
        self.monitoring = True
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        



            

            

            

            

        
    def browse_cli_jar(self):
        filename = filedialog.askopenfilename(
            title="Select ReVanced CLI JAR file",
            filetypes=[("JAR files", "*.jar"), ("All files", "*.*")]
        )
        if filename:
            self.cli_jar_path.set(filename)
            if self.save_config_enabled:
                self.save_config()
    
    def browse_patches(self):
        filename = filedialog.askopenfilename(
            title="Select patches RVP file",
            filetypes=[("RVP files", "*.rvp"), ("All files", "*.*")]
        )
        if filename:
            self.patches_rvp_path.set(filename)
            if self.save_config_enabled:
                self.save_config()
    
    def browse_apk(self):
        filename = filedialog.askopenfilename(
            title="Select APK file to patch",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if filename:
            self.apk_path.set(filename)
            if self.save_config_enabled:
                self.save_config()
    
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_path.set(directory)
            if self.save_config_enabled:
                self.save_config()
    
    def update_output_filename(self, *args):
        # Automatically set output filename with "-patched" suffix
        apk_path = self.apk_path.get()
        if apk_path:
            base_name = os.path.basename(apk_path)
            name, ext = os.path.splitext(base_name)
            self.output_filename.set(f"{name}-patched{ext}")
    
    def clear_log(self):
        self.progress_text.delete(1.0, tk.END)
    
    def export_log(self):
        """Export the current log to a file"""
        filename = filedialog.asksaveasfilename(
            title="Export Log File",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.progress_text.get(1.0, tk.END))
                self.log_message(f"Log exported to: {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export log: {str(e)}")
    
    def log_message(self, message):
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update_idletasks()
        logging.info(message)
    
    def validate_inputs(self):
        """Validate all input fields before patching"""
        errors = []
        
        # Check Java
        java_ok, java_info = self.validate_java_version_compatibility()
        if not java_ok:
            errors.append(('java_not_found', java_info))
        
        # Check files exist
        if not self.cli_jar_path.get() or not os.path.exists(self.cli_jar_path.get()):
            errors.append(('file_not_found', "ReVanced CLI JAR file not found"))
        
        if not self.patches_rvp_path.get() or not os.path.exists(self.patches_rvp_path.get()):
            errors.append(('file_not_found', "Patches RVP file not found"))
        
        if not self.apk_path.get() or not os.path.exists(self.apk_path.get()):
            errors.append(('file_not_found', "APK file not found"))
        
        if not self.output_path.get() or not os.path.exists(self.output_path.get()):
            errors.append(('file_not_found', "Output directory not found"))
        
        # Check disk space
        if PSUTIL_AVAILABLE:
            free_gb, total_gb = self.get_disk_usage(self.output_path.get())
            if free_gb > 0:
                apk_size = os.path.getsize(self.apk_path.get()) if self.apk_path.get() and os.path.exists(self.apk_path.get()) else 0
                needed_gb = (apk_size * 3) // (1024**3)  # Approximate space needed (3x APK size)
                
                if free_gb < needed_gb:
                    errors.append(('insufficient_memory', f"Need {needed_gb}GB, only {free_gb}GB free"))
        
        return errors

    def handle_patching_error(self, error_type, details):
        """Provide specific recovery suggestions"""
        error_solutions = {
            'java_not_found': "Install Java 8+ and ensure it's in your PATH",
            'file_not_found': "Check that all required files exist and are accessible",
            'corrupted_apk': "Use a different APK file or re-download the original",
            'patch_mismatch': "Ensure APK version matches the patches version",
            'insufficient_memory': "Free up disk space or use a smaller APK",
            'unknown': "Check the log for detailed error information"
        }
        
        solution = error_solutions.get(error_type, "Check the documentation for troubleshooting steps")
        error_msg = f"Error: {details}\nSolution: {solution}"
        
        self.log_message(error_msg)
        messagebox.showerror("Patching Error", error_msg)
    
    def patch_apk(self):
        # Validate inputs
        validation_errors = self.validate_inputs()
        if validation_errors:
            for error_type, details in validation_errors:
                self.handle_patching_error(error_type, details)
            return
        
        # Build command
        output_file = os.path.join(self.output_path.get(), self.output_filename.get())
        cmd = [
            "java", "-jar", 
            self.cli_jar_path.get(), 
            "patch",
            "-p", self.patches_rvp_path.get(),
            "-o", output_file,
            self.apk_path.get()
        ]
        
        self.log_message("=" * 60)
        self.log_message("Starting ReVanced Patching Process")
        self.log_message("=" * 60)
        self.log_message(f"Input APK: {self.apk_path.get()}")
        self.log_message(f"Output file: {output_file}")
        self.log_message(f"Java version: {self.java_version.get()}")
        self.log_message("Using all available patches")
        self.log_message(f"Command: {' '.join(cmd)}")
        self.log_message("-" * 60)
        
        # Start progress indicator
        self.start_progress("Patching APK...")
        self.start_time = time.time()
        
        # Save config before starting (if enabled)
        if self.save_config_enabled:
            self.save_config()
        
        # Run in separate thread to avoid freezing GUI
        thread = threading.Thread(target=self.run_patching, args=(cmd, output_file))
        thread.daemon = True
        thread.start()
    
    def run_patching(self, cmd, output_file):
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Read output in real-time
            for line in process.stdout:
                self.root.after(0, self.log_message, line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                elapsed = time.time() - self.start_time
                self.root.after(0, lambda: self.log_message("-" * 60))
                self.root.after(0, lambda: self.log_message(f"Patching completed successfully in {elapsed:.1f}s!"))
                self.root.after(0, lambda: self.log_message(f"Patched APK saved as: {output_file}"))
                self.root.after(0, lambda: self.stop_progress("Success!", "green"))
                self.root.after(0, lambda: messagebox.showinfo("Success", "Patching completed successfully!"))
            else:
                error_msg = f"Patching failed with return code {process.returncode}"
                self.root.after(0, lambda: self.log_message("-" * 60))
                self.root.after(0, lambda: self.log_message(error_msg))
                self.root.after(0, lambda: self.stop_progress("Failed!", "red"))
                self.root.after(0, lambda: self.handle_patching_error('patch_mismatch', error_msg))
                
        except FileNotFoundError:
            error_msg = "Java not found. Please make sure Java is installed and available in your PATH."
            self.root.after(0, lambda: self.log_message("-" * 60))
            self.root.after(0, lambda: self.log_message(error_msg))
            self.root.after(0, lambda: self.stop_progress("Failed!", "red"))
            self.root.after(0, lambda: self.handle_patching_error('java_not_found', error_msg))
        except Exception as e:
            error_msg = f"Exception occurred: {str(e)}"
            self.root.after(0, lambda: self.log_message("-" * 60))
            self.root.after(0, lambda: self.log_message(error_msg))
            self.root.after(0, lambda: self.stop_progress("Failed!", "red"))
            self.root.after(0, lambda: self.handle_patching_error('unknown', error_msg))
        finally:
            self.root.after(0, lambda: self.log_message("=" * 60))

def main():
    # Create root window with drag & drop support if available
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        
    app = ReVancedGUI(root)
    
    if app:  # Only proceed if initialization was successful
        # Handle application close
        def on_closing():
            app.monitoring = False
            if app.save_config_enabled:
                app.save_config()
            root.quit()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

if __name__ == "__main__":
    main()