"""System monitoring and resource management."""

import os
import threading
import time
import logging

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemMonitor:
    """Handles system monitoring and resource checking."""
    
    def __init__(self):
        self.monitoring = False
    
    @staticmethod
    def get_disk_usage(path: str = None) -> tuple[int, int]:
        """Get disk usage for specific path, cross-platform compatible."""
        if not PSUTIL_AVAILABLE:
            return 0, 0
            
        try:
            check_path = path if path and os.path.exists(path) else os.getcwd()
            
            # On Windows, get the drive root
            if os.name == 'nt':
                drive = os.path.splitdrive(check_path)[0]
                if drive:
                    check_path = drive + '\\'
            
            disk = psutil.disk_usage(check_path)
            return disk.free // (1024**3), disk.total // (1024**3)
        except Exception as e:
            logging.warning(f"Could not check disk usage: {e}")
            return 0, 0
    
    def start_system_monitor(self, log_callback):
        """Start background system monitoring."""
        def monitor():
            while self.monitoring:
                if PSUTIL_AVAILABLE:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    if cpu_percent > 80:
                        log_callback(f"High CPU usage: {cpu_percent}%")
                time.sleep(5)
        
        self.monitoring = True
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring = False
    
    @staticmethod
    def is_psutil_available() -> bool:
        """Check if psutil is available."""
        return PSUTIL_AVAILABLE