"""
Plugin interface and base classes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class PluginState(Enum):
    """Plugin lifecycle states."""
    UNLOADED = "unloaded"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginMetadata:
    """Plugin metadata information."""
    name: str
    version: str
    author: str
    description: str
    dependencies: Optional[List[str]] = None
    
    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []


class Plugin(ABC):
    """
    Abstract base class for CleverGit plugins.
    
    All plugins must inherit from this class and implement the required methods.
    """
    
    def __init__(self) -> None:
        """Initialize the plugin."""
        self._state = PluginState.UNLOADED
        self._config: Dict[str, Any] = {}
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return plugin metadata.
        
        Returns:
            PluginMetadata: Plugin information including name, version, author, etc.
        """
        pass
    
    @abstractmethod
    def on_load(self) -> None:
        """
        Called when the plugin is loaded.
        
        This is where you should initialize resources but not start operations.
        """
        pass
    
    @abstractmethod
    def on_enable(self) -> None:
        """
        Called when the plugin is enabled.
        
        This is where you should start plugin operations.
        """
        pass
    
    @abstractmethod
    def on_disable(self) -> None:
        """
        Called when the plugin is disabled.
        
        This is where you should stop plugin operations but keep resources.
        """
        pass
    
    @abstractmethod
    def on_unload(self) -> None:
        """
        Called when the plugin is unloaded.
        
        This is where you should clean up all resources.
        """
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin with settings.
        
        Args:
            config: Dictionary of configuration settings
        """
        self._config = config
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current plugin configuration.
        
        Returns:
            Dict[str, Any]: Current configuration settings
        """
        return self._config.copy()
    
    def get_state(self) -> PluginState:
        """
        Get the current plugin state.
        
        Returns:
            PluginState: Current plugin state
        """
        return self._state
    
    def _set_state(self, state: PluginState) -> None:
        """
        Set the plugin state (internal use only).
        
        Args:
            state: New plugin state
        """
        self._state = state
