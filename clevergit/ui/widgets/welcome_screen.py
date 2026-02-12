"""
Welcome screen widget displayed when no repository tabs are open.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, Signal


class WelcomeScreen(QWidget):
    """Welcome screen with options to open or clone a repository."""
    
    open_repository_clicked = Signal()
    clone_repository_clicked = Signal()
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the welcome screen UI."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        
        # Title
        title = QLabel("Welcome to CleverGit")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Get started by opening or cloning a repository")
        subtitle.setStyleSheet("font-size: 14px; color: gray;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        # Open button
        open_btn = QPushButton("📁 Open Repository")
        open_btn.setMinimumWidth(200)
        open_btn.setMinimumHeight(40)
        open_btn.clicked.connect(self.open_repository_clicked.emit)
        button_layout.addWidget(open_btn)
        
        # Clone button
        clone_btn = QPushButton("⬇️ Clone Repository")
        clone_btn.setMinimumWidth(200)
        clone_btn.setMinimumHeight(40)
        clone_btn.clicked.connect(self.clone_repository_clicked.emit)
        button_layout.addWidget(clone_btn)
        
        layout.addLayout(button_layout)
