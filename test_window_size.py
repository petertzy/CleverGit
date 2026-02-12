#!/usr/bin/env python
"""Test window size after startup."""

import sys
from PySide6.QtWidgets import QApplication
from clevergit.ui.windows.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Print initial size
print(f"WINDOW_SIZE_AFTER_SHOW: {window.width()}x{window.height()}")
print(f"WINDOW_MAX_SIZE: {window.maximumWidth()}x{window.maximumHeight()}")
sys.stdout.flush()

# Process events to let the window fully initialize
app.processEvents()

# Print final size
print(f"WINDOW_SIZE_AFTER_PROCESS: {window.width()}x{window.height()}")
sys.stdout.flush()

sys.exit(0)
