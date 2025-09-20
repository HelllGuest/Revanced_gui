"""Dialog windows for help and about information."""

import tkinter as tk
from tkinter import ttk


class HelpDialog:
    """Help dialog with usage instructions."""
    
    @staticmethod
    def show(parent):
        """Show help dialog with usage instructions."""
        help_window = tk.Toplevel(parent)
        help_window.title("ReVanced GUI Help")
        help_window.geometry("600x500")
        help_window.resizable(True, True)
        help_window.transient(parent)
        help_window.grab_set()
        
        # Center the window
        help_window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - help_window.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - help_window.winfo_height()) // 2
        help_window.geometry(f"+{x}+{y}")
        
        # Help content
        help_frame = ttk.Frame(help_window, padding="20")
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(help_frame, text="ReVanced GUI Help", font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(help_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Usage tab
        HelpDialog._create_usage_tab(notebook)
        
        # Requirements tab
        HelpDialog._create_requirements_tab(notebook)
        
        # Troubleshooting tab
        HelpDialog._create_troubleshooting_tab(notebook)
        
        # Close button
        ttk.Button(help_frame, text="Close", command=help_window.destroy).pack()
    
    @staticmethod
    def _create_usage_tab(notebook):
        """Create the usage instructions tab."""
        usage_frame = ttk.Frame(notebook, padding=10)
        notebook.add(usage_frame, text="Usage")
        
        usage_text = tk.Text(usage_frame, wrap=tk.WORD, font=("Arial", 10))
        usage_text.pack(fill=tk.BOTH, expand=True)
        
        usage_content = """USAGE INSTRUCTIONS:

1. Select ReVanced CLI JAR file (browse or drag & drop)
2. Select patches RVP file (browse or drag & drop)
3. Choose APK file to patch (browse or drag & drop)
4. Output directory automatically set to APK's location
5. Click 'Patch APK' to start the process
6. Monitor progress in the log area

BUTTONS:
• Patch APK: Start the patching process
• Reset: Clear all file paths and log, start fresh
• Exit: Close the application

AUTOMATIC FEATURES:
• JAR and RVP paths are remembered between sessions
• Output directory automatically matches APK file location
• Output filename gets '-patched' suffix automatically

SETTINGS:
• Logs: Enable/disable saving logs to file
• Config: Enable/disable saving configuration between sessions

The application automatically validates your system and files before patching.
"""
        usage_text.insert(tk.END, usage_content)
        usage_text.config(state=tk.DISABLED)
    
    @staticmethod
    def _create_requirements_tab(notebook):
        """Create the requirements tab."""
        req_frame = ttk.Frame(notebook, padding=10)
        notebook.add(req_frame, text="Requirements")
        
        req_text = tk.Text(req_frame, wrap=tk.WORD, font=("Arial", 10))
        req_text.pack(fill=tk.BOTH, expand=True)
        
        req_content = """REQUIREMENTS:

• Java 8+ (Java 11+ recommended for best compatibility)
• ReVanced CLI JAR file (download from GitHub releases)
• ReVanced patches RVP file (download from GitHub releases)
• APK file to patch (original app from trusted source)

OPTIONAL:
• psutil package for advanced system monitoring
• tkinterdnd2 package for drag & drop support

Ensure all files are from official ReVanced sources to avoid security issues.
"""
        req_text.insert(tk.END, req_content)
        req_text.config(state=tk.DISABLED)
    
    @staticmethod
    def _create_troubleshooting_tab(notebook):
        """Create the troubleshooting tab."""
        trouble_frame = ttk.Frame(notebook, padding=10)
        notebook.add(trouble_frame, text="Troubleshooting")
        
        trouble_text = tk.Text(trouble_frame, wrap=tk.WORD, font=("Arial", 10))
        trouble_text.pack(fill=tk.BOTH, expand=True)
        
        trouble_content = """COMMON ISSUES:

• Java not found: Install Java and ensure it's in PATH
• File not found: Check file paths and permissions
• Patching failed: Ensure APK version matches patches
• Out of memory: Close other applications or use smaller APK

TIPS:
• Check the log output for detailed error information
• Ensure you have enough disk space (2GB+ recommended)
• Use original APK files from trusted sources
• Keep ReVanced CLI and patches up to date

FILE LOCATIONS:
• Configuration: config.json (in application directory)
• Logs: logs/ folder (if enabled in settings)
"""
        trouble_text.insert(tk.END, trouble_content)
        trouble_text.config(state=tk.DISABLED)


class AboutDialog:
    """About dialog with application information."""
    
    @staticmethod
    def show(parent, version: str, author: str, license_name: str):
        """Show about dialog with application information."""
        about_window = tk.Toplevel(parent)
        about_window.title("About ReVanced Patcher")
        about_window.geometry("450x300")
        about_window.resizable(False, False)
        about_window.transient(parent)
        about_window.grab_set()
        
        # Center the window
        about_window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - about_window.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - about_window.winfo_height()) // 2
        about_window.geometry(f"+{x}+{y}")
        
        # About content
        about_frame = ttk.Frame(about_window, padding="20")
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(about_frame, text="ReVanced Patcher GUI", font=("Arial", 16, "bold")).pack(pady=(0, 15))
        
        # Version info
        info_frame = ttk.Frame(about_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text="Version:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(info_frame, text=f"v{version}", font=("Arial", 10)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Author info
        author_frame = ttk.Frame(about_frame)
        author_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(author_frame, text="Author:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(author_frame, text=author, font=("Arial", 10)).pack(side=tk.LEFT, padx=(5, 0))
        
        # License info
        license_frame = ttk.Frame(about_frame)
        license_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(license_frame, text="License:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        ttk.Label(license_frame, text=license_name, font=("Arial", 10)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Description
        desc_text = tk.Text(about_frame, height=8, wrap=tk.WORD, font=("Arial", 9), relief=tk.FLAT)
        desc_text.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        desc_content = """This is a GUI wrapper for the ReVanced CLI tool. It provides an easy-to-use interface for patching APK files with ReVanced patches.

Features:
• Cross-platform compatibility (Windows, macOS, Linux)
• Drag & drop file support
• Real-time progress monitoring
• Configurable logging and settings
• System validation and error handling

This software is provided under the MIT License. ReVanced is a community-driven project for customizing Android applications."""
        
        desc_text.insert(tk.END, desc_content)
        desc_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(about_frame, text="Close", command=about_window.destroy).pack(pady=(15, 0))