"""
Main GUI application entry point for CleverGit.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from clevergit.ui.windows.main_window import MainWindow
from clevergit.ui.themes import get_theme_manager
from clevergit.ui.settings import Settings
from clevergit import __version__


def main() -> None:
    """Start the CleverGit GUI application."""
    if "--version" in sys.argv or "-V" in sys.argv:
        print(f"CleverGit GUI v{__version__}")
        return

    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("CleverGit")
    app.setApplicationVersion("0.1.1")

    # Initialize theme system
    theme_manager = get_theme_manager()
    settings = Settings()

    # Load custom themes from settings
    custom_themes = settings.get_custom_themes()
    for name, theme_data in custom_themes.items():
        theme_manager.register_custom_theme(name, theme_data)

    # Apply theme
    if settings.use_system_theme():
        theme_manager.apply_system_theme()
    else:
        saved_theme = settings.get_theme()
        if saved_theme and theme_manager.get_theme(saved_theme):
            theme_manager.set_theme(saved_theme)
        else:
            # Default to light theme
            theme_manager.set_theme("light")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
