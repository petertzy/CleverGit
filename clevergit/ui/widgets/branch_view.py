"""
Branch view widget.
"""

from typing import TYPE_CHECKING, List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from clevergit.models.branch_info import BranchInfo

if TYPE_CHECKING:
    from clevergit.ui.widgets.repository_tab import RepositoryTab


class BranchView(QWidget):
    """Display and manage branches."""
    
    def __init__(self, repository_tab: "RepositoryTab") -> None:
        super().__init__()
        self.repository_tab = repository_tab
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_branch_double_clicked)
        
        button_layout = QHBoxLayout()
        
        new_button = QPushButton("New Branch")
        new_button.clicked.connect(self._new_branch)
        button_layout.addWidget(new_button)
        
        compare_button = QPushButton("Compare")
        compare_button.clicked.connect(self._compare_branches)
        button_layout.addWidget(compare_button)
        
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
        
        if self.repository_tab.repo:
            try:
                self.repository_tab.repo.checkout(branch_name)
                
                # Save the branch change to settings
                self.repository_tab.save_branch_to_settings(branch_name)
                
                self.repository_tab.refresh()
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self.repository_tab, "Error", f"Failed to switch branch:\n{e}")
    
    def _new_branch(self) -> None:
        """Create new branch dialog."""
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        
        name, ok = QInputDialog.getText(self, "New Branch", "Branch name:")
        if ok and name:
            if self.repository_tab.repo:
                try:
                    self.repository_tab.repo.create_branch(name)
                    self.repository_tab.refresh()
                    QMessageBox.information(self.repository_tab, "Success", f"Branch '{name}' created")
                except Exception as e:
                    QMessageBox.critical(self.repository_tab, "Error", f"Failed to create branch:\n{e}")
    
    def _delete_branch(self) -> None:
        """Delete selected branch."""
        from PySide6.QtWidgets import QMessageBox
        
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Select a branch to delete")
            return
        
        # Extract branch name from display text
        branch_name = item.text().replace("→ ", "").replace(" (current)", "").replace(" (remote)", "").strip()
        
        # Don't allow deleting current or remote branches
        if "(current)" in item.text():
            QMessageBox.warning(self, "Warning", "Cannot delete the current branch")
            return
        
        if "(remote)" in item.text():
            QMessageBox.warning(self, "Warning", "Cannot delete remote branches from this interface")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete branch '{branch_name}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.repository_tab.repo:
                try:
                    self.repository_tab.repo.delete_branch(branch_name, force=False)
                    self.repository_tab.refresh()
                    QMessageBox.information(self.repository_tab, "Success", f"Branch '{branch_name}' deleted")
                except Exception as e:
                    error_msg = str(e)
                    # Check if branch is not fully merged
                    if "not fully merged" in error_msg or "is not fully merged" in error_msg:
                        force_reply = QMessageBox.question(
                            self,
                            "Branch Not Merged",
                            f"Branch '{branch_name}' is not fully merged.\n\n"
                            "Deleting it will permanently lose any unmerged commits.\n\n"
                            "Do you want to force delete it?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        
                        if force_reply == QMessageBox.Yes:
                            try:
                                self.repository_tab.repo.delete_branch(branch_name, force=True)
                                self.repository_tab.refresh()
                                QMessageBox.information(self.repository_tab, "Success", f"Branch '{branch_name}' force deleted")
                            except Exception as e2:
                                QMessageBox.critical(self.repository_tab, "Error", f"Failed to force delete:\n{e2}")
                    else:
                        QMessageBox.critical(self.repository_tab, "Error", f"Failed to delete branch:\n{error_msg}")
    
    def _compare_branches(self) -> None:
        """Open branch comparison dialog."""
        from clevergit.ui.widgets.branch_compare_dialog import BranchCompareDialog
        
        if self.repository_tab.repo:
            try:
                dialog = BranchCompareDialog(self.repository_tab, self.repository_tab.repo)
                dialog.exec()
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self.repository_tab, "Error", f"Failed to open branch comparison:\n{e}")

