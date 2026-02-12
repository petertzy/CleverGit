"""
Reset dialog widget.
"""

from typing import TYPE_CHECKING, List, Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
    QWidget,
)
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from clevergit.core.repo import Repo


class ResetDialog(QDialog):
    """Dialog for resetting to previous commits."""

    def __init__(self, parent, repo: "Repo") -> None:
        """
        Initialize reset dialog.

        Args:
            parent: Parent widget
            repo: Repository instance
        """
        super().__init__(parent)
        self.repo = repo
        self.selected_commit: Optional[str] = None
        self.reset_mode: str = "mixed"

        self.setWindowTitle("Reset to Commit")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Instructions
        instruction_label = QLabel("Select a commit to reset to:")
        layout.addWidget(instruction_label)

        # Commits list
        self.commits_list = QListWidget()
        self.commits_list.itemSelectionChanged.connect(self._on_selection_changed)

        # Load commits and reflog
        try:
            commits = repo.client.log(max_count=50)
            self.commit_data = {}

            for commit in commits:
                sha = commit.get("sha", "")
                message = commit.get("message", "").split("\n")[0]  # First line only
                author = commit.get("author", "")
                date = commit.get("date", "")

                # Format display text
                display_text = f"{sha[:8]} - {message} ({author})"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, sha)  # Store full SHA in item data
                self.commits_list.addItem(item)

                # Store full commit info
                self.commit_data[sha] = commit

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to load commits: {e}")

        layout.addWidget(self.commits_list)

        # Commit details view
        details_label = QLabel("Commit Details:")
        layout.addWidget(details_label)

        self.details_view = QTextEdit()
        self.details_view.setReadOnly(True)
        self.details_view.setMaximumHeight(120)
        layout.addWidget(self.details_view)

        # Reset mode selection
        mode_label = QLabel("Reset Mode:")
        mode_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(mode_label)

        self.mode_group = QButtonGroup(self)

        # Soft reset radio button
        self.soft_radio = QRadioButton("Soft Reset")
        self.soft_radio.setToolTip("Keep staged and working directory changes")
        soft_desc = QLabel("  → Moves HEAD, keeps staged and working changes")
        soft_desc.setStyleSheet("color: gray; font-style: italic; margin-left: 20px;")

        # Mixed reset radio button (default)
        self.mixed_radio = QRadioButton("Mixed Reset (default)")
        self.mixed_radio.setToolTip("Reset staging area, keep working directory changes")
        self.mixed_radio.setChecked(True)
        mixed_desc = QLabel("  → Moves HEAD, resets staging, keeps working changes")
        mixed_desc.setStyleSheet("font-style: italic; margin-left: 20px;")

        # Hard reset radio button
        self.hard_radio = QRadioButton("Hard Reset")
        self.hard_radio.setToolTip("Discard all changes (DESTRUCTIVE)")
        hard_desc = QLabel("  → Moves HEAD, resets staging, discards all changes")
        hard_desc.setStyleSheet("font-weight: bold; margin-left: 20px;")

        self.mode_group.addButton(self.soft_radio, 1)
        self.mode_group.addButton(self.mixed_radio, 2)
        self.mode_group.addButton(self.hard_radio, 3)

        layout.addWidget(self.soft_radio)
        layout.addWidget(soft_desc)
        layout.addWidget(self.mixed_radio)
        layout.addWidget(mixed_desc)
        layout.addWidget(self.hard_radio)
        layout.addWidget(hard_desc)

        # Warning label
        warning_label = QLabel("⚠️ Use reflog to recover from accidental resets")
        warning_label.setStyleSheet("font-style: italic; margin-top: 10px;")
        layout.addWidget(warning_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._on_reset)
        self.reset_button.setEnabled(False)
        button_layout.addWidget(self.reset_button)

        self.reflog_button = QPushButton("View Reflog")
        self.reflog_button.clicked.connect(self._show_reflog)
        button_layout.addWidget(self.reflog_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_selection_changed(self) -> None:
        """Handle commit selection change."""
        selected_items = self.commits_list.selectedItems()
        self.reset_button.setEnabled(len(selected_items) == 1)

        if len(selected_items) == 1:
            sha = selected_items[0].data(Qt.UserRole)
            commit = self.commit_data.get(sha, {})

            details = f"SHA: {sha}\n"
            details += f"Author: {commit.get('author', 'Unknown')}\n"
            details += f"Date: {commit.get('date', 'Unknown')}\n"
            details += f"\nMessage:\n{commit.get('message', 'No message')}"

            self.details_view.setPlainText(details)
        else:
            self.details_view.setPlainText("No commit selected")

    def _on_reset(self) -> None:
        """Handle reset button click."""
        selected_items = self.commits_list.selectedItems()

        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a commit to reset to")
            return

        sha = selected_items[0].data(Qt.UserRole)

        # Determine reset mode
        if self.soft_radio.isChecked():
            self.reset_mode = "soft"
            mode_desc = "soft reset"
        elif self.hard_radio.isChecked():
            self.reset_mode = "hard"
            mode_desc = "hard reset"
        else:
            self.reset_mode = "mixed"
            mode_desc = "mixed reset"

        # Confirm action with appropriate warning
        message = f"Reset to commit {sha[:8]}?\n\n"

        if self.reset_mode == "hard":
            message += "⚠️ WARNING: This will DISCARD ALL uncommitted changes!\n"
            message += "This operation is DESTRUCTIVE and cannot be easily undone.\n\n"
            message += "Are you absolutely sure you want to proceed?"

            reply = QMessageBox.critical(
                self,
                "Confirm Hard Reset",
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
        else:
            message += f"Mode: {mode_desc}\n"
            if self.reset_mode == "soft":
                message += "Staged and working changes will be preserved."
            else:  # mixed
                message += "Working changes will be preserved, but staging area will be reset."

            reply = QMessageBox.question(
                self, "Confirm Reset", message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

        if reply != QMessageBox.Yes:
            return

        # Perform reset
        try:
            from clevergit.core.commit import soft_reset, mixed_reset, hard_reset

            if self.reset_mode == "soft":
                soft_reset(self.repo.client, sha)
            elif self.reset_mode == "hard":
                hard_reset(self.repo.client, sha)
            else:
                mixed_reset(self.repo.client, sha)

            self.selected_commit = sha
            QMessageBox.information(
                self, "Success", f"Successfully reset to {sha[:8]} ({self.reset_mode} mode)"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset:\n{e}")

    def _show_reflog(self) -> None:
        """Show reflog dialog."""
        try:
            from clevergit.core.commit import get_reflog

            reflog_entries = get_reflog(self.repo.client, max_count=30)

            if not reflog_entries:
                QMessageBox.information(self, "Reflog", "No reflog entries found")
                return

            # Create reflog dialog
            reflog_dialog = QDialog(self)
            reflog_dialog.setWindowTitle("Reflog - Command History")
            reflog_dialog.setGeometry(150, 150, 700, 400)

            layout = QVBoxLayout()

            info_label = QLabel("Recent HEAD movements (use to recover from accidental resets):")
            layout.addWidget(info_label)

            reflog_list = QListWidget()

            for entry in reflog_entries:
                sha = entry.get("sha", "")
                message = entry.get("message", "")
                selector = entry.get("selector", "")

                display_text = f"{selector}: {sha[:8]} - {message}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, sha)
                reflog_list.addItem(item)

            layout.addWidget(reflog_list)

            # Buttons
            button_layout = QHBoxLayout()

            reset_to_button = QPushButton("Reset to Selected")
            reset_to_button.clicked.connect(
                lambda: self._reset_to_reflog(reflog_list, reflog_dialog)
            )
            button_layout.addWidget(reset_to_button)

            close_button = QPushButton("Close")
            close_button.clicked.connect(reflog_dialog.close)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)
            reflog_dialog.setLayout(layout)

            reflog_dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get reflog:\n{e}")

    def _reset_to_reflog(self, reflog_list: QListWidget, dialog: QDialog) -> None:
        """Reset to selected reflog entry."""
        selected_items = reflog_list.selectedItems()

        if not selected_items:
            QMessageBox.warning(dialog, "Warning", "Please select a reflog entry")
            return

        sha = selected_items[0].data(Qt.UserRole)

        reply = QMessageBox.question(
            dialog,
            "Confirm Reset",
            f"Reset to {sha[:8]}?\n\nThis will use the current reset mode.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                from clevergit.core.commit import soft_reset, mixed_reset, hard_reset

                if self.reset_mode == "soft":
                    soft_reset(self.repo.client, sha)
                elif self.reset_mode == "hard":
                    hard_reset(self.repo.client, sha)
                else:
                    mixed_reset(self.repo.client, sha)

                QMessageBox.information(dialog, "Success", f"Reset to {sha[:8]}")
                dialog.close()
                self.accept()

            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to reset:\n{e}")
