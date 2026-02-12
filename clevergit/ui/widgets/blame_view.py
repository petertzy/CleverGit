"""
Blame view widget for displaying line-by-line blame information.
"""

from typing import List, Optional, Callable
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from clevergit.models.blame_info import BlameInfo


class BlameView(QWidget):
    """Display blame information for a file."""
    
    # Signal emitted when user clicks on a commit
    commit_clicked = Signal(str)  # Emits commit SHA
    # Signal emitted when user wants to refresh
    refresh_requested = Signal(str)  # Emits file path
    
    def __init__(self) -> None:
        super().__init__()
        self._blame_data: List[BlameInfo] = []
        self._file_path: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the UI layout."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header with file path
        header_layout = QHBoxLayout()
        
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.file_label)
        
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self._on_refresh)
        self.refresh_button.setEnabled(False)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table for blame information
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Line",
            "Commit",
            "Author",
            "Date",
            "Content"
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Make table read-only and enable selection
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Connect cell click to commit details
        self.table.cellClicked.connect(self._on_cell_clicked)
        
        # Use monospace font for content column
        mono_font = QFont("Courier New")
        mono_font.setPointSize(9)
        
        layout.addWidget(self.table)
        
        # Status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
    
    def update_blame(self, blame_data: List[BlameInfo], file_path: str) -> None:
        """
        Update the blame view with new data.
        
        Args:
            blame_data: List of BlameInfo objects
            file_path: Path to the file being blamed
        """
        self._blame_data = blame_data
        self._file_path = file_path
        
        # Update header
        self.file_label.setText(f"Blame: {file_path}")
        self.refresh_button.setEnabled(True)
        
        # Clear and populate table
        self.table.setRowCount(len(blame_data))
        
        mono_font = QFont("Courier New")
        mono_font.setPointSize(9)
        
        for row, blame in enumerate(blame_data):
            # Line number
            line_item = QTableWidgetItem(str(blame.line_number))
            line_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 0, line_item)
            
            # Commit SHA (clickable)
            commit_item = QTableWidgetItem(blame.short_sha)
            commit_item.setForeground(Qt.GlobalColor.blue)
            commit_item.setToolTip(f"{blame.commit_sha}\n{blame.summary}")
            self.table.setItem(row, 1, commit_item)
            
            # Author
            author_item = QTableWidgetItem(blame.author)
            author_item.setToolTip(blame.author_email)
            self.table.setItem(row, 2, author_item)
            
            # Date
            date_str = blame.date.strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(date_str)
            self.table.setItem(row, 3, date_item)
            
            # Content
            content_item = QTableWidgetItem(blame.content)
            content_item.setFont(mono_font)
            self.table.setItem(row, 4, content_item)
        
        # Update status
        self.status_label.setText(f"Showing {len(blame_data)} lines")
    
    def clear(self) -> None:
        """Clear the blame view."""
        self._blame_data = []
        self._file_path = None
        self.table.setRowCount(0)
        self.file_label.setText("No file loaded")
        self.status_label.setText("")
        self.refresh_button.setEnabled(False)
    
    def _on_cell_clicked(self, row: int, column: int) -> None:
        """Handle cell click - emit commit signal when commit column is clicked."""
        if 0 <= row < len(self._blame_data):
            blame = self._blame_data[row]
            # Emit commit signal for any column click in the row
            self.commit_clicked.emit(blame.commit_sha)
    
    def _on_refresh(self) -> None:
        """Handle refresh button click."""
        # Re-fetch blame information for the current file
        if self._file_path:
            # Emit signal so parent can refresh the data
            self.refresh_requested.emit(self._file_path)
    
    def get_current_file(self) -> Optional[str]:
        """Get the currently displayed file path."""
        return self._file_path
    
    def get_blame_at_line(self, line_number: int) -> Optional[BlameInfo]:
        """
        Get blame information for a specific line.
        
        Args:
            line_number: Line number (1-indexed)
            
        Returns:
            BlameInfo object or None if not found
        """
        for blame in self._blame_data:
            if blame.line_number == line_number:
                return blame
        return None
