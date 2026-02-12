"""Base theme class."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Theme:
    """Base theme class with color definitions."""

    name: str
    # Background colors
    background: str
    background_secondary: str
    background_hover: str

    # Text colors
    text: str
    text_secondary: str
    text_disabled: str

    # Button colors
    button_primary: str
    button_success: str
    button_warning: str
    button_danger: str
    button_info: str

    # Diff colors
    diff_added: str
    diff_removed: str
    diff_modified: str
    diff_context: str

    # Graph colors
    graph_colors: list

    # Border and separator colors
    border: str
    separator: str

    # Status colors
    status_success: str
    status_warning: str
    status_error: str
    status_info: str

    # Selection colors
    selection_background: str
    selection_text: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert theme to dictionary."""
        return {
            "name": self.name,
            "background": self.background,
            "background_secondary": self.background_secondary,
            "background_hover": self.background_hover,
            "text": self.text,
            "text_secondary": self.text_secondary,
            "text_disabled": self.text_disabled,
            "button_primary": self.button_primary,
            "button_success": self.button_success,
            "button_warning": self.button_warning,
            "button_danger": self.button_danger,
            "button_info": self.button_info,
            "diff_added": self.diff_added,
            "diff_removed": self.diff_removed,
            "diff_modified": self.diff_modified,
            "diff_context": self.diff_context,
            "graph_colors": self.graph_colors,
            "border": self.border,
            "separator": self.separator,
            "status_success": self.status_success,
            "status_warning": self.status_warning,
            "status_error": self.status_error,
            "status_info": self.status_info,
            "selection_background": self.selection_background,
            "selection_text": self.selection_text,
        }

    def get_stylesheet(self) -> str:
        """Generate QSS stylesheet for this theme."""
        return f"""
            QWidget {{
                background-color: {self.background};
                color: {self.text};
            }}
            
            QMainWindow {{
                background-color: {self.background};
            }}
            
            QPushButton {{
                background-color: {self.button_primary};
                color: white;
                border: 1px solid {self.border};
                padding: 5px 15px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {self.background_hover};
            }}
            
            QPushButton:disabled {{
                background-color: {self.background_secondary};
                color: {self.text_disabled};
            }}
            
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {self.background_secondary};
                color: {self.text};
                border: 1px solid {self.border};
                padding: 3px;
                border-radius: 2px;
            }}
            
            QTreeView, QListView, QTableView {{
                background-color: {self.background};
                color: {self.text};
                border: 1px solid {self.border};
                alternate-background-color: {self.background_secondary};
            }}
            
            QTreeView::item:selected, QListView::item:selected, QTableView::item:selected {{
                background-color: {self.selection_background};
                color: {self.selection_text};
            }}
            
            QTreeView::item:hover, QListView::item:hover, QTableView::item:hover {{
                background-color: {self.background_hover};
            }}
            
            QMenuBar {{
                background-color: {self.background_secondary};
                color: {self.text};
            }}
            
            QMenuBar::item:selected {{
                background-color: {self.background_hover};
            }}
            
            QMenu {{
                background-color: {self.background};
                color: {self.text};
                border: 1px solid {self.border};
            }}
            
            QMenu::item:selected {{
                background-color: {self.selection_background};
            }}
            
            QToolBar {{
                background-color: {self.background_secondary};
                border: none;
                spacing: 3px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {self.border};
                background-color: {self.background};
            }}
            
            QTabBar::tab {{
                background-color: {self.background_secondary};
                color: {self.text};
                padding: 5px 10px;
                border: 1px solid {self.border};
            }}
            
            QTabBar::tab:selected {{
                background-color: {self.background};
                border-bottom-color: {self.background};
            }}
            
            QStatusBar {{
                background-color: {self.background_secondary};
                color: {self.text_secondary};
            }}
            
            QScrollBar:vertical {{
                background-color: {self.background_secondary};
                width: 12px;
                border: none;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {self.border};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {self.background_secondary};
                height: 12px;
                border: none;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {self.border};
                border-radius: 6px;
                min-width: 20px;
            }}
        """
