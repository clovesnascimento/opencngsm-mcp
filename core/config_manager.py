"""
OpenCngsm v3.1 - Configuration Manager
Universal path management for cross-platform deployment
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional
import platform
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Universal configuration manager for OpenCngsm
    
    Features:
    - Auto-detects installation directory
    - Cross-platform path resolution
    - User-specific config directories
    - Environment variable support
    - Default config generation
    """
    
    def __init__(self):
        """Initialize configuration manager"""
        self.platform = platform.system()  # Windows, Linux, Darwin (macOS)
        self.home_dir = Path.home()
        
        # Detect installation directory
        self.install_dir = self._detect_install_dir()
        
        # Config directory (user-specific)
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / 'config.json'
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create config
        self.config = self._load_or_create_config()
    
    def _detect_install_dir(self) -> Path:
        """
        Auto-detect OpenCngsm installation directory
        
        Returns:
            Path to installation directory
        """
        # Method 1: Environment variable
        if 'OPENCNGSM_HOME' in os.environ:
            return Path(os.environ['OPENCNGSM_HOME'])
        
        # Method 2: Current working directory (if running from install dir)
        cwd = Path.cwd()
        if (cwd / 'skills').exists() and (cwd / 'core').exists():
            return cwd
        
        # Method 3: Script location
        if hasattr(sys, 'frozen'):
            # Running as compiled executable
            return Path(sys.executable).parent
        else:
            # Running as Python script
            # Go up from core/config_manager.py to root
            return Path(__file__).parent.parent.parent
        
        # Fallback: current directory
        return cwd
    
    def _get_config_dir(self) -> Path:
        """
        Get user-specific config directory (cross-platform)
        
        Returns:
            Path to config directory
        """
        if self.platform == 'Windows':
            # Windows: %APPDATA%/OpenCngsm
            base = Path(os.environ.get('APPDATA', self.home_dir / 'AppData' / 'Roaming'))
            return base / 'OpenCngsm'
        
        elif self.platform == 'Darwin':
            # macOS: ~/Library/Application Support/OpenCngsm
            return self.home_dir / 'Library' / 'Application Support' / 'OpenCngsm'
        
        else:
            # Linux/Unix: ~/.config/opencngsm
            xdg_config = os.environ.get('XDG_CONFIG_HOME', self.home_dir / '.config')
            return Path(xdg_config) / 'opencngsm'
    
    def _load_or_create_config(self) -> Dict:
        """Load existing config or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"✅ Loaded config from: {self.config_file}")
                return config
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}")
        
        # Create default config
        config = self._create_default_config()
        self.save_config(config)
        logger.info(f"✅ Created default config: {self.config_file}")
        return config
    
    def _create_default_config(self) -> Dict:
        """Create default configuration"""
        return {
            "version": "3.1",
            "install_dir": str(self.install_dir),
            "config_dir": str(self.config_dir),
            "platform": self.platform,
            
            "gateway": {
                "bind": "loopback",
                "port": 18789,
                "auth": {
                    "mode": "token",
                    "token": self._generate_token()
                }
            },
            
            "skills": {
                "directory": str(self.install_dir / 'skills'),
                "auto_load": True,
                "sandbox": {
                    "enabled": False,
                    "default_cpu_limit": 1.0,
                    "default_memory_limit": "512m"
                }
            },
            
            "channels": {},
            
            "logging": {
                "level": "INFO",
                "file": str(self.config_dir / 'logs' / 'opencngsm.log')
            }
        }
    
    def _generate_token(self) -> str:
        """Generate secure random token"""
        import secrets
        return secrets.token_hex(24)  # 48 characters
    
    def save_config(self, config: Optional[Dict] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"💾 Config saved to: {self.config_file}")
    
    def get(self, key: str, default=None):
        """
        Get config value by key (supports dot notation)
        
        Example:
            config.get('gateway.port')  # Returns 18789
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value):
        """
        Set config value by key (supports dot notation)
        
        Example:
            config.set('gateway.port', 8080)
        """
        keys = key.split('.')
        target = self.config
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
        self.save_config()
    
    def get_path(self, key: str, create: bool = False) -> Path:
        """
        Get path from config and resolve it
        
        Args:
            key: Config key (e.g., 'skills.directory')
            create: If True, create directory if it doesn't exist
        
        Returns:
            Resolved Path object
        """
        path_str = self.get(key)
        
        if path_str is None:
            raise KeyError(f"Config key not found: {key}")
        
        path = Path(path_str)
        
        # Resolve relative to install_dir if not absolute
        if not path.is_absolute():
            path = self.install_dir / path
        
        if create:
            path.mkdir(parents=True, exist_ok=True)
        
        return path
    
    def get_skills_dir(self) -> Path:
        """Get skills directory"""
        return self.get_path('skills.directory', create=True)
    
    def get_logs_dir(self) -> Path:
        """Get logs directory"""
        log_file = self.get_path('logging.file')
        log_dir = log_file.parent
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
    
    def get_data_dir(self) -> Path:
        """Get data directory"""
        data_dir = self.config_dir / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    @staticmethod
    def get_instance() -> 'ConfigManager':
        """Get singleton instance"""
        if not hasattr(ConfigManager, '_instance'):
            ConfigManager._instance = ConfigManager()
        return ConfigManager._instance


# Global instance
config = ConfigManager.get_instance()


# Convenience functions
def get_config_dir() -> Path:
    """Get user config directory"""
    return config.config_dir


def get_install_dir() -> Path:
    """Get installation directory"""
    return config.install_dir


def get_skills_dir() -> Path:
    """Get skills directory"""
    return config.get_skills_dir()


def get_data_dir() -> Path:
    """Get data directory"""
    return config.get_data_dir()


def get_logs_dir() -> Path:
    """Get logs directory"""
    return config.get_logs_dir()


# Example usage
if __name__ == "__main__":
    print("🔧 OpenCngsm Configuration")
    print(f"Platform: {config.platform}")
    print(f"Install Dir: {config.install_dir}")
    print(f"Config Dir: {config.config_dir}")
    print(f"Config File: {config.config_file}")
    print(f"Skills Dir: {config.get_skills_dir()}")
    print(f"Data Dir: {config.get_data_dir()}")
    print(f"Logs Dir: {config.get_logs_dir()}")
    print(f"\nGateway Port: {config.get('gateway.port')}")
    print(f"Auth Token: {config.get('gateway.auth.token')[:20]}...")
