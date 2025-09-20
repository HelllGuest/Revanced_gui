"""APK patching functionality."""

import os
import subprocess
import threading
import time
from typing import Callable, List, Tuple

from .java_manager import JavaManager
from .system_monitor import SystemMonitor


class APKPatcher:
    """Handles APK patching operations."""
    
    def __init__(self, log_callback: Callable[[str], None]):
        self.log_callback = log_callback
        self.start_time = None
    
    def validate_inputs(self, cli_jar_path: str, patches_rvp_path: str, 
                       apk_path: str, output_path: str) -> List[Tuple[str, str]]:
        """Validate all input fields before patching."""
        errors = []
        
        # Check Java
        java_ok, java_info = JavaManager.validate_java_version_compatibility()
        if not java_ok:
            errors.append(('java_not_found', java_info))
        
        # Check files exist
        if not cli_jar_path or not os.path.exists(cli_jar_path):
            errors.append(('file_not_found', "ReVanced CLI JAR file not found"))
        
        if not patches_rvp_path or not os.path.exists(patches_rvp_path):
            errors.append(('file_not_found', "Patches RVP file not found"))
        
        if not apk_path or not os.path.exists(apk_path):
            errors.append(('file_not_found', "APK file not found"))
        
        if not output_path or not os.path.exists(output_path):
            errors.append(('file_not_found', "Output directory not found"))
        
        # Check disk space
        if SystemMonitor.is_psutil_available():
            free_gb, total_gb = SystemMonitor.get_disk_usage(output_path)
            if free_gb > 0 and apk_path and os.path.exists(apk_path):
                apk_size = os.path.getsize(apk_path)
                needed_gb = (apk_size * 3) // (1024**3)
                
                if free_gb < needed_gb:
                    errors.append(('insufficient_memory', 
                                 f"Need {needed_gb}GB, only {free_gb}GB free"))
        
        return errors
    
    def handle_patching_error(self, error_type: str, details: str):
        """Provide specific recovery suggestions."""
        error_solutions = {
            'java_not_found': "Install Java 8+ and ensure it's in your PATH",
            'file_not_found': "Check that all required files exist and are accessible",
            'corrupted_apk': "Use a different APK file or re-download the original",
            'patch_mismatch': "Ensure APK version matches the patches version",
            'insufficient_memory': "Free up disk space or use a smaller APK",
            'unknown': "Check the log for detailed error information"
        }
        
        solution = error_solutions.get(error_type, 
                                     "Check the log output for detailed error information")
        error_msg = f"Error: {details}\nSolution: {solution}"
        
        self.log_callback(error_msg)
        return error_msg
    
    def build_command(self, cli_jar_path: str, patches_rvp_path: str, 
                     apk_path: str, output_file: str) -> List[str]:
        """Build the patching command."""
        return [
            "java", "-jar", cli_jar_path, "patch",
            "-p", patches_rvp_path,
            "-o", output_file,
            apk_path
        ]
    
    def run_patching(self, cmd: List[str], output_file: str, 
                    success_callback: Callable, error_callback: Callable):
        """Run the patching process in a separate thread."""
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            for line in process.stdout:
                self.log_callback(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                elapsed = time.time() - self.start_time
                self.log_callback("-" * 60)
                self.log_callback(f"Patching completed successfully in {elapsed:.1f}s!")
                self.log_callback(f"Patched APK saved as: {output_file}")
                success_callback()
            else:
                error_msg = f"Patching failed with return code {process.returncode}"
                self.log_callback("-" * 60)
                self.log_callback(error_msg)
                error_callback('patch_mismatch', error_msg)
                
        except FileNotFoundError:
            error_msg = "Java not found. Please make sure Java is installed and available in your PATH."
            self.log_callback("-" * 60)
            self.log_callback(error_msg)
            error_callback('java_not_found', error_msg)
        except Exception as e:
            error_msg = f"Exception occurred: {str(e)}"
            self.log_callback("-" * 60)
            self.log_callback(error_msg)
            error_callback('unknown', error_msg)
        finally:
            self.log_callback("=" * 60)
    
    def start_patching(self, cli_jar_path: str, patches_rvp_path: str, 
                      apk_path: str, output_file: str, java_version: str,
                      success_callback: Callable, error_callback: Callable):
        """Start the patching process."""
        self.log_callback("=" * 60)
        self.log_callback("Starting ReVanced Patching Process")
        self.log_callback("=" * 60)
        self.log_callback(f"Input APK: {apk_path}")
        self.log_callback(f"Output file: {output_file}")
        self.log_callback(f"Java version: {java_version}")
        self.log_callback("Using all available patches")
        
        cmd = self.build_command(cli_jar_path, patches_rvp_path, apk_path, output_file)
        self.log_callback(f"Command: {' '.join(cmd)}")
        self.log_callback("-" * 60)
        
        self.start_time = time.time()
        
        thread = threading.Thread(
            target=self.run_patching, 
            args=(cmd, output_file, success_callback, error_callback)
        )
        thread.daemon = True
        thread.start()