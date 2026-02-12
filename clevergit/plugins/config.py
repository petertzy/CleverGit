"""
Plugin configuration management.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class PluginConfig:
    """Manages plugin configuration persistence."""
    
    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize plugin configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        if config_path is None:
            config_path = Path.home() / ".clevergit" / "plugins.json"
        
        self.config_path = config_path
        self._ensure_config_dir()
        self._configs: Dict[str, Dict[str, Any]] = self._load_configs()
    
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self.config_path.write_text("{}")
    
    def _load_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load plugin configurations from file.
        
        Returns:
            Dict[str, Dict[str, Any]]: Plugin configurations keyed by plugin name
        """
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_configs(self) -> None:
        """Save plugin configurations to file."""
        with open(self.config_path, "w") as f:
            json.dump(self._configs, f, indent=2)
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dict[str, Any]: Plugin configuration or empty dict if not found
        """
        return self._configs.get(plugin_name, {})
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> None:
        """
        Set configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            config: Configuration dictionary to save
        """
        self._configs[plugin_name] = config
        self._save_configs()
    
    def remove_plugin_config(self, plugin_name: str) -> None:
        """
        Remove configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self._configs:
            del self._configs[plugin_name]
            self._save_configs()
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all plugin configurations.
        
        Returns:
            Dict[str, Dict[str, Any]]: All plugin configurations
        """
        return self._configs.copy()
