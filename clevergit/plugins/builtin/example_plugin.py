"""
Example plugin: Commit Statistics

This plugin tracks commit statistics and provides insights about repository activity.
"""

from clevergit.plugins.interface import Plugin, PluginMetadata
from typing import Dict, Any


class CommitStatsPlugin(Plugin):
    """
    A simple example plugin that tracks commit statistics.
    
    This plugin demonstrates the plugin interface and lifecycle management.
    """
    
    def __init__(self) -> None:
        """Initialize the commit statistics plugin."""
        super().__init__()
        self._commit_count = 0
        self._active = False
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="commit_stats",
            version="1.0.0",
            author="CleverGit Team",
            description="Tracks and displays commit statistics",
            dependencies=[]
        )
    
    def on_load(self) -> None:
        """Called when plugin is loaded."""
        print(f"[CommitStats] Plugin loaded")
        self._commit_count = 0
    
    def on_enable(self) -> None:
        """Called when plugin is enabled."""
        print(f"[CommitStats] Plugin enabled - tracking commits")
        self._active = True
    
    def on_disable(self) -> None:
        """Called when plugin is disabled."""
        print(f"[CommitStats] Plugin disabled - stopped tracking")
        self._active = False
    
    def on_unload(self) -> None:
        """Called when plugin is unloaded."""
        print(f"[CommitStats] Plugin unloaded - Total commits tracked: {self._commit_count}")
        self._commit_count = 0
    
    def track_commit(self) -> None:
        """Track a new commit (example plugin method)."""
        if self._active:
            self._commit_count += 1
            print(f"[CommitStats] Commits tracked: {self._commit_count}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return {
            "total_commits": self._commit_count,
            "active": self._active
        }
