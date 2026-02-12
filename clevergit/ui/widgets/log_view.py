"""
Commit log view widget.
"""

from typing import List, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt


class LogView(QWidget):
    """Display commit history log."""
    
    def __init__(self) -> None:
        super().__init__()
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Commit", "Author", "Date", "Message"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def update_log(self, commits: List[Any]) -> None:
        """Update commit log display."""
        self.table.setRowCount(len(commits))
        
        for row, commit in enumerate(commits):
            # Extract commit info - handle both CommitInfo objects and Git objects
            if hasattr(commit, 'short_sha'):
                # CommitInfo object from core/log.py
                commit_hash = commit.short_sha or "unknown"
                author = commit.author or "unknown"
                date = commit.date.strftime("%Y-%m-%d %H:%M") if commit.date else "unknown"
                message = commit.message.split('\n')[0] if commit.message else "unknown"
            else:
                # Raw Git object (GitPython)
                commit_hash = str(commit.hexsha[:7]) if hasattr(commit, 'hexsha') else "unknown"
                author_obj = commit.author if hasattr(commit, 'author') else None
                author = author_obj.name if author_obj and hasattr(author_obj, 'name') else str(author_obj) if author_obj else "unknown"
                date = commit.committed_datetime.strftime("%Y-%m-%d %H:%M") if hasattr(commit, 'committed_datetime') else "unknown"
                message = commit.message.split('\n')[0] if hasattr(commit, 'message') else "unknown"
            
            # Add to table
            self.table.setItem(row, 0, QTableWidgetItem(commit_hash))
            self.table.setItem(row, 1, QTableWidgetItem(author))
            self.table.setItem(row, 2, QTableWidgetItem(date))
            self.table.setItem(row, 3, QTableWidgetItem(message))
