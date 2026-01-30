"""
Main GUI application entry point for CleverGit.
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from clevergit.ui.windows.main_window import MainWindow


def main() -> None:
    """Start the CleverGit GUI application."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("CleverGit")
    app.setApplicationVersion("0.1.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
