#!/usr/bin/env python3
"""
ReVanced Patcher GUI - Main Entry Point

A comprehensive GUI wrapper for the ReVanced CLI tool that provides an easy-to-use
interface for patching APK files with ReVanced patches.

Author: ReVanced Community
License: MIT
Version: 1.3.1
"""

import sys
import tkinter as tk
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

from src.revanced_gui import ReVancedGUI


def main():
    """Main entry point for the ReVanced GUI application."""
    # Create root window with drag & drop support if available
    root = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
    
    # Create application instance
    app = ReVancedGUI(root)
    
    if app:
        # Handle application close
        def on_closing():
            app.cleanup()
            root.quit()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the main event loop
        try:
            root.mainloop()
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
            app.cleanup()
        except Exception as e:
            print(f"Unexpected error: {e}")
            app.cleanup()
            raise


if __name__ == "__main__":
    main()