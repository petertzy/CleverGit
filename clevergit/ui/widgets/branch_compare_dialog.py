"""
Branch comparison dialog widget.
"""

from typing import TYPE_CHECKING
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QMessageBox,
    QTextEdit,
    QSplitter,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

if TYPE_CHECKING:
    from clevergit.core.repo import Repo


class BranchCompareDialog(QDialog):
    """Dialog for comparing two branches."""

    def __init__(self, parent, repo: "Repo") -> None:
        """
        Initialize branch comparison dialog.

        Args:
            parent: Parent widget
            repo: Repository instance
        """
        super().__init__(parent)
        self.repo = repo
        self.comparison = None

        self.setWindowTitle("Compare Branches")
        self.setGeometry(100, 100, 900, 700)

        layout = QVBoxLayout()

        # Branch selection section
        selection_group = QGroupBox("Compare Branch with Current Branch")
        selection_layout = QHBoxLayout()

        # Current branch display (read-only)
        selection_layout.addWidget(QLabel("Current Branch:"))
        self.current_branch_label = QLabel()
        current_font = QFont()
        current_font.setBold(True)
        self.current_branch_label.setFont(current_font)
        selection_layout.addWidget(self.current_branch_label)

        selection_layout.addWidget(QLabel("↔"))

        # Compare branch selector
        selection_layout.addWidget(QLabel("Select Branch:"))
        self.compare_branch_combo = QComboBox()
        selection_layout.addWidget(self.compare_branch_combo)

        # Compare button
        compare_button = QPushButton("Compare")
        compare_button.clicked.connect(self._perform_comparison)
        selection_layout.addWidget(compare_button)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Load branches
        self._load_branches()

        # Summary section
        self.summary_label = QLabel("")
        summary_font = QFont()
        summary_font.setBold(True)
        summary_font.setPointSize(11)
        self.summary_label.setFont(summary_font)
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        # Statistics section
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout()

        self.ahead_label = QLabel("Ahead: -")
        self.behind_label = QLabel("Behind: -")
        self.files_label = QLabel("Different Files: -")

        stats_layout.addWidget(self.ahead_label)
        stats_layout.addWidget(self.behind_label)
        stats_layout.addWidget(self.files_label)
        stats_layout.addStretch()

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Create splitter for details
        splitter = QSplitter(Qt.Vertical)

        # Commits section
        commits_widget = QWidget()
        commits_layout = QVBoxLayout()
        commits_layout.setContentsMargins(0, 0, 0, 0)

        # Ahead commits
        commits_layout.addWidget(QLabel("Commits in Compare Branch (ahead):"))
        self.ahead_commits_list = QListWidget()
        self.ahead_commits_list.itemDoubleClicked.connect(self._show_commit_details)
        commits_layout.addWidget(self.ahead_commits_list)

        # Behind commits
        commits_layout.addWidget(QLabel("Commits in Current Branch (behind):"))
        self.behind_commits_list = QListWidget()
        self.behind_commits_list.itemDoubleClicked.connect(self._show_commit_details)
        commits_layout.addWidget(self.behind_commits_list)

        commits_widget.setLayout(commits_layout)
        splitter.addWidget(commits_widget)

        # Files section
        files_widget = QWidget()
        files_layout = QVBoxLayout()
        files_layout.setContentsMargins(0, 0, 0, 0)

        files_layout.addWidget(QLabel("Different Files:"))
        self.files_list = QListWidget()
        self.files_list.itemDoubleClicked.connect(self._show_file_diff)
        files_layout.addWidget(self.files_list)

        files_widget.setLayout(files_layout)
        splitter.addWidget(files_widget)

        # Set initial splitter sizes
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _load_branches(self) -> None:
        """Load branches into the combo boxes."""
        try:
            branches = self.repo.list_branches(remote=False)
            branch_names = [b.name for b in branches]

            # Get current branch
            current = self.repo.current_branch()

            # Display current branch
            if current:
                self.current_branch_label.setText(current)
            else:
                self.current_branch_label.setText("(detached HEAD)")

            # Add all branches except current to compare combo
            for branch_name in branch_names:
                if branch_name != current:
                    self.compare_branch_combo.addItem(branch_name)

            # If no other branches available, show message
            if self.compare_branch_combo.count() == 0:
                self.compare_branch_combo.addItem("(no other branches)")
                self.compare_branch_combo.setEnabled(False)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load branches: {e}")

    def _perform_comparison(self) -> None:
        """Perform branch comparison and display results."""
        # Base branch is always the current branch
        base_branch = self.repo.current_branch()
        compare_branch = self.compare_branch_combo.currentText()

        if not base_branch:
            QMessageBox.warning(self, "Warning", "Cannot determine current branch")
            return

        if not compare_branch or compare_branch == "(no other branches)":
            QMessageBox.warning(self, "Warning", "Please select a branch to compare")
            return

        if base_branch == compare_branch:
            QMessageBox.information(
                self, "Info", "Selected branches are the same. Please select a different branch."
            )
            return

        try:
            # Perform comparison
            self.comparison = self.repo.compare_branches(base_branch, compare_branch)

            # Update summary
            self.summary_label.setText(self.comparison.summary())

            # Update statistics
            self.ahead_label.setText(f"Ahead: {self.comparison.ahead_count} commit(s)")
            self.behind_label.setText(f"Behind: {self.comparison.behind_count} commit(s)")
            self.files_label.setText(f"Different Files: {len(self.comparison.different_files)}")

            # Update ahead commits list
            self.ahead_commits_list.clear()
            for commit_sha in self.comparison.ahead_commits:
                try:
                    commit_info = self.repo.client.show_commit(commit_sha)
                    message = commit_info.get("message", "").split("\n")[0]
                    display_text = f"{commit_sha[:8]} - {message}"
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, commit_sha)
                    self.ahead_commits_list.addItem(item)
                except Exception:
                    # If we can't get commit info, just show the SHA
                    item = QListWidgetItem(commit_sha[:8])
                    item.setData(Qt.UserRole, commit_sha)
                    self.ahead_commits_list.addItem(item)

            # Update behind commits list
            self.behind_commits_list.clear()
            for commit_sha in self.comparison.behind_commits:
                try:
                    commit_info = self.repo.client.show_commit(commit_sha)
                    message = commit_info.get("message", "").split("\n")[0]
                    display_text = f"{commit_sha[:8]} - {message}"
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, commit_sha)
                    self.behind_commits_list.addItem(item)
                except Exception:
                    # If we can't get commit info, just show the SHA
                    item = QListWidgetItem(commit_sha[:8])
                    item.setData(Qt.UserRole, commit_sha)
                    self.behind_commits_list.addItem(item)

            # Update files list
            self.files_list.clear()
            for file_path in self.comparison.different_files:
                self.files_list.addItem(file_path)

            # Show message if branches are up to date
            if self.comparison.is_up_to_date:
                QMessageBox.information(
                    self,
                    "Up to Date",
                    f"Branches '{compare_branch}' and '{base_branch}' are up to date.\nNo differences found.",
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to compare branches:\n{e}")

    def _show_commit_details(self, item: QListWidgetItem) -> None:
        """Show detailed information about a commit."""
        commit_sha = item.data(Qt.UserRole)
        if not commit_sha:
            return

        try:
            # Get full commit information
            commit_info = self.repo.client.show_commit(commit_sha)

            # Get commit diff - handle root commit case
            try:
                diff = self.repo.client.diff(f"{commit_sha}^", commit_sha)
            except Exception:
                # This might be the root commit with no parent
                try:
                    diff = self.repo.client.diff(commit_sha)
                except Exception:
                    diff = "(Unable to show diff for this commit)"

            # Create a dialog to show commit details
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"Commit Details - {commit_sha[:8]}")
            details_dialog.setGeometry(150, 150, 800, 600)

            layout = QVBoxLayout()

            # Commit info
            info_text = f"SHA: {commit_sha}\n"
            info_text += f"Author: {commit_info.get('author', 'Unknown')}\n"
            info_text += f"Date: {commit_info.get('date', 'Unknown')}\n"
            info_text += f"Message:\n{commit_info.get('message', 'No message')}\n"

            info_label = QTextEdit()
            info_label.setPlainText(info_text)
            info_label.setReadOnly(True)
            info_label.setMaximumHeight(120)
            layout.addWidget(info_label)

            # Diff
            layout.addWidget(QLabel("Changes:"))
            diff_view = QTextEdit()
            diff_view.setPlainText(diff)
            diff_view.setReadOnly(True)
            diff_view.setFontFamily("Courier")
            layout.addWidget(diff_view)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(details_dialog.accept)
            layout.addWidget(close_btn)

            details_dialog.setLayout(layout)
            details_dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to show commit details:\n{e}")

    def _show_file_diff(self, item: QListWidgetItem) -> None:
        """Show diff for a specific file between the compared branches."""
        file_path = item.text()
        if not file_path or not self.comparison:
            return

        try:
            # Get the base and compare branch names
            base_branch = self.repo.current_branch()
            compare_branch = self.compare_branch_combo.currentText()

            if not base_branch or not compare_branch:
                return

            # Get the diff for this specific file
            try:
                diff = self.repo.client.diff(base_branch, compare_branch, file_path=file_path)
            except Exception as e:
                diff = f"(Unable to show diff for this file: {e})"

            # Create a dialog to show the file diff
            diff_dialog = QDialog(self)
            diff_dialog.setWindowTitle(f"File Diff - {file_path}")
            diff_dialog.setGeometry(150, 150, 900, 700)

            layout = QVBoxLayout()

            # File info
            info_text = f"File: {file_path}\n"
            info_text += f"Comparing: {base_branch} ↔ {compare_branch}\n"

            info_label = QLabel(info_text)
            info_font = QFont()
            info_font.setBold(True)
            info_label.setFont(info_font)
            layout.addWidget(info_label)

            # Diff view
            diff_view = QTextEdit()
            diff_view.setPlainText(diff)
            diff_view.setReadOnly(True)
            diff_font = QFont("Courier")
            diff_view.setFont(diff_font)
            diff_view.setLineWrapMode(QTextEdit.NoWrap)
            layout.addWidget(diff_view)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(diff_dialog.accept)
            layout.addWidget(close_btn)

            diff_dialog.setLayout(layout)
            diff_dialog.exec()

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to show file diff:\n{e}")
