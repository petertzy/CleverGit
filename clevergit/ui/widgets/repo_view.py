"""
Repository information view widget.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class RepositoryView(QWidget):
    """Display repository information."""
    
    def __init__(self) -> None:
        super().__init__()
        self.path_label = QLabel("Path: N/A")
        self.branch_label = QLabel("Branch: N/A")
        self.status_label = QLabel("Status: N/A")
        
        layout = QVBoxLayout()
        layout.addWidget(self.path_label)
        layout.addWidget(self.branch_label)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def update_info(self, path: str, branch: str, status: str) -> None:
        """Update repository information display."""
        self.path_label.setText(f"Path: {path}")
        self.branch_label.setText(f"Branch: {branch}")
        self.status_label.setText(f"Status: {status}")
