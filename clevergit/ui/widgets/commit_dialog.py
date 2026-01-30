"""
Commit dialog widget.
"""

from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QCheckBox, QMessageBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from clevergit.core.repo import Repo


class CommitDialog(QDialog):
    """Dialog for creating a new commit."""
    
    def __init__(self, parent, repo: "Repo") -> None:
        super().__init__(parent)
        self.repo = repo
        
        self.setWindowTitle("Create Commit")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        # File status display
        layout.addWidget(QLabel("Files to commit:"))
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        
        try:
            status = repo.status()
            for file in status.modified:
                item = QListWidgetItem(f"M  {file}")
                self.file_list.addItem(item)
            for file in status.untracked:
                item = QListWidgetItem(f"?  {file}")
                self.file_list.addItem(item)
        except Exception:
            pass
        
        layout.addWidget(self.file_list)
        
        # Commit message
        layout.addWidget(QLabel("Commit message:"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter commit message...")
        layout.addWidget(self.message_input)
        
        # Options
        self.commit_all_checkbox = QCheckBox("Commit all changes")
        self.commit_all_checkbox.setChecked(True)
        layout.addWidget(self.commit_all_checkbox)
        
        self.allow_empty_checkbox = QCheckBox("Allow empty commit")
        layout.addWidget(self.allow_empty_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        commit_button = QPushButton("Commit")
        commit_button.clicked.connect(self._on_commit)
        button_layout.addWidget(commit_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _on_commit(self) -> None:
        """Handle commit button click."""
        message = self.message_input.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(self, "Warning", "Commit message cannot be empty")
            return
        
        try:
            if self.commit_all_checkbox.isChecked():
                self.repo.commit_all(
                    message,
                    allow_empty=self.allow_empty_checkbox.isChecked()
                )
            else:
                # TODO: Implement selective commit
                QMessageBox.information(self, "Info", "Selective commit not yet implemented")
                return
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create commit:\n{e}")
