"""
Main application window for CleverGit GUI.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QPushButton, QFileDialog, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from clevergit.core.repo import Repo
from clevergit.git.errors import RepoNotFoundError
from clevergit.ui.widgets.repo_view import RepositoryView
from clevergit.ui.widgets.status_view import StatusView
from clevergit.ui.widgets.branch_view import BranchView
from clevergit.ui.widgets.log_view import LogView
from clevergit.ui.widgets.commit_dialog import CommitDialog


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self) -> None:
        super().__init__()
        self.repo: Optional[Repo] = None
        self.current_path: Optional[Path] = None
        
        self.setWindowTitle("CleverGit - Git Client")
        self.setGeometry(100, 100, 1200, 800)
        
        self._setup_ui()
        self._setup_menu()
        
    def _setup_ui(self) -> None:
        """Setup the main UI layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Top toolbar
        toolbar_layout = QHBoxLayout()
        
        self.open_button = QPushButton("📁 Open Repository")
        self.open_button.clicked.connect(self._open_repository)
        toolbar_layout.addWidget(self.open_button)
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self._refresh)
        toolbar_layout.addWidget(self.refresh_button)
        
        self.commit_button = QPushButton("✅ Commit")
        self.commit_button.clicked.connect(self._show_commit_dialog)
        self.commit_button.setEnabled(False)
        toolbar_layout.addWidget(self.commit_button)
        
        self.path_label = QLabel("No repository opened")
        toolbar_layout.addWidget(self.path_label)
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Repository info and branches
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Repository Info"))
        self.repo_view = RepositoryView()
        left_layout.addWidget(self.repo_view)
        
        left_layout.addWidget(QLabel("Branches"))
        self.branch_view = BranchView(self)
        left_layout.addWidget(self.branch_view)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Right panel: Status and Log
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("File Status"))
        self.status_view = StatusView()
        right_layout.addWidget(self.status_view)
        
        right_layout.addWidget(QLabel("Commit History"))
        self.log_view = LogView()
        right_layout.addWidget(self.log_view)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
    def _setup_menu(self) -> None:
        """Setup application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = file_menu.addAction("Open Repository")
        open_action.triggered.connect(self._open_repository)
        open_action.setShortcut("Ctrl+O")
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        refresh_action = edit_menu.addAction("Refresh")
        refresh_action.triggered.connect(self._refresh)
        refresh_action.setShortcut("F5")
        
        # Commit menu
        commit_menu = menubar.addMenu("Commit")
        
        commit_action = commit_menu.addAction("New Commit")
        commit_action.triggered.connect(self._show_commit_dialog)
        commit_action.setShortcut("Ctrl+K")
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)
        
    def _open_repository(self) -> None:
        """Open a repository dialog."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Repository Directory",
            str(Path.home())
        )
        
        if not path:
            return
        
        try:
            self.repo = Repo.open(path)
            self.current_path = Path(path)
            self.path_label.setText(f"📂 {path}")
            self.commit_button.setEnabled(True)
            
            self._refresh()
            QMessageBox.information(self, "Success", f"Opened repository: {path}")
            
        except RepoNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Failed to open repository:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")
    
    def _refresh(self) -> None:
        """Refresh all views."""
        if not self.repo:
            QMessageBox.warning(self, "Warning", "No repository opened")
            return
        
        try:
            # Update repository view
            current_branch = self.repo.current_branch()
            is_clean = self.repo.is_clean()
            self.repo_view.update_info(
                str(self.current_path),
                current_branch or "unknown",
                "Clean" if is_clean else "Dirty"
            )
            
            # Update status view
            status = self.repo.status()
            self.status_view.update_status(status)
            
            # Update branch view
            branches = self.repo.list_branches()
            self.branch_view.update_branches(branches)
            
            # Update log view
            log = self.repo.log(max_count=20)
            self.log_view.update_log(log)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh:\n{e}")
    
    def _show_commit_dialog(self) -> None:
        """Show commit dialog."""
        if not self.repo:
            QMessageBox.warning(self, "Warning", "No repository opened")
            return
        
        dialog = CommitDialog(self, self.repo)
        if dialog.exec():
            self._refresh()
            QMessageBox.information(self, "Success", "Commit created successfully")
    
    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.information(
            self,
            "About CleverGit",
            "CleverGit v0.1.0\n\n"
            "A powerful Git client with high-level abstractions.\n\n"
            "Made with Python and PySide6"
        )
