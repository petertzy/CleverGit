"""
CleverGit - A high-level Git client library for Python.

This library provides a more intuitive and Pythonic way to interact with Git,
abstracting away complex command-line operations.
"""

__version__ = "0.1.0"

from clevergit.core.repo import Repo
from clevergit.plugins import Plugin, PluginManager, PluginMetadata

__all__ = ["Repo", "Plugin", "PluginManager", "PluginMetadata"]
