"""
Plugin loading and discovery mechanism.
"""

import importlib.util
import sys
import logging
from pathlib import Path
from typing import List, Dict, Type, Optional
from clevergit.plugins.interface import Plugin

logger = logging.getLogger(__name__)


class PluginLoader:
    """Handles plugin discovery and loading."""
    
    def __init__(self) -> None:
        """Initialize the plugin loader."""
        self._plugin_paths: List[Path] = []
        self._loaded_classes: Dict[str, Type[Plugin]] = {}
    
    def add_plugin_path(self, path: Path) -> None:
        """
        Add a directory to search for plugins.
        
        Args:
            path: Path to directory containing plugins
        """
        if path.exists() and path.is_dir():
            self._plugin_paths.append(path)
    
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in registered paths.
        
        Returns:
            List[str]: List of discovered plugin module names
        """
        discovered = []
        
        for plugin_path in self._plugin_paths:
            # Look for Python files (excluding __init__.py)
            for py_file in plugin_path.glob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                module_name = py_file.stem
                discovered.append(module_name)
        
        return discovered
    
    def load_plugin(self, module_name: str) -> Optional[Type[Plugin]]:
        """
        Load a plugin class from a module.
        
        Args:
            module_name: Name of the plugin module
            
        Returns:
            Type[Plugin]: Plugin class if found, None otherwise
        """
        # Check if already loaded
        if module_name in self._loaded_classes:
            return self._loaded_classes[module_name]
        
        # Try to find and load the module
        for plugin_path in self._plugin_paths:
            module_file = plugin_path / f"{module_name}.py"
            if module_file.exists():
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(
                        f"clevergit_plugin_{module_name}",
                        module_file
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[spec.name] = module
                        spec.loader.exec_module(module)
                        
                        # Find Plugin subclass in module
                        plugin_class = self._find_plugin_class(module)
                        if plugin_class:
                            self._loaded_classes[module_name] = plugin_class
                            return plugin_class
                except Exception as e:
                    logger.error(f"Error loading plugin {module_name}: {e}")
                    return None
        
        return None
    
    def _find_plugin_class(self, module: object) -> Optional[Type[Plugin]]:
        """
        Find a Plugin subclass in a module.
        
        Args:
            module: The loaded module
            
        Returns:
            Type[Plugin]: Plugin class if found, None otherwise
        """
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # Check if it's a class, is a subclass of Plugin, and is not Plugin itself
            if (isinstance(attr, type) and 
                issubclass(attr, Plugin) and 
                attr is not Plugin):
                return attr
        return None
    
    def get_loaded_plugins(self) -> Dict[str, Type[Plugin]]:
        """
        Get all loaded plugin classes.
        
        Returns:
            Dict[str, Type[Plugin]]: Dictionary of loaded plugin classes keyed by module name
        """
        return self._loaded_classes.copy()
    
    def unload_plugin(self, module_name: str) -> None:
        """
        Unload a plugin class.
        
        Args:
            module_name: Name of the plugin module to unload
        """
        if module_name in self._loaded_classes:
            del self._loaded_classes[module_name]
            # Also remove from sys.modules if present
            module_full_name = f"clevergit_plugin_{module_name}"
            if module_full_name in sys.modules:
                del sys.modules[module_full_name]
