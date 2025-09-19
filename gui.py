import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import sys
import platform
import webbrowser
import json
from pathlib import Path
import re
import logging
from datetime import datetime
import zipfile
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
        self.root.geometry("850x650")
        self.root.minsize(750, 550)
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
        
        # Configuration
        self.config_file = Path.home() / ".revanced_gui_config.json"
        self.recent_files_file = Path.home() / ".revanced_gui_recent.json"
        self.profiles_file = Path.home() / ".revanced_gui_profiles.json"
        
        # Monitoring
        self.monitoring = False
        
        # Retry mechanism
        self.retry_count = 0
        self.max_retries = 3
        
        self.setup_logging()
        
        # Create menu bar
        self.create_menu()
        
        # Configure style for better scaling
        self.setup_ui()
        
        # Bind events for dynamic scaling
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
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
        log_dir = Path.home() / ".revanced_gui_logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"revanced_gui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        logging.info(f"ReVanced GUI v{__version__} started")
        
    def create_menu(self):
        # Create a menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Create File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Log", command=self.clear_log, accelerator="Ctrl+L")
        file_menu.add_separator()
        
        # Recent Files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        
        # Profiles submenu
        self.profiles_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Profiles", menu=self.profiles_menu)
        self.profiles_menu.add_command(label="Save Current Profile", command=self.save_current_profile)
        self.profiles_menu.add_separator()
        
        file_menu.add_separator()
        file_menu.add_command(label="Export Log", command=self.export_log, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Create View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="System Info", command=self.show_system_info, accelerator="F1")
        view_menu.add_command(label="Analyze APK", command=self.analyze_apk)
        view_menu.add_command(label="Analyze Patches", command=self.analyze_patches_file)
        
        # Create Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="Help Contents", command=self.show_help_dialog)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        
        # Load recent files and profiles
        self.load_recent_files()
        self.load_profiles()
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind('<Control-o>', lambda e: self.browse_apk())
        self.root.bind('<Control-p>', lambda e: self.patch_apk())
        self.root.bind('<Control-l>', lambda e: self.clear_log())
        self.root.bind('<Control-s>', lambda e: self.export_log())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<F1>', lambda e: self.show_system_info())
        self.root.bind('<F5>', lambda e: self.validate_system_requirements())
        
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
        """Handle dropped files"""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0]
                ext = os.path.splitext(file_path)[1].lower()
                
                if ext == '.jar':
                    self.cli_jar_path.set(file_path)
                    self.add_to_recent_files('cli', file_path)
                elif ext == '.rvp':
                    self.patches_rvp_path.set(file_path)
                    self.add_to_recent_files('patches', file_path)
                elif ext == '.apk':
                    self.apk_path.set(file_path)
                    self.add_to_recent_files('apk', file_path)
                    
                self.log_message(f"Dropped file: {os.path.basename(file_path)}")
        except Exception as e:
            self.log_message(f"Drag & drop error: {e}")
    
    def show_system_info(self):
        """Display system information dialog"""
        info_window = tk.Toplevel(self.root)
        info_window.title("System Information")
        info_window.geometry("550x450")
        info_window.resizable(False, False)
        info_window.transient(self.root)
        info_window.grab_set()
        
        # Center the window
        info_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - info_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - info_window.winfo_height()) // 2
        info_window.geometry(f"+{x}+{y}")
        
        # System info content
        info_frame = ttk.Frame(info_window, padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(info_frame, text="System Information", font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # System details
        details = self.get_system_details()
        
        text_widget = tk.Text(info_frame, wrap=tk.WORD, font=("Consolas", 10), height=18)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=5)
        
        for key, value in details.items():
            text_widget.insert(tk.END, f"{key:<25}: {value}\n")
        
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(info_frame, text="Close", command=info_window.destroy).pack(pady=(15, 0))
    
    def get_system_details(self):
        """Get detailed system information"""
        details = {
            "Application Version": __version__,
            "Python Version": sys.version.split()[0],
            "Platform": platform.platform(),
            "Processor": platform.processor() or "Unknown",
            "Java Version": self.java_version.get(),
        }
        
        if PSUTIL_AVAILABLE:
            details["RAM Available"] = f"{psutil.virtual_memory().available // (1024**3)} GB"
            details["Disk Space"] = self.get_disk_space()
            details["CPU Cores"] = psutil.cpu_count(logical=False)
            details["Logical CPUs"] = psutil.cpu_count(logical=True)
        else:
            details["System Info"] = "psutil not available"
            
        details["Drag & Drop"] = "Available" if DND_AVAILABLE else "Not available"
            
        return details
    
    def get_disk_space(self):
        """Get available disk space"""
        if not PSUTIL_AVAILABLE:
            return "psutil not available"
            
        try:
            free_gb, total_gb = self.get_disk_usage()
            return f"{free_gb} GB free of {total_gb} GB"
        except:
            return "Unknown"
            
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

KEYBOARD SHORTCUTS:
• Ctrl+O - Open APK file
• Ctrl+P - Start patching
• Ctrl+L - Clear log
• Ctrl+S - Export log
• F1 - System Information
• F5 - Validate system
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
• Analyze APK files before patching
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
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        ttk.Label(status_frame, textvariable=self.system_status, foreground="blue").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(status_frame, text="Java:").pack(side=tk.LEFT, padx=(20, 0))
        ttk.Label(status_frame, textvariable=self.java_version).pack(side=tk.LEFT, padx=(5, 0))
        
        # Title
        title_label = ttk.Label(main_frame, text="ReVanced Patcher", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # CLI JAR file selection
        ttk.Label(main_frame, text="ReVanced CLI JAR:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.cli_entry = ttk.Entry(main_frame, textvariable=self.cli_jar_path)
        self.cli_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        ttk.Button(main_frame, text="Browse", command=self.browse_cli_jar).grid(row=2, column=2, padx=5, pady=8)
        self.create_tooltip(self.cli_entry, "Select the ReVanced CLI JAR file")
        
        # Patches file selection
        ttk.Label(main_frame, text="Patches RVP:").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.patches_entry = ttk.Entry(main_frame, textvariable=self.patches_rvp_path)
        self.patches_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        ttk.Button(main_frame, text="Browse", command=self.browse_patches).grid(row=3, column=2, padx=5, pady=8)
        self.create_tooltip(self.patches_entry, "Select the ReVanced patches RVP file")
        
        # APK file selection
        ttk.Label(main_frame, text="APK File:").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.apk_entry = ttk.Entry(main_frame, textvariable=self.apk_path)
        self.apk_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        ttk.Button(main_frame, text="Browse", command=self.browse_apk).grid(row=4, column=2, padx=5, pady=8)
        self.create_tooltip(self.apk_entry, "Select the APK file to patch")
        # Bind the APK path change to update output filename
        self.apk_path.trace_add('write', self.update_output_filename)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=5, column=0, sticky=tk.W, pady=8)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_path)
        output_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=5, column=2, padx=5, pady=8)
        self.create_tooltip(output_entry, "Select where to save the patched APK")
        
        # Output filename
        ttk.Label(main_frame, text="Output Filename:").grid(row=6, column=0, sticky=tk.W, pady=8)
        self.output_filename_entry = ttk.Entry(main_frame, textvariable=self.output_filename)
        self.output_filename_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), padx=5, pady=8)
        self.create_tooltip(self.output_filename_entry, "Automatically generated with '-patched' suffix")
        
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
        
    def create_tooltip(self, widget, text):
        """Simple tooltip implementation"""
        def on_enter(event):
            # Only show tooltip if there's enough text to warrant it
            if len(text) > 20:
                x, y = widget.winfo_rootx() + 20, widget.winfo_rooty() + 20
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{x}+{y}")
                label = tk.Label(tooltip, text=text, background="lightyellow", 
                                relief="solid", borderwidth=1, font=("Arial", 9), justify=tk.LEFT)
                label.pack()
                widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
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
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Validate config structure
                if not isinstance(config, dict):
                    raise ValueError("Invalid config format")
                
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
            # Continue with empty defaults
        except Exception as e:
            logging.error(f"Unexpected config error: {e}")
    
    def save_config(self):
        """Save configuration with error handling"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(exist_ok=True)
            
            config = {
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
            
            temp_file.replace(self.config_file)
            logging.info("Configuration saved")
            
        except (OSError, json.JSONEncodeError) as e:
            logging.error(f"Failed to save config: {e}")
            
    def load_recent_files(self):
        """Load recent files from disk"""
        try:
            if self.recent_files_file.exists():
                with open(self.recent_files_file, 'r') as f:
                    self.recent_files = json.load(f)
                self.update_recent_menu()
        except:
            self.recent_files = {'cli': [], 'patches': [], 'apk': []}
            
    def save_recent_files(self):
        """Save recent files to disk"""
        try:
            with open(self.recent_files_file, 'w') as f:
                json.dump(self.recent_files, f, indent=2)
        except:
            pass
            
    def load_profiles(self):
        """Load saved profiles"""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r') as f:
                    self.profiles = json.load(f)
                self.update_profiles_menu()
        except:
            self.profiles = {}
            
    def save_profiles(self):
        """Save profiles to disk"""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except:
            pass
            
    def update_recent_menu(self):
        """Update recent files menu"""
        self.recent_menu.delete(0, tk.END)
        
        if hasattr(self, 'recent_files'):
            for file_type, files in self.recent_files.items():
                if files:
                    try:
                        menu_index = self.recent_menu.index(tk.END)
                        if menu_index is not None and menu_index > 0:
                            self.recent_menu.add_separator()
                    except tk.TclError:
                        pass  # Menu is empty, continue
                    
                    self.recent_menu.add_command(label=f"{file_type.upper()} Files", state=tk.DISABLED)
                    
                    for file_path in files:
                        if os.path.exists(file_path):
                            filename = os.path.basename(file_path)
                            self.recent_menu.add_command(
                                label=f"  {filename}", 
                                command=lambda p=file_path, t=file_type: self.load_recent_file(t, p)
                            )
        
        try:
            menu_index = self.recent_menu.index(tk.END)
            if menu_index is None or menu_index == 0:
                self.recent_menu.add_command(label="No recent files", state=tk.DISABLED)
        except tk.TclError:
            self.recent_menu.add_command(label="No recent files", state=tk.DISABLED)
            
    def update_profiles_menu(self):
        """Update profiles menu"""
        self.profiles_menu.delete(2, tk.END)  # Clear existing profiles
        
        if hasattr(self, 'profiles'):
            for profile_name in self.profiles.keys():
                self.profiles_menu.add_command(
                    label=profile_name,
                    command=lambda n=profile_name: self.load_profile(n)
                )
        
        if len(self.profiles) == 0:
            self.profiles_menu.add_command(label="No saved profiles", state=tk.DISABLED)
            
    def add_to_recent_files(self, file_type, file_path):
        """Add file to recent files list"""
        if not hasattr(self, 'recent_files'):
            self.recent_files = {'cli': [], 'patches': [], 'apk': []}
        
        # Remove if already exists and add to front
        if file_path in self.recent_files.get(file_type, []):
            self.recent_files[file_type].remove(file_path)
        
        self.recent_files[file_type].insert(0, file_path)
        
        # Keep only 5 recent files per type
        self.recent_files[file_type] = self.recent_files[file_type][:5]
        
        self.update_recent_menu()
        self.save_recent_files()
        
    def load_recent_file(self, file_type, file_path):
        """Load a recent file"""
        if os.path.exists(file_path):
            if file_type == 'cli':
                self.cli_jar_path.set(file_path)
            elif file_type == 'patches':
                self.patches_rvp_path.set(file_path)
            elif file_type == 'apk':
                self.apk_path.set(file_path)
        else:
            messagebox.showerror("File Not Found", f"File no longer exists:\n{file_path}")
            # Remove from recent files
            if file_path in self.recent_files.get(file_type, []):
                self.recent_files[file_type].remove(file_path)
                self.update_recent_menu()
                self.save_recent_files()
                
    def save_current_profile(self):
        """Save current settings as a profile"""
        profile_name = simpledialog.askstring("Save Profile", "Enter profile name:")
        if profile_name:
            profile = {
                'cli_path': self.cli_jar_path.get(),
                'patches_path': self.patches_rvp_path.get(),
                'output_dir': self.output_path.get()
            }
            
            if not hasattr(self, 'profiles'):
                self.profaces = {}
            
            self.profiles[profile_name] = profile
            self.save_profiles()
            self.update_profiles_menu()
            self.log_message(f"Profile '{profile_name}' saved")
            
    def load_profile(self, profile_name):
        """Load a saved profile"""
        if profile_name in self.profiles:
            profile = self.profiles[profile_name]
            self.cli_jar_path.set(profile.get('cli_path', ''))
            self.patches_rvp_path.set(profile.get('patches_path', ''))
            self.output_path.set(profile.get('output_dir', ''))
            self.log_message(f"Profile '{profile_name}' loaded")
    
    def handle_patching_error(self, error_type, details):
        """Provide specific recovery suggestions"""
        error_solutions = {
            'java_not_found': "Install Java JRE 8+ and add to PATH",
            'insufficient_memory': "Close other applications or increase Java heap size with -Xmx option",
            'corrupted_apk': "Try a different APK file or redownload it",
            'patch_mismatch': "Ensure patches are compatible with APK version",
            'file_not_found': "Check that all file paths are correct and files exist",
            'permission_denied': "Check file permissions and try running as administrator if needed"
        }
        
        solution = error_solutions.get(error_type, "Check the log for details and try again")
        error_msg = f"Error: {details}\nSolution: {solution}"
        
        self.log_message(error_msg)
        messagebox.showerror("Patching Error", error_msg)
        
        # Generate error report
        report_file = self.generate_error_report(details)
        self.log_message(f"Error report saved: {report_file}")
        
    def generate_error_report(self, error_details):
        """Generate detailed error report for troubleshooting"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'version': __version__,
            'system': {
                'platform': platform.platform(),
                'python': sys.version,
                'java': self.java_version.get()
            },
            'files': {
                'cli_jar': os.path.basename(self.cli_jar_path.get()) if self.cli_jar_path.get() else None,
                'patches': os.path.basename(self.patches_rvp_path.get()) if self.patches_rvp_path.get() else None,
                'apk': os.path.basename(self.apk_path.get()) if self.apk_path.get() else None
            },
            'error': error_details
        }
        
        report_file = Path.home() / f".revanced_gui_error_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log_message(f"Error report saved: {report_file}")
        return report_file
        
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
        
    def validate_apk_file(self, apk_path):
        """Validate APK file integrity"""
        try:
            # Check if it's a valid ZIP (APK is a ZIP file)
            with zipfile.ZipFile(apk_path, 'r') as apk:
                # Check for essential APK components
                files = apk.namelist()
                required_files = ['AndroidManifest.xml', 'classes.dex']
                
                missing = [f for f in required_files if f not in files]
                if missing:
                    return False, f"Invalid APK: missing {', '.join(missing)}"
                
            # Check file size (reasonable limits)
            size_mb = os.path.getsize(apk_path) / (1024 * 1024)
            if size_mb > 500:  # > 500MB seems unusual
                self.log_message(f"Warning: Large APK file ({size_mb:.1f} MB)")
            
            return True, "Valid APK file"
            
        except zipfile.BadZipFile:
            return False, "Corrupted APK file"
        except Exception as e:
            return False, f"APK validation error: {str(e)}"

    def validate_jar_file(self, jar_path):
        """Validate JAR file integrity"""
        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                # Check for manifest
                if 'META-INF/MANIFEST.MF' not in jar.namelist():
                    return False, "Invalid JAR: missing manifest"
            return True, "Valid JAR file"
        except zipfile.BadZipFile:
            return False, "Corrupted JAR file"
        except Exception as e:
            return False, f"JAR validation error: {str(e)}"
            
    def analyze_apk(self):
        """Analyze APK and show detailed information"""
        apk_path = self.apk_path.get()
        if not apk_path or not os.path.exists(apk_path):
            messagebox.showwarning("No APK", "Please select an APK file first")
            return
        
        try:
            # Use lazy loading for large files
            file_size = os.path.getsize(apk_path)
            if file_size > 100 * 1024 * 1024:  # > 100MB
                info = self.quick_apk_analysis(apk_path)
            else:
                info = self.full_apk_analysis(apk_path)
                
            # Show analysis dialog
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("APK Analysis")
            analysis_window.geometry("450x350")
            
            text_widget = tk.Text(analysis_window, wrap=tk.WORD, font=("Consolas", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for key, value in info.items():
                text_widget.insert(tk.END, f"{key:<25}: {value}\n")
            
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze APK: {str(e)}")
            
    def quick_apk_analysis(self, apk_path):
        """Quick analysis for large APK files"""
        size_mb = os.path.getsize(apk_path) / (1024 * 1024)
        return {
            'Filename': os.path.basename(apk_path),
            'Size': f"{size_mb:.1f} MB",
            'Analysis': 'Quick analysis (large file)',
            'Recommendation': 'Proceed with patching if file is valid'
        }
            
    def full_apk_analysis(self, apk_path):
        """Full analysis for APK files"""
        with zipfile.ZipFile(apk_path, 'r') as apk:
            files = apk.namelist()
            size_mb = os.path.getsize(apk_path) / (1024 * 1024)
            
            # Count different file types
            dex_files = [f for f in files if f.endswith('.dex')]
            lib_files = [f for f in files if f.startswith('lib/')]
            res_files = [f for f in files if f.startswith('res/')]
            
            return {
                'Filename': os.path.basename(apk_path),
                'Size': f"{size_mb:.1f} MB",
                'Total Files': len(files),
                'DEX Files': len(dex_files),
                'Native Libraries': len(lib_files),
                'Resource Files': len(res_files),
                'Has Manifest': 'Yes' if 'AndroidManifest.xml' in files else 'No',
                'Has Resources': 'Yes' if len(res_files) > 0 else 'No',
                'Has Native Code': 'Yes' if len(lib_files) > 0 else 'No'
            }
            
    def analyze_patches_file(self):
        """Analyze patches file"""
        patches_path = self.patches_rvp_path.get()
        if not patches_path or not os.path.exists(patches_path):
            messagebox.showwarning("No Patches", "Please select a patches file first")
            return
            
        try:
            # Try to read the patches file
            with open(patches_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # Read first 1000 chars
                
            # Simple analysis - count lines and look for patch names
            lines = content.split('\n')
            patch_count = sum(1 for line in lines if 'patch' in line.lower() and 'name' in line.lower())
            
            info = {
                'Filename': os.path.basename(patches_path),
                'Size': f"{os.path.getsize(patches_path) / 1024:.1f} KB",
                'Estimated Patches': patch_count,
                'Format': 'RVP (ReVanced Patches)'
            }
            
            # Show analysis dialog
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("Patches Analysis")
            analysis_window.geometry("450x200")
            
            text_widget = tk.Text(analysis_window, wrap=tk.WORD, font=("Consolas", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for key, value in info.items():
                text_widget.insert(tk.END, f"{key:<25}: {value}\n")
            
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze patches: {str(e)}")
        
    def browse_cli_jar(self):
        filename = filedialog.askopenfilename(
            title="Select ReVanced CLI JAR file",
            filetypes=[("JAR files", "*.jar"), ("All files", "*.*")]
        )
        if filename:
            self.cli_jar_path.set(filename)
            self.add_to_recent_files('cli', filename)
            self.save_config()
    
    def browse_patches(self):
        filename = filedialog.askopenfilename(
            title="Select patches RVP file",
            filetypes=[("RVP files", "*.rvp"), ("All files", "*.*")]
        )
        if filename:
            self.patches_rvp_path.set(filename)
            self.add_to_recent_files('patches', filename)
            self.save_config()
    
    def browse_apk(self):
        filename = filedialog.askopenfilename(
            title="Select APK file to patch",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if filename:
            self.apk_path.set(filename)
            self.add_to_recent_files('apk', filename)
            self.save_config()
    
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_path.set(directory)
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
        else:
            # Validate JAR file
            jar_ok, jar_msg = self.validate_jar_file(self.cli_jar_path.get())
            if not jar_ok:
                errors.append(('corrupted_apk', f"CLI JAR: {jar_msg}"))
        
        if not self.patches_rvp_path.get() or not os.path.exists(self.patches_rvp_path.get()):
            errors.append(('file_not_found', "Patches RVP file not found"))
        
        if not self.apk_path.get() or not os.path.exists(self.apk_path.get()):
            errors.append(('file_not_found', "APK file not found"))
        else:
            # Validate APK file
            apk_ok, apk_msg = self.validate_apk_file(self.apk_path.get())
            if not apk_ok:
                errors.append(('corrupted_apk', f"APK: {apk_msg}"))
        
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
        
        # Save config before starting
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
                
                # Auto-retry logic
                if self.retry_count < self.max_retries:
                    self.retry_count += 1
                    self.root.after(0, lambda: self.log_message(f"Auto-retry {self.retry_count}/{self.max_retries} in 3 seconds..."))
                    self.root.after(3000, lambda: self.auto_retry_on_failure(cmd, output_file))
                else:
                    self.root.after(0, lambda: self.handle_patching_error('patch_mismatch', error_msg))
                    self.retry_count = 0
                
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
            
    def auto_retry_on_failure(self, cmd, output_file):
        """Automatically retry failed operations"""
        self.log_message(f"Retrying... (attempt {self.retry_count}/{self.max_retries})")
        
        # Modify command for retry (add memory flags, etc.)
        modified_cmd = self.modify_command_for_retry(cmd)
        
        self.start_progress(f"Retrying {self.retry_count}/{self.max_retries}...")
        
        thread = threading.Thread(target=self.run_patching, args=(modified_cmd, output_file))
        thread.daemon = True
        thread.start()
        
    def modify_command_for_retry(self, cmd):
        """Modify command parameters for retry attempts"""
        # Add memory parameters for retry
        modified = cmd.copy()
        # Insert memory option after 'java'
        if len(modified) > 1 and modified[0] == 'java':
            modified.insert(1, '-Xmx2G')  # Add more memory
        return modified

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
            app.save_config()
            root.quit()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()

if __name__ == "__main__":
    main()