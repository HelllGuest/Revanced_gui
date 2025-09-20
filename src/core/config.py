"""Configuration management for ReVanced GUI."""

import json
import logging
from pathlib import Path
import re


class ConfigManager:
    """Handles configuration loading, saving, and management."""
    
    def __init__(self, script_dir: Path):
        self.script_dir = script_dir
        self.config_file = script_dir / "config.json"
        self.save_logs_enabled = False
        self.save_config_enabled = True
    
    def load_config(self, gui_instance):
        """Load configuration from file and apply to GUI instance."""
        if not self.save_config_enabled or not self.config_file.exists():
            return
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            if not isinstance(config, dict):
                raise ValueError("Invalid config format")
            
            # Load settings
            self.save_logs_enabled = config.get('save_logs_enabled', False)
            self.save_config_enabled = config.get('save_config_enabled', True)
            
            # Update GUI checkboxes if they exist
            if hasattr(gui_instance, 'logs_var'):
                gui_instance.logs_var.set(self.save_logs_enabled)
            if hasattr(gui_instance, 'config_var'):
                gui_instance.config_var.set(self.save_config_enabled)
            
            # Restore file paths
            gui_instance.cli_jar_path.set(str(config.get('last_cli_path', '')))
            gui_instance.patches_rvp_path.set(str(config.get('last_patches_path', '')))
            
            # Only restore output path if no APK is selected yet
            if not gui_instance.apk_path.get():
                gui_instance.output_path.set(str(config.get('last_output_dir', '')))
            
            # Restore window geometry
            geometry = config.get('window_geometry', '')
            if geometry and re.match(r'\d+x\d+\+\d+\+\d+', geometry):
                gui_instance.root.geometry(geometry)
            
            logging.info("Configuration loaded successfully")
            
        except (json.JSONDecodeError, ValueError, OSError) as e:
            logging.warning(f"Config load error (using defaults): {e}")
        except Exception as e:
            logging.error(f"Unexpected config error: {e}")
    
    def save_config(self, gui_instance):
        """Save current configuration to file."""
        if not self.save_config_enabled:
            return
            
        try:
            self.config_file.parent.mkdir(exist_ok=True)
            
            config = {
                'save_logs_enabled': self.save_logs_enabled,
                'save_config_enabled': self.save_config_enabled,
                'last_cli_path': gui_instance.cli_jar_path.get(),
                'last_patches_path': gui_instance.patches_rvp_path.get(),
                'last_output_dir': gui_instance.output_path.get(),
                'window_geometry': gui_instance.root.geometry(),
                'version': gui_instance.__class__.__version__,
            }
            
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            temp_file.replace(self.config_file)
            
        except Exception as e:
            logging.error(f"Failed to save config: {e}")