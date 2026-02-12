"""
Cherry-pick dialog widget.
"""

from typing import TYPE_CHECKING, List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QMessageBox, QTextEdit, QSplitter, QWidget
)
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from clevergit.core.repo import Repo


class CherryPickDialog(QDialog):
    """Dialog for cherry-picking commits."""
    
    def __init__(self, parent, repo: "Repo", commits: Optional[List[dict]] = None) -> None:
        """
        Initialize cherry-pick dialog.
        
        Args:
            parent: Parent widget
            repo: Repository instance
            commits: List of commit dicts with 'sha', 'message', 'author', 'date' keys.
                    If None, will load recent commits from the repository.
        """
        super().__init__(parent)
        self.repo = repo
        self.selected_commits: List[str] = []
        
        self.setWindowTitle("Cherry-Pick Commits")
        self.setGeometry(100, 100, 700, 500)
        
        layout = QVBoxLayout()
        
        # Instructions
        layout.addWidget(QLabel("Select one or more commits to cherry-pick onto the current branch:"))
        
        # Create splitter for commits list and details
        splitter = QSplitter(Qt.Vertical)
        
        # Commits list
        self.commits_list = QListWidget()
        self.commits_list.setSelectionMode(QListWidget.MultiSelection)
        self.commits_list.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Load commits
        if commits is None:
            try:
                commits = repo.client.log(max_count=50)
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Failed to load commits: {e}")
                commits = []
        
        # Populate commits list
        self.commit_data = {}
        for commit in commits:
            sha = commit.get("sha", "")
            message = commit.get("message", "").split("\n")[0]  # First line only
            author = commit.get("author", "")
            date = commit.get("date", "")
            
            # Format display text
            display_text = f"{sha[:8]} - {message} ({author})"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, sha)  # Store full SHA in item data
            self.commits_list.addItem(item)
            
            # Store full commit info
            self.commit_data[sha] = commit
        
        splitter.addWidget(self.commits_list)
        
        # Commit details view
        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel("Commit Details:"))
        self.details_view = QTextEdit()
        self.details_view.setReadOnly(True)
        self.details_view.setMaximumHeight(150)
        details_layout.addWidget(self.details_view)
        
        details_container = QWidget()
        details_container.setLayout(details_layout)
        splitter.addWidget(details_container)
        
        layout.addWidget(splitter)
        
        # Options
        info_label = QLabel("Note: Commits will be cherry-picked in the order selected.")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cherry_pick_button = QPushButton("Cherry-Pick")
        self.cherry_pick_button.clicked.connect(self._on_cherry_pick)
        self.cherry_pick_button.setEnabled(False)
        button_layout.addWidget(self.cherry_pick_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _on_selection_changed(self) -> None:
        """Handle commit selection change."""
        selected_items = self.commits_list.selectedItems()
        self.cherry_pick_button.setEnabled(len(selected_items) > 0)
        
        # Update details view
        if len(selected_items) == 1:
            sha = selected_items[0].data(Qt.UserRole)
            commit = self.commit_data.get(sha, {})
            
            details = f"SHA: {sha}\n"
            details += f"Author: {commit.get('author', 'Unknown')}\n"
            details += f"Date: {commit.get('date', 'Unknown')}\n"
            details += f"\nMessage:\n{commit.get('message', 'No message')}"
            
            self.details_view.setPlainText(details)
        elif len(selected_items) > 1:
            self.details_view.setPlainText(f"{len(selected_items)} commits selected")
        else:
            self.details_view.setPlainText("No commit selected")
    
    def _on_cherry_pick(self) -> None:
        """Handle cherry-pick button click."""
        selected_items = self.commits_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select at least one commit to cherry-pick")
            return
        
        # Get SHAs in selection order (top to bottom)
        commit_shas = []
        for i in range(self.commits_list.count()):
            item = self.commits_list.item(i)
            if item.isSelected():
                sha = item.data(Qt.UserRole)
                commit_shas.append(sha)
        
        # Confirm action
        if len(commit_shas) == 1:
            message = f"Cherry-pick commit {commit_shas[0][:8]}?"
        else:
            message = f"Cherry-pick {len(commit_shas)} commits?"
        
        reply = QMessageBox.question(
            self,
            "Confirm Cherry-Pick",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Perform cherry-pick
        try:
            from clevergit.core.cherry_pick import cherry_pick
            
            for sha in commit_shas:
                try:
                    cherry_pick(self.repo.path, sha)
                except Exception as e:
                    # Check if it's a conflict
                    from clevergit.core.cherry_pick import is_cherry_picking
                    
                    if is_cherry_picking(self.repo.path):
                        error_msg = f"Cherry-pick conflict detected for commit {sha[:8]}.\n\n"
                        error_msg += "Resolve conflicts manually, then:\n"
                        error_msg += "- Use 'git cherry-pick --continue' to continue\n"
                        error_msg += "- Use 'git cherry-pick --abort' to abort\n\n"
                        error_msg += f"Error: {e}"
                        QMessageBox.warning(self, "Cherry-Pick Conflict", error_msg)
                        self.reject()
                        return
                    else:
                        raise
            
            self.selected_commits = commit_shas
            QMessageBox.information(
                self,
                "Success",
                f"Successfully cherry-picked {len(commit_shas)} commit(s)"
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to cherry-pick:\n{e}")
