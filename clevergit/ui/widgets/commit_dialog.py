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
        layout.addWidget(QLabel("Files to commit (select specific files or use 'Commit all changes'):"))
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        
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
                # Get selected files
                selected_items = self.file_list.selectedItems()
                if not selected_items:
                    QMessageBox.warning(self, "Warning", "Please select files to commit or use 'Commit all changes'")
                    return
                
                # Extract file paths from list items (remove status prefix like "M  " or "?  ")
                selected_files = []
                for item in selected_items:
                    file_text = item.text()
                    # Status format is typically "X  filename" where X is status code
                    # Split on whitespace and take everything after the first token
                    parts = file_text.split(None, 1)  # Split on whitespace, max 1 split
                    if len(parts) >= 2:
                        file_path = parts[1]
                        selected_files.append(file_path)
                
                if not selected_files:
                    QMessageBox.warning(self, "Warning", "No valid files selected")
                    return
                
                # Commit selected files
                self.repo.commit_files(selected_files, message)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create commit:\n{e}")
