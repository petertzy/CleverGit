"""
Branch view widget.
"""

from typing import TYPE_CHECKING, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from clevergit.models.branch_info import BranchInfo

if TYPE_CHECKING:
    from clevergit.ui.windows.main_window import MainWindow


class BranchView(QWidget):
    """Display and manage branches."""
    
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.main_window = main_window
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_branch_double_clicked)
        
        button_layout = QHBoxLayout()
        
        new_button = QPushButton("New Branch")
        new_button.clicked.connect(self._new_branch)
        button_layout.addWidget(new_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._delete_branch)
        button_layout.addWidget(delete_button)
        
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_branches(self, branches: List[BranchInfo]) -> None:
        """Update branch list display."""
        self.list_widget.clear()
        
        for branch in branches:
            item = QListWidgetItem(branch.name)
            
            # Highlight current branch
            if branch.is_current:
                item.setBackground(QBrush(QColor(100, 150, 200)))
                item.setText(f"→ {branch.name} (current)")
            
            # Mark remote branches
            if branch.is_remote:
                item.setText(f"  {branch.name} (remote)")
                item.setForeground(QBrush(QColor(150, 150, 150)))
            
            self.list_widget.addItem(item)
    
    def _on_branch_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle branch double-click to switch."""
        branch_name = item.text().replace("→ ", "").replace(" (current)", "").strip()
        
        if self.main_window.repo:
            try:
                self.main_window.repo.checkout(branch_name)
                self.main_window._refresh()
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self.main_window, "Error", f"Failed to switch branch:\n{e}")
    
    def _new_branch(self) -> None:
        """Create new branch dialog."""
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        
        name, ok = QInputDialog.getText(self, "New Branch", "Branch name:")
        if ok and name:
            if self.main_window.repo:
                try:
                    self.main_window.repo.create_branch(name)
                    self.main_window._refresh()
                    QMessageBox.information(self.main_window, "Success", f"Branch '{name}' created")
                except Exception as e:
                    QMessageBox.critical(self.main_window, "Error", f"Failed to create branch:\n{e}")
    
    def _delete_branch(self) -> None:
        """Delete selected branch."""
        from PySide6.QtWidgets import QMessageBox
        
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Select a branch to delete")
            return
        
        branch_name = item.text().replace("→ ", "").replace(" (current)", "").strip()
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete branch '{branch_name}'?"
        )
        
        if reply == QMessageBox.Yes:
            # TODO: Implement branch deletion in core module
            QMessageBox.information(self, "Info", "Branch deletion not yet implemented")
