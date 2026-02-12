"""
Tag view widget.
"""

from typing import TYPE_CHECKING, List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QInputDialog,
    QMessageBox,
    QDialog,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDialogButtonBox,
    QCheckBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from clevergit.models.tag_info import TagInfo

if TYPE_CHECKING:
    from clevergit.ui.windows.main_window import MainWindow


class CreateTagDialog(QDialog):
    """Dialog for creating a new tag."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Tag")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Tag name
        name_label = QLabel("Tag name:")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        
        # Annotated tag checkbox
        self.annotated_checkbox = QCheckBox("Create annotated tag")
        self.annotated_checkbox.stateChanged.connect(self._on_annotated_changed)
        layout.addWidget(self.annotated_checkbox)
        
        # Message (for annotated tags)
        self.message_label = QLabel("Tag message:")
        self.message_label.setVisible(False)
        layout.addWidget(self.message_label)
        
        self.message_input = QTextEdit()
        self.message_input.setVisible(False)
        self.message_input.setMaximumHeight(100)
        layout.addWidget(self.message_input)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def _on_annotated_changed(self, state):
        """Toggle message input visibility based on annotated checkbox."""
        is_annotated = state == Qt.Checked
        self.message_label.setVisible(is_annotated)
        self.message_input.setVisible(is_annotated)
    
    def get_tag_info(self):
        """Get tag information from dialog."""
        return {
            "name": self.name_input.text(),
            "is_annotated": self.annotated_checkbox.isChecked(),
            "message": self.message_input.toPlainText() if self.annotated_checkbox.isChecked() else None,
        }


class TagView(QWidget):
    """Display and manage tags."""
    
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.main_window = main_window
        
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_tag_double_clicked)
        
        button_layout = QHBoxLayout()
        
        new_button = QPushButton("New Tag")
        new_button.clicked.connect(self._new_tag)
        button_layout.addWidget(new_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self._delete_tag)
        button_layout.addWidget(delete_button)
        
        push_button = QPushButton("Push")
        push_button.clicked.connect(self._push_tag)
        button_layout.addWidget(push_button)
        
        push_all_button = QPushButton("Push All")
        push_all_button.clicked.connect(self._push_all_tags)
        button_layout.addWidget(push_all_button)
        
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_tags(self, tags: List[TagInfo]) -> None:
        """Update tag list display."""
        self.list_widget.clear()
        
        for tag in tags:
            # Format display text
            if tag.is_annotated:
                display_text = f"🏷️ {tag.name} (annotated) -> {tag.short_sha}"
            else:
                display_text = f"  {tag.name} (lightweight) -> {tag.short_sha}"
            
            item = QListWidgetItem(display_text)
            
            # Color code annotated tags
            if tag.is_annotated:
                item.setForeground(QBrush(QColor(100, 150, 255)))
            
            # Store tag name in item data for later retrieval
            item.setData(Qt.UserRole, tag.name)
            
            self.list_widget.addItem(item)
    
    def _on_tag_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle tag double-click to show details."""
        tag_name = item.data(Qt.UserRole)
        
        if self.main_window.repo:
            try:
                tags = self.main_window.repo.list_tags()
                selected_tag = None
                
                for tag in tags:
                    if tag.name == tag_name:
                        selected_tag = tag
                        break
                
                if selected_tag:
                    details = f"Tag: {selected_tag.name}\n"
                    details += f"Commit: {selected_tag.commit_sha}\n"
                    details += f"Type: {'Annotated' if selected_tag.is_annotated else 'Lightweight'}\n"
                    
                    if selected_tag.is_annotated:
                        if selected_tag.tagger:
                            details += f"Tagger: {selected_tag.tagger}\n"
                        if selected_tag.date:
                            details += f"Date: {selected_tag.date}\n"
                        if selected_tag.message:
                            details += f"\nMessage:\n{selected_tag.message}"
                    
                    QMessageBox.information(self, "Tag Details", details)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to get tag details:\n{e}")
    
    def _new_tag(self) -> None:
        """Create new tag dialog."""
        dialog = CreateTagDialog(self)
        
        if dialog.exec() == QDialog.Accepted:
            tag_info = dialog.get_tag_info()
            name = tag_info["name"]
            
            if not name:
                QMessageBox.warning(self, "Warning", "Tag name cannot be empty")
                return
            
            if self.main_window.repo:
                try:
                    if tag_info["is_annotated"]:
                        message = tag_info["message"]
                        if not message:
                            QMessageBox.warning(self, "Warning", "Message is required for annotated tags")
                            return
                        self.main_window.repo.create_annotated_tag(name, message)
                        QMessageBox.information(self, "Success", f"Annotated tag '{name}' created")
                    else:
                        self.main_window.repo.create_tag(name)
                        QMessageBox.information(self, "Success", f"Lightweight tag '{name}' created")
                    
                    self.main_window._refresh()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create tag:\n{e}")
    
    def _delete_tag(self) -> None:
        """Delete selected tag."""
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Select a tag to delete")
            return
        
        tag_name = item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete tag '{tag_name}'?\n\nThis will only delete the local tag. "
            "To delete from remote, you need to push the deletion separately.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.main_window.repo:
                try:
                    self.main_window.repo.delete_tag(tag_name)
                    self.main_window._refresh()
                    QMessageBox.information(self, "Success", f"Tag '{tag_name}' deleted")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete tag:\n{e}")
    
    def _push_tag(self) -> None:
        """Push selected tag to remote."""
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Warning", "Select a tag to push")
            return
        
        tag_name = item.data(Qt.UserRole)
        
        if self.main_window.repo:
            try:
                self.main_window.repo.push_tag(tag_name)
                QMessageBox.information(self, "Success", f"Tag '{tag_name}' pushed to remote")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to push tag:\n{e}")
    
    def _push_all_tags(self) -> None:
        """Push all tags to remote."""
        reply = QMessageBox.question(
            self,
            "Confirm Push All Tags",
            "Push all tags to remote?\n\nThis will push all local tags that don't exist on the remote.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.main_window.repo:
                try:
                    self.main_window.repo.push_all_tags()
                    QMessageBox.information(self, "Success", "All tags pushed to remote")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to push tags:\n{e}")
