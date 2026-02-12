"""
Keyboard shortcuts help dialog for CleverGit GUI.
"""

from typing import Optional, Dict
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QTabWidget,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence

from clevergit.ui.shortcuts import ShortcutManager


class ShortcutHelpDialog(QDialog):
    """Dialog to display and customize keyboard shortcuts."""
    
    def __init__(self, shortcut_manager: ShortcutManager, parent: Optional[QWidget] = None) -> None:
        """
        Initialize shortcuts help dialog.
        
        Args:
            shortcut_manager: ShortcutManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.shortcut_manager = shortcut_manager
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumSize(700, 500)
        
        self._setup_ui()
        self._load_shortcuts()
    
    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # View tab - display shortcuts
        view_tab = QWidget()
        view_layout = QVBoxLayout()
        view_tab.setLayout(view_layout)
        
        view_layout.addWidget(QLabel("Available keyboard shortcuts:"))
        
        self.view_table = QTableWidget()
        self.view_table.setColumnCount(3)
        self.view_table.setHorizontalHeaderLabels(["Category", "Action", "Shortcut"])
        self.view_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.view_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.view_table.setSelectionBehavior(QTableWidget.SelectRows)
        view_layout.addWidget(self.view_table)
        
        tab_widget.addTab(view_tab, "View Shortcuts")
        
        # Customize tab - edit shortcuts
        customize_tab = QWidget()
        customize_layout = QVBoxLayout()
        customize_tab.setLayout(customize_layout)
        
        customize_layout.addWidget(QLabel("Customize keyboard shortcuts:"))
        
        self.customize_table = QTableWidget()
        self.customize_table.setColumnCount(4)
        self.customize_table.setHorizontalHeaderLabels(["Category", "Action", "Shortcut", "Actions"])
        self.customize_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.customize_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customize_table.setSelectionBehavior(QTableWidget.SelectRows)
        customize_layout.addWidget(self.customize_table)
        
        # Reset all button
        reset_all_btn = QPushButton("Reset All to Defaults")
        reset_all_btn.clicked.connect(self._reset_all_shortcuts)
        customize_layout.addWidget(reset_all_btn)
        
        tab_widget.addTab(customize_tab, "Customize")
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _load_shortcuts(self) -> None:
        """Load shortcuts into the tables."""
        shortcuts_by_category = self.shortcut_manager.get_shortcuts_by_category()
        
        # Populate view table
        self._populate_view_table(shortcuts_by_category)
        
        # Populate customize table
        self._populate_customize_table(shortcuts_by_category)
    
    def _populate_view_table(self, shortcuts_by_category: Dict) -> None:
        """Populate the view shortcuts table."""
        self.view_table.setRowCount(0)
        
        row = 0
        for category, shortcuts in sorted(shortcuts_by_category.items()):
            for action_id, data in sorted(shortcuts.items(), key=lambda x: x[1]['description']):
                self.view_table.insertRow(row)
                
                self.view_table.setItem(row, 0, QTableWidgetItem(category))
                self.view_table.setItem(row, 1, QTableWidgetItem(data['description']))
                self.view_table.setItem(row, 2, QTableWidgetItem(data['shortcut']))
                
                row += 1
    
    def _populate_customize_table(self, shortcuts_by_category: Dict) -> None:
        """Populate the customize shortcuts table."""
        self.customize_table.setRowCount(0)
        
        row = 0
        for category, shortcuts in sorted(shortcuts_by_category.items()):
            for action_id, data in sorted(shortcuts.items(), key=lambda x: x[1]['description']):
                self.customize_table.insertRow(row)
                
                self.customize_table.setItem(row, 0, QTableWidgetItem(category))
                self.customize_table.setItem(row, 1, QTableWidgetItem(data['description']))
                self.customize_table.setItem(row, 2, QTableWidgetItem(data['shortcut']))
                
                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(4, 2, 4, 2)
                action_widget.setLayout(action_layout)
                
                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(lambda checked, aid=action_id: self._edit_shortcut(aid))
                action_layout.addWidget(edit_btn)
                
                reset_btn = QPushButton("Reset")
                reset_btn.clicked.connect(lambda checked, aid=action_id: self._reset_shortcut(aid))
                action_layout.addWidget(reset_btn)
                
                self.customize_table.setCellWidget(row, 3, action_widget)
                
                row += 1
    
    def _edit_shortcut(self, action_id: str) -> None:
        """
        Edit a keyboard shortcut.
        
        Args:
            action_id: Action identifier
        """
        from clevergit.ui.shortcuts import SHORTCUT_DESCRIPTIONS
        
        current_shortcut = self.shortcut_manager.get_shortcut(action_id)
        action_description = SHORTCUT_DESCRIPTIONS.get(action_id, action_id)
        
        # Create input dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Shortcut")
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        layout.addWidget(QLabel(f"Enter new shortcut for: {action_description}"))
        layout.addWidget(QLabel(f"Current: {current_shortcut}"))
        
        shortcut_input = QLineEdit()
        shortcut_input.setPlaceholderText("Press keys (e.g., Ctrl+Shift+S)")
        if current_shortcut:
            shortcut_input.setText(current_shortcut)
        layout.addWidget(shortcut_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            new_shortcut = shortcut_input.text().strip()
            
            # Validate shortcut
            key_sequence = QKeySequence(new_shortcut)
            if key_sequence.isEmpty() and new_shortcut:
                QMessageBox.warning(self, "Invalid Shortcut", "The entered shortcut is not valid.")
                return
            
            # Try to set the shortcut
            if self.shortcut_manager.set_shortcut(action_id, new_shortcut):
                QMessageBox.information(self, "Success", "Shortcut updated successfully!")
                self._load_shortcuts()
            else:
                QMessageBox.warning(self, "Conflict", "This shortcut conflicts with another action.")
    
    def _reset_shortcut(self, action_id: str) -> None:
        """
        Reset a shortcut to default.
        
        Args:
            action_id: Action identifier
        """
        reply = QMessageBox.question(
            self,
            "Reset Shortcut",
            f"Reset shortcut for '{action_id}' to default?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.shortcut_manager.reset_shortcut(action_id):
                QMessageBox.information(self, "Success", "Shortcut reset to default!")
                self._load_shortcuts()
            else:
                QMessageBox.warning(self, "Error", "Failed to reset shortcut.")
    
    def _reset_all_shortcuts(self) -> None:
        """Reset all shortcuts to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset All Shortcuts",
            "Reset all shortcuts to their default values?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.shortcut_manager.reset_all_shortcuts()
            QMessageBox.information(self, "Success", "All shortcuts reset to defaults!")
            self._load_shortcuts()
