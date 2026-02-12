"""
CleverGit Plugin System

This module provides a plugin architecture for extending CleverGit functionality.
"""

from clevergit.plugins.interface import Plugin, PluginMetadata
from clevergit.plugins.manager import PluginManager
from clevergit.plugins.loader import PluginLoader
from clevergit.plugins.config import PluginConfig

__all__ = [
    "Plugin",
    "PluginMetadata",
    "PluginManager",
    "PluginLoader",
    "PluginConfig",
]
