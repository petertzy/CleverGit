"""Theme manager for CleverGit."""

import sys
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QPalette

from .base import Theme
from .light import LightTheme
from .dark import DarkTheme


class ThemeManager:
    """Manages theme selection and application."""

    _instance: Optional["ThemeManager"] = None

    def __init__(self):
        """Initialize theme manager."""
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[Theme] = None
        self._custom_themes: Dict[str, Theme] = {}

        # Register built-in themes
        self.register_theme(LightTheme())
        self.register_theme(DarkTheme())

    def register_theme(self, theme: Theme) -> None:
        """Register a theme.

        Args:
            theme: Theme to register
        """
        self._themes[theme.name] = theme

    def register_custom_theme(self, name: str, theme_data: Dict[str, Any]) -> None:
        """Register a custom theme from data.

        Args:
            name: Name for the custom theme
            theme_data: Dictionary containing theme properties
        """
        theme = Theme(
            name=name,
            background=theme_data.get("background", "#ffffff"),
            background_secondary=theme_data.get("background_secondary", "#f6f8fa"),
            background_hover=theme_data.get("background_hover", "#e1e4e8"),
            text=theme_data.get("text", "#24292e"),
            text_secondary=theme_data.get("text_secondary", "#586069"),
            text_disabled=theme_data.get("text_disabled", "#959da5"),
            button_primary=theme_data.get("button_primary", "#0366d6"),
            button_success=theme_data.get("button_success", "#28a745"),
            button_warning=theme_data.get("button_warning", "#ff9800"),
            button_danger=theme_data.get("button_danger", "#d73a49"),
            button_info=theme_data.get("button_info", "#0366d6"),
            diff_added=theme_data.get("diff_added", "#e6ffed"),
            diff_removed=theme_data.get("diff_removed", "#ffeef0"),
            diff_modified=theme_data.get("diff_modified", "#fff8c5"),
            diff_context=theme_data.get("diff_context", "#ffffff"),
            graph_colors=theme_data.get(
                "graph_colors",
                [
                    "#e74c3c",
                    "#3498db",
                    "#2ecc71",
                    "#f39c12",
                    "#9b59b6",
                    "#1abc9c",
                    "#e67e22",
                    "#95a5a6",
                ],
            ),
            border=theme_data.get("border", "#d1d5da"),
            separator=theme_data.get("separator", "#e1e4e8"),
            status_success=theme_data.get("status_success", "#28a745"),
            status_warning=theme_data.get("status_warning", "#ff9800"),
            status_error=theme_data.get("status_error", "#d73a49"),
            status_info=theme_data.get("status_info", "#0366d6"),
            selection_background=theme_data.get("selection_background", "#0366d6"),
            selection_text=theme_data.get("selection_text", "#ffffff"),
        )
        self._custom_themes[name] = theme
        self._themes[name] = theme

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get a theme by name.

        Args:
            name: Theme name

        Returns:
            Theme object or None if not found
        """
        return self._themes.get(name)

    def get_available_themes(self) -> list:
        """Get list of available theme names.

        Returns:
            List of theme names
        """
        return list(self._themes.keys())

    def get_current_theme(self) -> Optional[Theme]:
        """Get the current theme.

        Returns:
            Current theme or None
        """
        return self._current_theme

    def set_theme(self, name: str) -> bool:
        """Set the current theme.

        Args:
            name: Theme name

        Returns:
            True if theme was set successfully
        """
        theme = self.get_theme(name)
        if theme:
            self._current_theme = theme
            self._apply_theme(theme)
            return True
        return False

    def detect_system_theme(self) -> str:
        """Detect system theme preference.

        Returns:
            "light" or "dark" based on system preference
        """
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtGui import QPalette

            app = QApplication.instance()
            if app:
                palette = app.palette()
                # Check if window background is light or dark
                window_color = palette.color(QPalette.Window)
                # Calculate luminance (perceived brightness)
                luminance = (
                    0.299 * window_color.red()
                    + 0.587 * window_color.green()
                    + 0.114 * window_color.blue()
                )
                return "dark" if luminance < 128 else "light"
        except ImportError:
            pass

        # Default to light theme if no app instance or Qt not available
        return "light"

    def apply_system_theme(self) -> None:
        """Apply theme based on system preference."""
        theme_name = self.detect_system_theme()
        self.set_theme(theme_name)

    def _apply_theme(self, theme: Theme) -> None:
        """Apply a theme to the application.

        Args:
            theme: Theme to apply
        """
        try:
            from PySide6.QtWidgets import QApplication

            app = QApplication.instance()
            if app:
                stylesheet = theme.get_stylesheet()
                app.setStyleSheet(stylesheet)
        except ImportError:
            # Qt not available, skip application
            pass

    def export_theme(self, name: str) -> Optional[Dict[str, Any]]:
        """Export a theme to a dictionary.

        Args:
            name: Theme name

        Returns:
            Theme data dictionary or None
        """
        theme = self.get_theme(name)
        if theme:
            return theme.to_dict()
        return None


# Singleton instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the singleton theme manager instance.

    Returns:
        ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
