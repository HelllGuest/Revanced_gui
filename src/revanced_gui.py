"""Main ReVanced GUI application class."""

import os
import logging
import tkinter as tk
from pathlib import Path
from datetime import datetime
from tkinter import messagebox

from src.core.config import ConfigManager
from src.core.java_manager import JavaManager
from src.core.system_monitor import SystemMonitor
from src.core.patcher import APKPatcher
from src.ui.main_window import MainWindow

try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class ReVancedGUI:
    """Main ReVanced GUI application."""
    
    __version__ = "1.3.1"
    __author__ = "ReVanced Community"
    __license__ = "MIT"
    
    def __init__(self, root):
        self.root = root
        
        if not self.check_dependencies():
            root.quit()
            return
        
        # Initialize core variables
        self.cli_jar_path = tk.StringVar()
        self.patches_rvp_path = tk.StringVar()
        self.apk_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.output_filename = tk.StringVar()
        self.java_version = tk.StringVar(value="Checking...")
        self.system_status = tk.StringVar(value="Checking system...")
        
        # Initialize managers
        try:
            script_dir = Path(__file__).parent.parent.resolve()
        except (NameError, AttributeError):
            script_dir = Path.cwd()
        
        self.config_manager = ConfigManager(script_dir)
        self.system_monitor = SystemMonitor()
        self.patcher = APKPatcher(self.log_message)
        
        # Setup logging
        self.setup_logging()
        
        # Initialize UI
        self.main_window = MainWindow(root, self)
        
        # Load configuration
        self.config_manager.load_config(self)
        
        # Start system validation and monitoring
        self.root.after(100, self.validate_system_requirements)
        self.system_monitor.start_system_monitor(
            lambda msg: self.root.after(0, lambda: self.log_message(msg))
        )
    
    def check_dependencies(self):
        """Check for optional dependencies."""
        if not SystemMonitor.is_psutil_available():
            return messagebox.askyesno(
                "Optional Dependencies", 
                "Missing recommended package: psutil\n\n"
                "Install with: pip install psutil\n\n"
                "Continue without advanced features?"
            )
        return True
    
    def setup_logging(self):
        """Configure logging system."""
        handlers = [logging.StreamHandler()]
        
        if self.config_manager.save_logs_enabled:
            log_dir = self.config_manager.script_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"revanced_gui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        
        if self.config_manager.save_logs_enabled:
            logging.info(f"ReVanced GUI v{self.__version__} started - Logs saved")
        else:
            logging.info(f"ReVanced GUI v{self.__version__} started - Console only")
    
    def validate_system_requirements(self):
        """Validate system requirements and update status."""
        self.system_status.set("Checking system requirements...")
        
        java_ok, java_info = JavaManager.validate_java_version_compatibility()
        self.java_version.set(java_info)
        
        if not java_ok:
            self.system_status.set("Java not found or incompatible")
            self.log_message(f"ERROR: Java requirement not met: {java_info}")
            return False
        
        # Check disk space if psutil is available
        if SystemMonitor.is_psutil_available():
            free_gb, total_gb = SystemMonitor.get_disk_usage(self.output_path.get())
            if free_gb > 0:
                status = f"Low disk space: {free_gb}GB free" if free_gb < 2 else "System ready"
                self.system_status.set(status)
                if free_gb < 2:
                    self.log_message(f"WARNING: Low disk space: {free_gb}GB of {total_gb}GB free")
            self.log_message(f"Disk: {free_gb}GB free of {total_gb}GB")
        else:
            self.system_status.set("System ready (limited info)")
        
        self.log_message(f"System check: Java {java_info}")
        return True
    
    def update_preferences(self):
        """Update preferences when checkboxes change."""
        self.config_manager.save_logs_enabled = self.logs_var.get()
        self.config_manager.save_config_enabled = self.config_var.get()
        
        if self.config_manager.save_config_enabled:
            self.config_manager.save_config(self)
        
        logs_status = "ON" if self.config_manager.save_logs_enabled else "OFF"
        config_status = "ON" if self.config_manager.save_config_enabled else "OFF"
        self.log_message(f"Settings updated - Logs: {logs_status}, Config: {config_status}")
    
    def handle_drop(self, event):
        """Handle drag and drop file operations."""
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0]
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.jar':
                    self.cli_jar_path.set(file_path)
                    if self.config_manager.save_config_enabled:
                        self.config_manager.save_config(self)
                elif ext == '.rvp':
                    self.patches_rvp_path.set(file_path)
                    if self.config_manager.save_config_enabled:
                        self.config_manager.save_config(self)
                elif ext == '.apk':
                    self.apk_path.set(file_path)
                self.log_message(f"Dropped file: {os.path.basename(file_path)}")
        except Exception as e:
            self.log_message(f"Drag & drop error: {e}")
    
    def browse_cli_jar(self):
        """Browse for CLI JAR file."""
        filename = filedialog.askopenfilename(
            title="Select ReVanced CLI JAR file",
            filetypes=[("JAR files", "*.jar"), ("All files", "*.*")]
        )
        if filename:
            self.cli_jar_path.set(filename)
            if self.config_manager.save_config_enabled:
                self.config_manager.save_config(self)
    
    def browse_patches(self):
        """Browse for patches RVP file."""
        filename = filedialog.askopenfilename(
            title="Select patches RVP file",
            filetypes=[("RVP files", "*.rvp"), ("All files", "*.*")]
        )
        if filename:
            self.patches_rvp_path.set(filename)
            if self.config_manager.save_config_enabled:
                self.config_manager.save_config(self)
    
    def browse_apk(self):
        """Browse for APK file."""
        filename = filedialog.askopenfilename(
            title="Select APK file to patch",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        if filename:
            self.apk_path.set(filename)
    
    def browse_output(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_path.set(directory)
            if self.config_manager.save_config_enabled:
                self.config_manager.save_config(self)
    
    def update_output_filename(self, *args):
        """Update output filename when APK is selected."""
        apk_path = self.apk_path.get()
        if not apk_path:
            return
            
        # Set output directory to same as APK file directory
        self.output_path.set(os.path.dirname(apk_path))
        
        # Set output filename with -patched suffix
        base_name = os.path.basename(apk_path)
        name, ext = os.path.splitext(base_name)
        self.output_filename.set(f"{name}-patched{ext}")
        
        # Save config to remember the output directory change
        if self.config_manager.save_config_enabled:
            self.config_manager.save_config(self)
    
    def clear_all(self):
        """Reset all file paths, clear log, and reset the interface."""
        self.cli_jar_path.set("")
        self.patches_rvp_path.set("")
        self.apk_path.set("")
        self.output_path.set("")
        self.output_filename.set("")
        
        # Reset progress bar and status
        self.progress_bar.stop()
        self.status_label.config(text="Ready", foreground="green")
        
        # Clear the log
        self.progress_text.delete(1.0, tk.END)
        
        # Save the cleared state if config is enabled
        if self.config_manager.save_config_enabled:
            self.config_manager.save_config(self)
        
        self.log_message("Interface reset - all paths cleared")
    
    def export_log(self):
        """Export the current log to a file."""
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
        """Add a message to the log area."""
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update_idletasks()
        logging.info(message)
    
    def start_progress(self, message="Processing..."):
        """Start the progress bar with a message."""
        self.progress_bar.start(5)
        self.status_label.config(text=message, foreground="blue")
        self.root.update_idletasks()
    
    def stop_progress(self, message="Ready", color="green"):
        """Stop the progress bar with a final message."""
        self.progress_bar.stop()
        self.status_label.config(text=message, foreground=color)
    
    def patch_apk(self):
        """Start the APK patching process."""
        # Validate inputs
        validation_errors = self.patcher.validate_inputs(
            self.cli_jar_path.get(),
            self.patches_rvp_path.get(),
            self.apk_path.get(),
            self.output_path.get()
        )
        
        if validation_errors:
            for error_type, details in validation_errors:
                error_msg = self.patcher.handle_patching_error(error_type, details)
                messagebox.showerror("Patching Error", error_msg)
            return
        
        output_file = os.path.join(self.output_path.get(), self.output_filename.get())
        
        # Start progress
        self.start_progress("Patching APK...")
        
        # Save config before starting
        if self.config_manager.save_config_enabled:
            self.config_manager.save_config(self)
        
        # Define callbacks
        def success_callback():
            self.root.after(0, lambda: self.stop_progress("Success!", "green"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Patching completed successfully!"))
        
        def error_callback(error_type, details):
            error_msg = self.patcher.handle_patching_error(error_type, details)
            self.root.after(0, lambda: self.stop_progress("Failed!", "red"))
            self.root.after(0, lambda: messagebox.showerror("Patching Error", error_msg))
        
        # Start patching
        self.patcher.start_patching(
            self.cli_jar_path.get(),
            self.patches_rvp_path.get(),
            self.apk_path.get(),
            output_file,
            self.java_version.get(),
            success_callback,
            error_callback
        )
    
    def cleanup(self):
        """Cleanup resources when closing."""
        self.system_monitor.stop_monitoring()
        if self.config_manager.save_config_enabled:
            self.config_manager.save_config(self)