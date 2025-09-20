"""Java version detection and validation."""

import subprocess
import re


class JavaManager:
    """Handles Java installation detection and version validation."""
    
    @staticmethod
    def parse_java_version(version_string: str) -> int:
        """Parse Java version handling both old and new formats."""
        try:
            version = version_string.strip().strip('"')
            # Old format: 1.8.0_291 -> 8, New format: 11.0.1 -> 11
            return int(version.split('.')[1]) if version.startswith('1.') else int(version.split('.')[0])
        except (ValueError, IndexError):
            return 0
    
    @staticmethod
    def check_java_installation() -> tuple[bool, str]:
        """Check if Java is installed and return version info."""
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            version_output = result.stderr.split('\n')[0] if result.stderr else ""
            version_match = re.search(r'version\s+"([^"]+)"', version_output)
            
            if not version_match:
                return False, "Version format not recognized"
                
            version_str = version_match.group(1)
            major_version = JavaManager.parse_java_version(version_str)
            
            if major_version >= 8:
                return True, f"{version_str} (Java {major_version})"
            else:
                return False, f"Unsupported: {version_str} (need Java 8+)"
            
        except subprocess.TimeoutExpired:
            return False, "Java check timeout"
        except FileNotFoundError:
            return False, "Java not found in PATH"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def validate_java_version_compatibility() -> tuple[bool, str]:
        """Check if Java version is compatible with ReVanced CLI."""
        java_ok, java_info = JavaManager.check_java_installation()
        if java_ok:
            version_num = JavaManager.parse_java_version(java_info)
            if version_num < 11:
                return False, f"Java {version_num} detected. ReVanced CLI may require Java 11+"
        return java_ok, java_info