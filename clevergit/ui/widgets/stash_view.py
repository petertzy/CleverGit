"""
Stash view widget.
"""

from typing import TYPE_CHECKING, List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QSplitter,
    QMessageBox,
    QInputDialog,
    QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from clevergit.models.stash_info import StashInfo

if TYPE_CHECKING:
    from clevergit.ui.windows.main_window import MainWindow


class StashView(QWidget):
    """Display and manage stashes."""
    
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.main_window = main_window
        
        # Main layout with splitter
        layout = QVBoxLayout()
        
        # Top button bar
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("💾 Save Stash")
        save_button.clicked.connect(self._save_stash)
        button_layout.addWidget(save_button)
        
        apply_button = QPushButton("📥 Apply")
        apply_button.clicked.connect(self._apply_stash)
        button_layout.addWidget(apply_button)
        
        pop_button = QPushButton("↩️ Pop")
        pop_button.clicked.connect(self._pop_stash)
        button_layout.addWidget(pop_button)
        
        drop_button = QPushButton("🗑️ Drop")
        drop_button.clicked.connect(self._drop_stash)
        button_layout.addWidget(drop_button)
        
        clear_button = QPushButton("🧹 Clear All")
        clear_button.clicked.connect(self._clear_stashes)
        button_layout.addWidget(clear_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Splitter for list and preview
        splitter = QSplitter(Qt.Vertical)
        
        # Stash list
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("Stash List"))
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_stash_selected)
        self.list_widget.itemDoubleClicked.connect(self._on_stash_double_clicked)
        list_layout.addWidget(self.list_widget)
        
        list_widget.setLayout(list_layout)
        splitter.addWidget(list_widget)
        
        # Preview area
        preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(QLabel("Stash Preview (Diff)"))
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Courier", 10))
        preview_layout.addWidget(self.preview_text)
        
        preview_widget.setLayout(preview_layout)
        splitter.addWidget(preview_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def update_stashes(self, stashes: List[StashInfo]) -> None:
        """Update stash list display."""
        self.list_widget.clear()
        self.preview_text.clear()
        
        for stash in stashes:
            item = QListWidgetItem(stash.format_oneline())
            item.setData(Qt.UserRole, stash.index)
            self.list_widget.addItem(item)
    
    def _on_stash_selected(self, item: QListWidgetItem) -> None:
        """Handle stash selection to show preview."""
        stash_index = item.data(Qt.UserRole)
        
        if self.main_window.repo:
            try:
                diff_content = self.main_window.repo.stash_show(stash_index)
                self.preview_text.setPlainText(diff_content)
            except Exception as e:
                self.preview_text.setPlainText(f"Error loading stash preview:\n{str(e)}")
    
    def _on_stash_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click to apply stash."""
        self._apply_stash()
    
    def _save_stash(self) -> None:
        """Save current changes to stash."""
        if not self.main_window.repo:
            return
        
        # Ask for stash message
        message, ok = QInputDialog.getText(
            self,
            "Save Stash",
            "Enter stash message (optional):"
        )
        
        if ok:
            try:
                # Check if there are changes to stash
                if self.main_window.repo.is_clean():
                    QMessageBox.information(
                        self,
                        "No Changes",
                        "There are no changes to stash."
                    )
                    return
                
                # Save stash
                self.main_window.repo.stash_save(
                    message=message if message else None,
                    include_untracked=True
                )
                
                # Refresh the view
                self.main_window._refresh()
                QMessageBox.information(self, "Success", "Stash saved successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save stash:\n{e}")
    
    def _apply_stash(self) -> None:
        """Apply selected stash without removing it."""
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Select a stash to apply")
            return
        
        stash_index = item.data(Qt.UserRole)
        
        if self.main_window.repo:
            try:
                self.main_window.repo.stash_apply(stash_index)
                self.main_window._refresh()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Stash stash@{{{stash_index}}} applied successfully"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to apply stash:\n{e}")
    
    def _pop_stash(self) -> None:
        """Apply selected stash and remove it."""
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Select a stash to pop")
            return
        
        stash_index = item.data(Qt.UserRole)
        
        if self.main_window.repo:
            try:
                self.main_window.repo.stash_pop(stash_index)
                self.main_window._refresh()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Stash stash@{{{stash_index}}} popped successfully"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to pop stash:\n{e}")
    
    def _drop_stash(self) -> None:
        """Delete selected stash."""
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Select a stash to drop")
            return
        
        stash_index = item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Drop",
            f"Drop stash@{{{stash_index}}}?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.main_window.repo:
                try:
                    self.main_window.repo.stash_drop(stash_index)
                    self.main_window._refresh()
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Stash stash@{{{stash_index}}} dropped successfully"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to drop stash:\n{e}")
    
    def _clear_stashes(self) -> None:
        """Clear all stashes."""
        if not self.main_window.repo:
            return
        
        stashes = self.main_window.repo.stash_list()
        if not stashes:
            QMessageBox.information(self, "No Stashes", "There are no stashes to clear.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Clear All",
            f"Clear all {len(stashes)} stashes?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.main_window.repo.stash_clear()
                self.main_window._refresh()
                QMessageBox.information(self, "Success", "All stashes cleared successfully")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear stashes:\n{e}")
