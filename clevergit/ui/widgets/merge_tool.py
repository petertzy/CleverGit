"""
Merge tool widget for resolving Git merge conflicts.
"""

from typing import Optional, List
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QSplitter,
    QGroupBox,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QTextDocument

from clevergit.core.conflict import (
    ConflictBlock,
    ConflictedFile,
    parse_conflicted_file,
    resolve_conflict_take_ours,
    resolve_conflict_take_theirs,
    resolve_conflict_take_both,
    resolve_all_conflicts,
)
from clevergit.ui.themes import get_theme_manager


class ConflictHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for conflict sections."""

    def __init__(self, parent: QTextDocument, section_type: str):
        super().__init__(parent)
        self.section_type = section_type

        # Get current theme
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()

        # Define formats for different sections using theme colors
        self.ours_format = QTextCharFormat()
        if theme:
            self.ours_format.setBackground(QColor(theme.diff_added))
            self.ours_format.setForeground(QColor(theme.text))
        else:
            self.ours_format.setBackground(QColor("#e6ffed"))
            self.ours_format.setForeground(QColor("#24292e"))

        self.theirs_format = QTextCharFormat()
        if theme:
            self.theirs_format.setBackground(QColor(theme.diff_removed))
            self.theirs_format.setForeground(QColor(theme.text))
        else:
            self.theirs_format.setBackground(QColor("#ffeef0"))
            self.theirs_format.setForeground(QColor("#24292e"))

        self.base_format = QTextCharFormat()
        if theme:
            self.base_format.setBackground(QColor(theme.diff_modified))
            self.base_format.setForeground(QColor(theme.text))
        else:
            self.base_format.setBackground(QColor("#fffbdd"))
            self.base_format.setForeground(QColor("#24292e"))

    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to a block of text."""
        if not text:
            return

        # Apply background color based on section type
        if self.section_type == "ours":
            self.setFormat(0, len(text), self.ours_format)
        elif self.section_type == "theirs":
            self.setFormat(0, len(text), self.theirs_format)
        elif self.section_type == "base":
            self.setFormat(0, len(text), self.base_format)


class MergeToolWidget(QWidget):
    """
    Three-way merge tool widget for resolving conflicts.

    Features:
    - Display Base, Ours, and Theirs versions side by side
    - Quick resolution buttons (Take Ours, Take Theirs, Take Both)
    - Manual editing of the result
    - Navigate between multiple conflicts in a file

    Signals:
        conflict_resolved: Emitted when a conflict is resolved
        all_conflicts_resolved: Emitted when all conflicts in file are resolved
    """

    conflict_resolved = Signal(int)  # conflict_index
    all_conflicts_resolved = Signal()

    def __init__(self):
        super().__init__()

        self._conflicted_file: Optional[ConflictedFile] = None
        self._current_conflict_index: int = 0
        self._resolutions: List[Optional[List[str]]] = []

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Header with file info and conflict navigation
        header_layout = QHBoxLayout()

        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.file_label)

        header_layout.addStretch()

        self.conflict_label = QLabel("Conflict: -/-")
        header_layout.addWidget(self.conflict_label)

        self.prev_button = QPushButton("← Previous")
        self.prev_button.clicked.connect(self._go_to_previous_conflict)
        self.prev_button.setEnabled(False)
        header_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next →")
        self.next_button.clicked.connect(self._go_to_next_conflict)
        self.next_button.setEnabled(False)
        header_layout.addWidget(self.next_button)

        layout.addLayout(header_layout)

        # Three-way diff view (Base, Ours, Theirs)
        diff_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Base version (if available)
        base_group = QGroupBox("Base (Common Ancestor)")
        base_layout = QVBoxLayout(base_group)
        self.base_text = QTextEdit()
        self.base_text.setReadOnly(True)
        self.base_text.setFont(QFont("Monospace", 10))
        self.base_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        base_layout.addWidget(self.base_text)
        diff_splitter.addWidget(base_group)

        # Ours version
        ours_group = QGroupBox("Ours (Current Branch)")
        ours_layout = QVBoxLayout(ours_group)
        self.ours_text = QTextEdit()
        self.ours_text.setReadOnly(True)
        self.ours_text.setFont(QFont("Monospace", 10))
        self.ours_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        ours_layout.addWidget(self.ours_text)
        diff_splitter.addWidget(ours_group)

        # Theirs version
        theirs_group = QGroupBox("Theirs (Incoming)")
        theirs_layout = QVBoxLayout(theirs_group)
        self.theirs_text = QTextEdit()
        self.theirs_text.setReadOnly(True)
        self.theirs_text.setFont(QFont("Monospace", 10))
        self.theirs_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        theirs_layout.addWidget(self.theirs_text)
        diff_splitter.addWidget(theirs_group)

        # Set equal sizes for all panes
        diff_splitter.setSizes([333, 333, 334])

        layout.addWidget(diff_splitter)

        # Resolution result editor
        result_group = QGroupBox("Resolution Result (Editable)")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setFont(QFont("Monospace", 10))
        self.result_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.result_text.setPlaceholderText("Choose a resolution or manually edit...")
        result_layout.addWidget(self.result_text)

        layout.addWidget(result_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.take_ours_button = QPushButton("Take Ours")
        self.take_ours_button.clicked.connect(self._take_ours)
        self.take_ours_button.setEnabled(False)
        button_layout.addWidget(self.take_ours_button)

        self.take_theirs_button = QPushButton("Take Theirs")
        self.take_theirs_button.clicked.connect(self._take_theirs)
        self.take_theirs_button.setEnabled(False)
        button_layout.addWidget(self.take_theirs_button)

        self.take_both_button = QPushButton("Take Both")
        self.take_both_button.clicked.connect(self._take_both)
        self.take_both_button.setEnabled(False)
        button_layout.addWidget(self.take_both_button)

        button_layout.addStretch()

        self.mark_resolved_button = QPushButton("Mark as Resolved")
        # Inline styles are removed - theme system handles button styling
        self.mark_resolved_button.clicked.connect(self._mark_current_resolved)
        self.mark_resolved_button.setEnabled(False)
        button_layout.addWidget(self.mark_resolved_button)

        self.save_all_button = QPushButton("Save All Resolutions")
        # Inline styles are removed - theme system handles button styling
        self.save_all_button.clicked.connect(self._save_all_resolutions)
        self.save_all_button.setEnabled(False)
        button_layout.addWidget(self.save_all_button)

        layout.addLayout(button_layout)

        # Apply syntax highlighters
        self.base_highlighter = ConflictHighlighter(self.base_text.document(), "base")
        self.ours_highlighter = ConflictHighlighter(self.ours_text.document(), "ours")
        self.theirs_highlighter = ConflictHighlighter(self.theirs_text.document(), "theirs")

    def load_file(self, file_path: Path) -> None:
        """
        Load a conflicted file for resolution.

        Args:
            file_path: Path to the file with conflicts
        """
        try:
            self._conflicted_file = parse_conflicted_file(file_path)
            self._current_conflict_index = 0

            # Initialize resolutions list
            self._resolutions = [None] * self._conflicted_file.get_conflict_count()

            # Update UI
            self.file_label.setText(f"File: {file_path}")

            if self._conflicted_file.has_conflicts():
                self._update_conflict_display()
                self._enable_buttons(True)
            else:
                QMessageBox.information(
                    self,
                    "No Conflicts",
                    f"The file '{file_path}' does not contain any merge conflicts.",
                )
                self._enable_buttons(False)

        except FileNotFoundError:
            QMessageBox.critical(
                self, "File Not Found", f"The file '{file_path}' could not be found."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading File", f"An error occurred while loading the file: {str(e)}"
            )

    def _update_conflict_display(self) -> None:
        """Update the display for the current conflict."""
        if not self._conflicted_file or not self._conflicted_file.has_conflicts():
            return

        conflict = self._conflicted_file.conflicts[self._current_conflict_index]

        # Update conflict counter
        self.conflict_label.setText(
            f"Conflict: {self._current_conflict_index + 1}/"
            f"{self._conflicted_file.get_conflict_count()}"
        )

        # Update navigation buttons
        self.prev_button.setEnabled(self._current_conflict_index > 0)
        self.next_button.setEnabled(
            self._current_conflict_index < self._conflicted_file.get_conflict_count() - 1
        )

        # Display base version (if available)
        if conflict.has_base():
            self.base_text.setText(conflict.get_base_text())
        else:
            self.base_text.setText("(No base version available)")

        # Display ours and theirs versions
        self.ours_text.setText(conflict.get_ours_text())
        self.theirs_text.setText(conflict.get_theirs_text())

        # Display existing resolution if available
        if self._resolutions[self._current_conflict_index] is not None:
            resolution = self._resolutions[self._current_conflict_index]
            self.result_text.setText("\n".join(resolution))
            self.mark_resolved_button.setText("✓ Resolved (Update)")
        else:
            self.result_text.clear()
            self.mark_resolved_button.setText("Mark as Resolved")

    def _go_to_previous_conflict(self) -> None:
        """Navigate to the previous conflict."""
        if self._current_conflict_index > 0:
            self._current_conflict_index -= 1
            self._update_conflict_display()

    def _go_to_next_conflict(self) -> None:
        """Navigate to the next conflict."""
        if (
            self._conflicted_file
            and self._current_conflict_index < self._conflicted_file.get_conflict_count() - 1
        ):
            self._current_conflict_index += 1
            self._update_conflict_display()

    def _take_ours(self) -> None:
        """Take the 'ours' version for resolution."""
        if not self._conflicted_file:
            return

        conflict = self._conflicted_file.conflicts[self._current_conflict_index]
        resolution = resolve_conflict_take_ours(conflict)
        self.result_text.setText("\n".join(resolution))

    def _take_theirs(self) -> None:
        """Take the 'theirs' version for resolution."""
        if not self._conflicted_file:
            return

        conflict = self._conflicted_file.conflicts[self._current_conflict_index]
        resolution = resolve_conflict_take_theirs(conflict)
        self.result_text.setText("\n".join(resolution))

    def _take_both(self) -> None:
        """Take both versions for resolution (ours first, then theirs)."""
        if not self._conflicted_file:
            return

        conflict = self._conflicted_file.conflicts[self._current_conflict_index]
        resolution = resolve_conflict_take_both(conflict, ours_first=True)
        self.result_text.setText("\n".join(resolution))

    def _mark_current_resolved(self) -> None:
        """Mark the current conflict as resolved with the content in result editor."""
        result_content = self.result_text.toPlainText()

        if not result_content.strip():
            QMessageBox.warning(
                self, "Empty Resolution", "Please provide a resolution before marking as resolved."
            )
            return

        # Store the resolution
        resolution_lines = result_content.split("\n")
        self._resolutions[self._current_conflict_index] = resolution_lines

        # Update button text
        self.mark_resolved_button.setText("✓ Resolved (Update)")

        # Enable save button if all conflicts are resolved
        if all(r is not None for r in self._resolutions):
            self.save_all_button.setEnabled(True)

        # Emit signal
        self.conflict_resolved.emit(self._current_conflict_index)

        # Auto-advance to next unresolved conflict if available
        for i in range(self._current_conflict_index + 1, len(self._resolutions)):
            if self._resolutions[i] is None:
                self._current_conflict_index = i
                self._update_conflict_display()
                return

        # If no more unresolved conflicts, show completion message
        if all(r is not None for r in self._resolutions):
            QMessageBox.information(
                self,
                "All Conflicts Resolved",
                "All conflicts have been resolved. Click 'Save All Resolutions' to write the changes to the file.",
            )

    def _save_all_resolutions(self) -> None:
        """Save all resolutions to the file."""
        if not self._conflicted_file:
            return

        # Check if all conflicts are resolved
        if not all(r is not None for r in self._resolutions):
            unresolved = [i + 1 for i, r in enumerate(self._resolutions) if r is None]
            QMessageBox.warning(
                self,
                "Unresolved Conflicts",
                f"Please resolve all conflicts before saving.\n"
                f"Unresolved conflicts: {', '.join(map(str, unresolved))}",
            )
            return

        try:
            # Apply all resolutions
            resolved_content = resolve_all_conflicts(self._conflicted_file, self._resolutions)

            # Write to file
            file_path = Path(self._conflicted_file.file_path)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(resolved_content)

            QMessageBox.information(
                self,
                "Saved Successfully",
                f"All conflicts have been resolved and saved to:\n{file_path}\n\n"
                f"Don't forget to stage and commit the resolved file.",
            )

            # Emit signal
            self.all_conflicts_resolved.emit()

            # Disable buttons after save
            self._enable_buttons(False)

        except Exception as e:
            QMessageBox.critical(
                self, "Save Error", f"An error occurred while saving the file: {str(e)}"
            )

    def _enable_buttons(self, enabled: bool) -> None:
        """Enable or disable action buttons."""
        self.take_ours_button.setEnabled(enabled)
        self.take_theirs_button.setEnabled(enabled)
        self.take_both_button.setEnabled(enabled)
        self.mark_resolved_button.setEnabled(enabled)
        self.prev_button.setEnabled(enabled and self._current_conflict_index > 0)
        self.next_button.setEnabled(
            enabled
            and self._conflicted_file
            and self._current_conflict_index < self._conflicted_file.get_conflict_count() - 1
        )

    def get_resolved_content(self) -> Optional[str]:
        """
        Get the fully resolved file content.

        Returns:
            Resolved content if all conflicts are resolved, None otherwise
        """
        if not self._conflicted_file or not all(r is not None for r in self._resolutions):
            return None

        return resolve_all_conflicts(self._conflicted_file, self._resolutions)

    def is_all_resolved(self) -> bool:
        """Check if all conflicts are resolved."""
        return all(r is not None for r in self._resolutions) if self._resolutions else False
