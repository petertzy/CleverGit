"""
Plugin lifecycle and registry management.
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
from clevergit.plugins.interface import Plugin, PluginState, PluginMetadata
from clevergit.plugins.loader import PluginLoader
from clevergit.plugins.config import PluginConfig

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages plugin lifecycle, registry, and coordination.
    
    This is the main entry point for interacting with the plugin system.
    """
    
    def __init__(self, config_path: Optional[Path] = None) -> None:
        """
        Initialize the plugin manager.
        
        Args:
            config_path: Path to plugin configuration file
        """
        self._loader = PluginLoader()
        self._config = PluginConfig(config_path)
        self._plugins: Dict[str, Plugin] = {}
        self._setup_default_paths()
    
    def _setup_default_paths(self) -> None:
        """Set up default plugin search paths."""
        # Add user plugins directory
        user_plugins = Path.home() / ".clevergit" / "plugins"
        user_plugins.mkdir(parents=True, exist_ok=True)
        self._loader.add_plugin_path(user_plugins)
        
        # Add built-in plugins directory if it exists
        try:
            from clevergit.plugins import builtin
            builtin_path = Path(builtin.__file__).parent
            self._loader.add_plugin_path(builtin_path)
        except ImportError:
            pass
    
    def add_plugin_path(self, path: Path) -> None:
        """
        Add a custom plugin search path.
        
        Args:
            path: Directory path to search for plugins
        """
        self._loader.add_plugin_path(path)
    
    def discover_plugins(self) -> List[str]:
        """
        Discover all available plugins.
        
        Returns:
            List[str]: List of discovered plugin names
        """
        return self._loader.discover_plugins()
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if plugin_name in self._plugins:
            return True  # Already loaded
        
        plugin_class = self._loader.load_plugin(plugin_name)
        if not plugin_class:
            return False
        
        try:
            # Instantiate the plugin
            plugin = plugin_class()
            
            # Load configuration
            config = self._config.get_plugin_config(plugin_name)
            plugin.configure(config)
            
            # Call on_load lifecycle method
            plugin.on_load()
            plugin._set_state(PluginState.LOADED)
            
            self._plugins[plugin_name] = plugin
            return True
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a loaded plugin.
        
        Args:
            plugin_name: Name of the plugin to enable
            
        Returns:
            bool: True if enabled successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            # Try to load it first
            if not self.load_plugin(plugin_name):
                return False
        
        plugin = self._plugins[plugin_name]
        if plugin.get_state() == PluginState.ENABLED:
            return True  # Already enabled
        
        try:
            plugin.on_enable()
            plugin._set_state(PluginState.ENABLED)
            return True
        except Exception as e:
            logger.error(f"Error enabling plugin {plugin_name}: {e}")
            plugin._set_state(PluginState.ERROR)
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable an enabled plugin.
        
        Args:
            plugin_name: Name of the plugin to disable
            
        Returns:
            bool: True if disabled successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_name]
        if plugin.get_state() != PluginState.ENABLED:
            return True  # Already disabled
        
        try:
            plugin.on_disable()
            plugin._set_state(PluginState.DISABLED)
            return True
        except Exception as e:
            logger.error(f"Error disabling plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            bool: True if unloaded successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            return True  # Already unloaded
        
        plugin = self._plugins[plugin_name]
        
        # Disable first if enabled
        if plugin.get_state() == PluginState.ENABLED:
            self.disable_plugin(plugin_name)
        
        try:
            plugin.on_unload()
            plugin._set_state(PluginState.UNLOADED)
            del self._plugins[plugin_name]
            self._loader.unload_plugin(plugin_name)
            return True
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """
        Get a loaded plugin instance.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[Plugin]: Plugin instance if loaded, None otherwise
        """
        return self._plugins.get(plugin_name)
    
    def list_plugins(self) -> List[PluginMetadata]:
        """
        List all loaded plugins.
        
        Returns:
            List[PluginMetadata]: List of loaded plugin metadata
        """
        return [plugin.get_metadata() for plugin in self._plugins.values()]
    
    def get_plugin_state(self, plugin_name: str) -> Optional[PluginState]:
        """
        Get the state of a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[PluginState]: Plugin state if loaded, None otherwise
        """
        plugin = self._plugins.get(plugin_name)
        return plugin.get_state() if plugin else None
    
    def configure_plugin(self, plugin_name: str, config: Dict) -> bool:
        """
        Configure a plugin and persist the configuration.
        
        Args:
            plugin_name: Name of the plugin
            config: Configuration dictionary
            
        Returns:
            bool: True if configured successfully, False otherwise
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return False
        
        try:
            plugin.configure(config)
            self._config.set_plugin_config(plugin_name, config)
            return True
        except Exception as e:
            logger.error(f"Error configuring plugin {plugin_name}: {e}")
            return False
