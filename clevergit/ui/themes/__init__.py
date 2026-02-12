"""Theme system for CleverGit UI."""

from .manager import ThemeManager, get_theme_manager
from .base import Theme
from .light import LightTheme
from .dark import DarkTheme

__all__ = [
    "Theme",
    "ThemeManager",
    "get_theme_manager",
    "LightTheme",
    "DarkTheme",
]
