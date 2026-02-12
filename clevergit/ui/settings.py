"""
Settings management for CleverGit GUI.
"""

import json
from pathlib import Path
from typing import Optional, Dict, List


class Settings:
    """Manage application settings and persistence."""

    def __init__(self) -> None:
        """Initialize settings with config file path."""
        self.config_dir = Path.home() / ".config" / "clevergit"
        self.config_file = self.config_dir / "settings.json"
        self._settings: dict = {}
        self._load()

    def _load(self) -> None:
        """Load settings from config file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self._settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or unreadable, start with empty settings
                self._settings = {}
        else:
            self._settings = {}

    def _save(self) -> None:
        """Save settings to config file."""
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_file, "w") as f:
                json.dump(self._settings, f, indent=2)
        except IOError:
            # Silently fail if we can't save settings
            pass

    def get_last_repository(self) -> Optional[str]:
        """Get the last opened repository path."""
        return self._settings.get("last_repository")

    def set_last_repository(self, path: str) -> None:
        """Set the last opened repository path."""
        self._settings["last_repository"] = path
        self._save()

    def get_repository_branches(self) -> Dict[str, str]:
        """Get all repository-branch mappings."""
        return self._settings.get("repository_branches", {})

    def get_repository_branch(self, repo_path: str) -> Optional[str]:
        """Get the last active branch for a repository."""
        branches = self.get_repository_branches()
        return branches.get(repo_path)

    def set_repository_branch(self, repo_path: str, branch: str) -> None:
        """Set the last active branch for a repository."""
        if "repository_branches" not in self._settings:
            self._settings["repository_branches"] = {}
        self._settings["repository_branches"][repo_path] = branch
        self._save()

    def get_recent_repositories(self, limit: int = 10) -> list[str]:
        """Get list of recently opened repositories."""
        recent = self._settings.get("recent_repositories", [])

        # Deduplicate based on normalized paths while preserving order
        seen = set()
        deduplicated = []
        for path in recent:
            normalized = str(Path(path).resolve())
            if normalized not in seen:
                seen.add(normalized)
                deduplicated.append(normalized)  # Return normalized path

        return deduplicated[:limit]

    def add_recent_repository(self, path: str) -> None:
        """Add a repository to the recent list."""
        if "recent_repositories" not in self._settings:
            self._settings["recent_repositories"] = []

        # Normalize the path to avoid duplicates
        normalized_path = str(Path(path).resolve())

        recent = self._settings["recent_repositories"]

        # Remove if already in list (checking normalized paths)
        # Always store normalized paths for consistency
        normalized_recent = []
        for p in recent:
            normalized_p = str(Path(p).resolve())
            if normalized_p != normalized_path:
                normalized_recent.append(normalized_p)

        # Add to front of list with normalized path
        normalized_recent.insert(0, normalized_path)

        # Keep only last 10
        self._settings["recent_repositories"] = normalized_recent[:10]
        self._save()

    def remove_recent_repository(self, path: str) -> None:
        """Remove a repository from the recent list."""
        if "recent_repositories" not in self._settings:
            return

        # Normalize the path to match stored paths
        normalized_path = str(Path(path).resolve())

        recent = self._settings["recent_repositories"]

        # Remove all entries that match this normalized path
        normalized_recent = []
        for p in recent:
            normalized_p = str(Path(p).resolve())
            if normalized_p != normalized_path:
                normalized_recent.append(p)

        self._settings["recent_repositories"] = normalized_recent
        self._save()

    def get_theme(self) -> Optional[str]:
        """Get the selected theme name."""
        return self._settings.get("theme")

    def set_theme(self, theme: str) -> None:
        """Set the selected theme name."""
        self._settings["theme"] = theme
        self._save()

    def get_custom_themes(self) -> Dict[str, Dict]:
        """Get all custom themes."""
        return self._settings.get("custom_themes", {})

    def add_custom_theme(self, name: str, theme_data: Dict) -> None:
        """Add or update a custom theme."""
        if "custom_themes" not in self._settings:
            self._settings["custom_themes"] = {}
        self._settings["custom_themes"][name] = theme_data
        self._save()

    def remove_custom_theme(self, name: str) -> None:
        """Remove a custom theme."""
        if "custom_themes" in self._settings:
            self._settings["custom_themes"].pop(name, None)
            self._save()

    def use_system_theme(self) -> bool:
        """Check if system theme should be followed."""
        return self._settings.get("use_system_theme", True)

    def get_window_geometry(self, window_id: str = "main") -> Optional[Dict]:
        """Get window geometry (position and size)."""
        geometries = self._settings.get("window_geometries", {})
        return geometries.get(window_id)

    def set_window_geometry(
        self, x: int, y: int, width: int, height: int, window_id: str = "main"
    ) -> None:
        """Set window geometry (position and size)."""
        if "window_geometries" not in self._settings:
            self._settings["window_geometries"] = {}
        self._settings["window_geometries"][window_id] = {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        self._save()

    def get_open_tabs(self, window_id: str = "main") -> List[str]:
        """Get list of open repository paths for a window."""
        windows = self._settings.get("session_windows", {})
        window_data = windows.get(window_id, {})
        return window_data.get("tabs", [])

    def set_open_tabs(self, tabs: List[str], window_id: str = "main") -> None:
        """Set list of open repository paths for a window."""
        if "session_windows" not in self._settings:
            self._settings["session_windows"] = {}
        if window_id not in self._settings["session_windows"]:
            self._settings["session_windows"][window_id] = {}
        self._settings["session_windows"][window_id]["tabs"] = tabs
        self._save()

    def get_active_tab(self, window_id: str = "main") -> int:
        """Get the last active tab index for a window."""
        windows = self._settings.get("session_windows", {})
        window_data = windows.get(window_id, {})
        return window_data.get("active_tab", 0)

    def set_active_tab(self, index: int, window_id: str = "main") -> None:
        """Set the last active tab index for a window."""
        if "session_windows" not in self._settings:
            self._settings["session_windows"] = {}
        if window_id not in self._settings["session_windows"]:
            self._settings["session_windows"][window_id] = {}
        self._settings["session_windows"][window_id]["active_tab"] = index
        self._save()

    def get_session_windows(self) -> List[Dict]:
        """Get session state for all windows."""
        return self._settings.get("session_state", [])

    def set_session_windows(self, windows: List[Dict]) -> None:
        """Set session state for all windows."""
        self._settings["session_state"] = windows
        self._save()

    def get_shortcuts(self) -> Optional[Dict[str, str]]:
        """Get custom keyboard shortcuts."""
        return self._settings.get("shortcuts")

    def set_shortcuts(self, shortcuts: Dict[str, str]) -> None:
        """Set custom keyboard shortcuts."""
        self._settings["shortcuts"] = shortcuts
        self._save()
