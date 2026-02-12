"""
File status view widget.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt
from clevergit.models.file_status import FileStatusList


class StatusView(QWidget):
    """Display file status in tree view."""
    
    def __init__(self) -> None:
        super().__init__()
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["File Status"])
        self.tree.setColumnCount(1)
        
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)
    
    def update_status(self, status: FileStatusList) -> None:
        """Update file status display."""
        self.tree.clear()
        
        # Modified files
        if status.modified:
            modified_item = QTreeWidgetItem(["Modified Files"])
            modified_item.setForeground(0, Qt.yellow)
            for file in status.modified:
                QTreeWidgetItem(modified_item, [file])
            self.tree.addTopLevelItem(modified_item)
            modified_item.setExpanded(True)
        
        # Untracked files
        if status.untracked:
            untracked_item = QTreeWidgetItem(["Untracked Files"])
            untracked_item.setForeground(0, Qt.red)
            for file in status.untracked:
                QTreeWidgetItem(untracked_item, [file])
            self.tree.addTopLevelItem(untracked_item)
            untracked_item.setExpanded(True)
        
        # Staged files
        if status.staged:
            staged_item = QTreeWidgetItem(["Staged Files"])
            staged_item.setForeground(0, Qt.green)
            for file in status.staged:
                QTreeWidgetItem(staged_item, [file])
            self.tree.addTopLevelItem(staged_item)
            staged_item.setExpanded(True)
        
        # Conflicted files
        if status.conflicted:
            conflict_item = QTreeWidgetItem(["Conflicted Files"])
            conflict_item.setForeground(0, Qt.red)
            for file in status.conflicted:
                QTreeWidgetItem(conflict_item, [file])
            self.tree.addTopLevelItem(conflict_item)
            conflict_item.setExpanded(True)
