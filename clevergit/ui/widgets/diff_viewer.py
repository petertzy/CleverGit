"""
Diff viewer widget for displaying file differences.
"""

from typing import Optional, List
from pathlib import Path
import difflib
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QSplitter,
    QGroupBox,
    QMenu,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument, QCursor, QTextBlockFormat

# Import diff utilities for hunk operations
from clevergit.core.diff import (
    parse_diff_hunks,
    create_patch_from_hunk,
    extract_index_line_from_diff,
)

# Import theme manager
from clevergit.ui.themes import get_theme_manager


class DiffSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for unified diff format with word-level highlighting."""

    def __init__(self, parent: QTextDocument):
        super().__init__(parent)

        # Get current theme
        theme_manager = get_theme_manager()
        theme = theme_manager.get_current_theme()

        # Define formats for different line types using improved colors
        self.added_format = QTextCharFormat()
        if theme:
            self.added_format.setBackground(QColor(theme.diff_added))
            self.added_format.setForeground(QColor(theme.text))
        else:
            # Softer green background similar to SmartGit
            self.added_format.setBackground(QColor("#d4f8d4"))
            self.added_format.setForeground(QColor("#1b4d1b"))

        # Word-level highlight for added content
        self.added_word_format = QTextCharFormat()
        if theme:
            self.added_word_format.setBackground(QColor(theme.diff_added))
            self.added_word_format.setForeground(QColor(theme.text))
        else:
            self.added_word_format.setBackground(QColor("#a3e7a3"))
            self.added_word_format.setForeground(QColor("#0a3d0a"))
        self.added_word_format.setFontWeight(QFont.Weight.Bold)

        self.deleted_format = QTextCharFormat()
        if theme:
            self.deleted_format.setBackground(QColor(theme.diff_removed))
            self.deleted_format.setForeground(QColor(theme.text))
        else:
            # Softer red background similar to SmartGit
            self.deleted_format.setBackground(QColor("#ffd7d7"))
            self.deleted_format.setForeground(QColor("#7d0000"))

        # Word-level highlight for deleted content
        self.deleted_word_format = QTextCharFormat()
        if theme:
            self.deleted_word_format.setBackground(QColor(theme.diff_removed))
            self.deleted_word_format.setForeground(QColor(theme.text))
        else:
            self.deleted_word_format.setBackground(QColor("#ffb3b3"))
            self.deleted_word_format.setForeground(QColor("#5c0000"))
        self.deleted_word_format.setFontWeight(QFont.Weight.Bold)

        self.hunk_format = QTextCharFormat()
        if theme:
            self.hunk_format.setForeground(QColor(theme.button_info))
            self.hunk_format.setBackground(QColor(theme.background_secondary))
        else:
            self.hunk_format.setForeground(QColor("#0066cc"))
            self.hunk_format.setBackground(QColor("#e6f2ff"))
        self.hunk_format.setFontWeight(QFont.Weight.Bold)

        self.file_format = QTextCharFormat()
        if theme:
            self.file_format.setForeground(QColor(theme.text))
            self.file_format.setBackground(QColor(theme.background_secondary))
        else:
            self.file_format.setForeground(QColor("#24292e"))
            self.file_format.setBackground(QColor("#f6f8fa"))
        self.file_format.setFontWeight(QFont.Weight.Bold)

        self.context_format = QTextCharFormat()
        if theme:
            self.context_format.setForeground(QColor(theme.text))
        else:
            self.context_format.setForeground(QColor("#586069"))

        # Store previous block for word-level comparison
        self._previous_deleted_line = None

    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to a block of text with word-level highlighting."""
        if not text:
            return

        # File headers - enhanced with background
        if text.startswith("diff --git"):
            self.setFormat(0, len(text), self.file_format)
        elif text.startswith("index ") or text.startswith("---") or text.startswith("+++"):
            self.setFormat(0, len(text), self.file_format)
        # Hunk headers - enhanced with background
        elif text.startswith("@@"):
            self.setFormat(0, len(text), self.hunk_format)
        # Added lines with word-level highlighting
        elif text.startswith("+") and not text.startswith("+++"):
            self.setFormat(0, len(text), self.added_format)
            # Apply word-level highlighting if we have a previous deleted line
            self._apply_word_level_highlight(text, self._previous_deleted_line, True)
            self._previous_deleted_line = None  # Reset after processing
        # Deleted lines with word-level highlighting
        elif text.startswith("-") and not text.startswith("---"):
            self.setFormat(0, len(text), self.deleted_format)
            # Store for comparison with next added line
            self._previous_deleted_line = text[1:]  # Store without the '-' prefix
        # Context lines
        else:
            self.setFormat(0, len(text), self.context_format)
            self._previous_deleted_line = None  # Reset on context line

    def _apply_word_level_highlight(self, current_line: str, previous_line: Optional[str], is_added: bool) -> None:
        """Apply word-level highlighting to show specific word changes."""
        if not previous_line:
            return

        # Remove the +/- prefix
        current_content = current_line[1:] if current_line else ""
        
        # Use difflib to find word-level differences
        current_words = current_content.split()
        previous_words = previous_line.split()
        
        if not current_words or not previous_words:
            return

        # Get a sequence matcher for the words
        matcher = difflib.SequenceMatcher(None, previous_words, current_words)
        
        # Highlight changed words
        current_pos = 1  # Start after the +/- character
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if is_added and tag in ('replace', 'insert'):
                # Highlight added/changed words
                for word in current_words[j1:j2]:
                    # Find the word position in the original line
                    word_start = current_line.find(word, current_pos)
                    if word_start >= 0:
                        self.setFormat(word_start, len(word), self.added_word_format)
                        current_pos = word_start + len(word)


class LineNumberArea(QWidget):
    """Widget to display line numbers for a text edit."""

    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.text_edit = text_edit
        self.setMinimumWidth(50)
        self.setMaximumWidth(80)


class DiffViewer(QWidget):
    """
    Advanced diff viewer widget with multiple view modes.

    Features:
    - Unified and side-by-side diff views
    - Syntax highlighting
    - Line numbers
    - Navigation to next/previous difference
    - Diff statistics
    - Expand/collapse unchanged sections
    """

    # Signals
    diff_changed = Signal()
    stage_hunk_requested = Signal(str)  # Emits patch to stage
    unstage_hunk_requested = Signal(str)  # Emits patch to unstage

    def __init__(self, parent: Optional[QWidget] = None, repo_path: Optional[Path] = None):
        super().__init__(parent)

        self._current_diff = ""
        self._current_line = 0
        self._view_mode = "unified"  # 'unified' or 'side-by-side'
        self._show_line_numbers = True
        self._collapse_unchanged = False
        self._repo_path = repo_path
        self._current_file_path = None

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Control bar
        control_bar = self._create_control_bar()
        layout.addWidget(control_bar)

        # Stats display
        self.stats_label = QLabel("No diff loaded")
        self.stats_label.setStyleSheet("""
            QLabel {
                padding: 8px 12px;
                background-color: #f6f8fa;
                border: 1px solid #d1d5da;
                border-radius: 3px;
                font-weight: bold;
                color: #24292e;
            }
        """)
        layout.addWidget(self.stats_label)

        # Main diff display area
        self.diff_container = QWidget()
        self.diff_layout = QVBoxLayout(self.diff_container)
        self.diff_layout.setContentsMargins(0, 0, 0, 0)

        # Create unified view by default
        self._create_unified_view()

        layout.addWidget(self.diff_container)

    def _create_control_bar(self) -> QWidget:
        """Create the control bar with navigation and view options."""
        control_bar = QWidget()
        layout = QHBoxLayout(control_bar)
        layout.setContentsMargins(5, 5, 5, 5)

        # View mode selector
        layout.addWidget(QLabel("View:"))
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["Unified", "Side-by-Side"])
        self.view_mode_combo.currentTextChanged.connect(self._on_view_mode_changed)
        layout.addWidget(self.view_mode_combo)

        layout.addStretch()

        # Staging buttons
        self.stage_hunk_btn = QPushButton("Stage Hunk")
        self.stage_hunk_btn.clicked.connect(self.stage_hunk_at_cursor)
        self.stage_hunk_btn.setToolTip("Stage the hunk at cursor position")
        layout.addWidget(self.stage_hunk_btn)

        self.unstage_hunk_btn = QPushButton("Unstage Hunk")
        self.unstage_hunk_btn.clicked.connect(self.unstage_hunk_at_cursor)
        self.unstage_hunk_btn.setToolTip("Unstage the hunk at cursor position")
        layout.addWidget(self.unstage_hunk_btn)

        # Navigation buttons
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self.navigate_to_previous_diff)
        layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.navigate_to_next_diff)
        layout.addWidget(self.next_btn)

        layout.addStretch()

        # Options
        self.line_numbers_btn = QPushButton("Line Numbers: ON")
        self.line_numbers_btn.setCheckable(True)
        self.line_numbers_btn.setChecked(True)
        self.line_numbers_btn.clicked.connect(self._toggle_line_numbers)
        layout.addWidget(self.line_numbers_btn)

        self.collapse_btn = QPushButton("Collapse Unchanged")
        self.collapse_btn.setCheckable(True)
        self.collapse_btn.setChecked(False)
        self.collapse_btn.clicked.connect(self._toggle_collapse_unchanged)
        layout.addWidget(self.collapse_btn)

        return control_bar

    def _create_unified_view(self) -> None:
        """Create unified diff view with improved styling."""
        # Clear existing widgets
        self._clear_diff_container()

        # Create text edit with syntax highlighting
        self.unified_text = QTextEdit()
        self.unified_text.setReadOnly(True)
        
        # Use a better monospace font
        font = QFont("Courier New", 10)
        if not font.exactMatch():
            font = QFont("Monospace", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.unified_text.setFont(font)
        
        self.unified_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Add padding and better spacing
        self.unified_text.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                line-height: 1.4;
                border: 1px solid #d1d5da;
                border-radius: 3px;
            }
        """)

        # Enable context menu
        self.unified_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.unified_text.customContextMenuRequested.connect(self._show_context_menu)

        # Apply syntax highlighter
        self.highlighter = DiffSyntaxHighlighter(self.unified_text.document())

        self.diff_layout.addWidget(self.unified_text)

    def _create_side_by_side_view(self) -> None:
        """Create side-by-side diff view with improved styling."""
        # Clear existing widgets
        self._clear_diff_container()

        # Create splitter for two-pane view
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Use a better monospace font
        font = QFont("Courier New", 10)
        if not font.exactMatch():
            font = QFont("Monospace", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)

        # Left pane (old version)
        left_group = QGroupBox("Before")
        left_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d5da;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        left_layout = QVBoxLayout(left_group)
        self.left_text = QTextEdit()
        self.left_text.setReadOnly(True)
        self.left_text.setFont(font)
        self.left_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.left_text.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                background-color: #fff5f5;
                border: none;
            }
        """)
        left_layout.addWidget(self.left_text)
        splitter.addWidget(left_group)

        # Right pane (new version)
        right_group = QGroupBox("After")
        right_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d5da;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        right_layout = QVBoxLayout(right_group)
        self.right_text = QTextEdit()
        self.right_text.setReadOnly(True)
        self.right_text.setFont(font)
        self.right_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.right_text.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                background-color: #f0fff0;
                border: none;
            }
        """)
        right_layout.addWidget(self.right_text)
        splitter.addWidget(right_group)

        # Set equal sizes
        splitter.setSizes([500, 500])

        self.diff_layout.addWidget(splitter)

        # Synchronize scrolling
        self.left_text.verticalScrollBar().valueChanged.connect(
            self.right_text.verticalScrollBar().setValue
        )
        self.right_text.verticalScrollBar().valueChanged.connect(
            self.left_text.verticalScrollBar().setValue
        )

    def _clear_diff_container(self) -> None:
        """Clear all widgets from diff container."""
        while self.diff_layout.count():
            item = self.diff_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def set_diff(self, diff_text: str, stats: Optional[dict] = None) -> None:
        """
        Set the diff content to display.

        Args:
            diff_text: Raw unified diff text
            stats: Optional dictionary with 'files_changed', 'insertions', 'deletions'
        """
        self._current_diff = diff_text
        self._current_line = 0

        # Update stats display with enhanced formatting
        if stats:
            files = stats.get('files_changed', 0)
            insertions = stats.get('insertions', 0)
            deletions = stats.get('deletions', 0)
            
            # Create a more informative stats display
            file_text = "file" if files == 1 else "files"
            stats_html = (
                f'<span style="color: #24292e; font-weight: bold;">'
                f'{files} {file_text} changed</span>'
                f' &nbsp;|&nbsp; '
                f'<span style="color: #28a745; font-weight: bold;">+{insertions}</span>'
                f' <span style="color: #28a745;">additions</span>'
                f' &nbsp;|&nbsp; '
                f'<span style="color: #d73a49; font-weight: bold;">-{deletions}</span>'
                f' <span style="color: #d73a49;">deletions</span>'
            )
            self.stats_label.setText(stats_html)
        else:
            self.stats_label.setText('<span style="color: #586069;">Diff loaded</span>')

        # Render based on current view mode
        self._render_diff()

        self.diff_changed.emit()

    def _render_diff(self) -> None:
        """Render the diff based on current view mode."""
        if self._view_mode == "unified":
            self._render_unified_diff()
        else:
            self._render_side_by_side_diff()

    def _render_unified_diff(self) -> None:
        """Render diff in unified view with enhanced formatting."""
        if hasattr(self, "unified_text"):
            display_text = self._current_diff

            # Apply collapse unchanged if enabled
            if self._collapse_unchanged:
                display_text = self._collapse_unchanged_sections(display_text)
            
            # Add better visual separation between files
            display_text = self._enhance_diff_formatting(display_text)

            self.unified_text.setPlainText(display_text)

    def _enhance_diff_formatting(self, diff_text: str) -> str:
        """Enhance diff formatting with better visual separators."""
        if not diff_text:
            return diff_text
            
        lines = diff_text.split("\n")
        enhanced_lines = []
        
        for i, line in enumerate(lines):
            # Add visual separator before each file
            if line.startswith("diff --git"):
                if i > 0:  # Don't add separator before first file
                    enhanced_lines.append("")  # Empty line for spacing
                    enhanced_lines.append("=" * 80)  # Separator line
                    enhanced_lines.append("")  # Empty line for spacing
            
            enhanced_lines.append(line)
        
        return "\n".join(enhanced_lines)

    def _render_side_by_side_diff(self) -> None:
        """Render diff in side-by-side view."""
        if not hasattr(self, "left_text") or not hasattr(self, "right_text"):
            return

        # Parse diff into left (old) and right (new) sides
        left_lines, right_lines = self._parse_side_by_side(self._current_diff)

        self.left_text.setPlainText("\n".join(left_lines))
        self.right_text.setPlainText("\n".join(right_lines))

        # Apply highlighting manually for deleted/added lines
        self._highlight_side_by_side()

    def _parse_side_by_side(self, diff_text: str) -> tuple[List[str], List[str]]:
        """
        Parse unified diff into two side-by-side views.

        Returns:
            Tuple of (left_lines, right_lines)
        """
        left_lines = []
        right_lines = []

        for line in diff_text.split("\n"):
            if (
                line.startswith("---")
                or line.startswith("+++")
                or line.startswith("diff --git")
                or line.startswith("index ")
            ):
                # File headers - show on both sides
                left_lines.append(line)
                right_lines.append(line)
            elif line.startswith("@@"):
                # Hunk header - show on both sides
                left_lines.append(line)
                right_lines.append(line)
            elif line.startswith("-"):
                # Deleted line - only on left
                left_lines.append(line)
                right_lines.append("")  # Empty on right
            elif line.startswith("+"):
                # Added line - only on right
                left_lines.append("")  # Empty on left
                right_lines.append(line)
            else:
                # Context line - show on both sides
                left_lines.append(line)
                right_lines.append(line)

        return left_lines, right_lines

    def _highlight_side_by_side(self) -> None:
        """Apply highlighting to side-by-side view."""
        # Highlight deleted lines in left pane
        left_cursor = self.left_text.textCursor()
        left_cursor.select(left_cursor.SelectionType.Document)

        # Highlight added lines in right pane
        right_cursor = self.right_text.textCursor()
        right_cursor.select(right_cursor.SelectionType.Document)

    def _collapse_unchanged_sections(self, diff_text: str) -> str:
        """
        Collapse unchanged context sections in the diff.

        Args:
            diff_text: Raw diff text

        Returns:
            Diff text with collapsed unchanged sections
        """
        lines = diff_text.split("\n")
        result: List[str] = []
        context_buffer: List[str] = []
        context_lines = 3  # Show 3 lines of context around changes

        for line in lines:
            # Always show headers and changed lines
            if (
                line.startswith("diff --git")
                or line.startswith("---")
                or line.startswith("+++")
                or line.startswith("@@")
                or line.startswith("+")
                or line.startswith("-")
            ):

                # Add buffered context
                if len(context_buffer) > context_lines * 2:
                    # Too many context lines - collapse middle
                    result.extend(context_buffer[:context_lines])
                    result.append(
                        f"... ({len(context_buffer) - context_lines * 2} unchanged lines) ..."
                    )
                    result.extend(context_buffer[-context_lines:])
                else:
                    result.extend(context_buffer)

                context_buffer = []
                result.append(line)
            else:
                # Buffer context lines
                context_buffer.append(line)

        # Add remaining context
        if context_buffer:
            if len(context_buffer) > context_lines:
                result.extend(context_buffer[:context_lines])
                result.append(f"... ({len(context_buffer) - context_lines} unchanged lines) ...")
            else:
                result.extend(context_buffer)

        return "\n".join(result)

    def navigate_to_next_diff(self) -> None:
        """Navigate to the next difference in the diff."""
        if not self._current_diff:
            return

        lines = self._current_diff.split("\n")

        # Find next hunk header (@@)
        for i in range(self._current_line + 1, len(lines)):
            if lines[i].startswith("@@"):
                self._current_line = i
                self._scroll_to_line(i)
                return

        # If no next hunk, stay at current position
        # Could show a message that we're at the end

    def navigate_to_previous_diff(self) -> None:
        """Navigate to the previous difference in the diff."""
        if not self._current_diff:
            return

        lines = self._current_diff.split("\n")

        # Find previous hunk header (@@)
        for i in range(self._current_line - 1, -1, -1):
            if lines[i].startswith("@@"):
                self._current_line = i
                self._scroll_to_line(i)
                return

        # If no previous hunk, stay at current position

    def _scroll_to_line(self, line_number: int) -> None:
        """Scroll to a specific line number."""
        if self._view_mode == "unified" and hasattr(self, "unified_text"):
            # Move cursor to line
            cursor = self.unified_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            for _ in range(line_number):
                cursor.movePosition(cursor.MoveOperation.Down)

            self.unified_text.setTextCursor(cursor)
            self.unified_text.ensureCursorVisible()

    def _on_view_mode_changed(self, mode: str) -> None:
        """Handle view mode change."""
        if mode == "Unified":
            self._view_mode = "unified"
            self._create_unified_view()
        else:
            self._view_mode = "side-by-side"
            self._create_side_by_side_view()

        # Re-render with new view mode
        self._render_diff()

    def _toggle_line_numbers(self) -> None:
        """Toggle line numbers display."""
        self._show_line_numbers = not self._show_line_numbers
        self.line_numbers_btn.setText(f"Line Numbers: {'ON' if self._show_line_numbers else 'OFF'}")
        # Note: Full line numbers implementation would require custom painting
        # This is a placeholder for the toggle functionality

    def _toggle_collapse_unchanged(self) -> None:
        """Toggle collapse unchanged sections."""
        self._collapse_unchanged = not self._collapse_unchanged
        self._render_diff()

    def clear(self) -> None:
        """Clear the diff viewer."""
        self._current_diff = ""
        self._current_line = 0

        if hasattr(self, "unified_text"):
            self.unified_text.clear()

        if hasattr(self, "left_text"):
            self.left_text.clear()

        if hasattr(self, "right_text"):
            self.right_text.clear()

        self.stats_label.setText("No diff loaded")

    def get_current_diff(self) -> str:
        """Get the current diff text."""
        return self._current_diff

    def set_file_path(self, file_path: str) -> None:
        """Set the current file path being viewed."""
        self._current_file_path = file_path

    def _show_context_menu(self, pos) -> None:
        """Show context menu for staging/unstaging operations."""
        if not hasattr(self, "unified_text"):
            return

        cursor = self.unified_text.textCursor()
        if not cursor.hasSelection():
            return

        # Get selected text
        selected_text = cursor.selectedText()

        # Check if selection contains diff hunks
        if not self._has_diff_content(selected_text):
            return

        menu = QMenu(self)

        stage_action = menu.addAction("Stage Selected Lines")
        unstage_action = menu.addAction("Unstage Selected Lines")

        action = menu.exec(self.unified_text.mapToGlobal(pos))

        if action == stage_action:
            self._stage_selection()
        elif action == unstage_action:
            self._unstage_selection()

    def _has_diff_content(self, text: str) -> bool:
        """Check if text contains actual diff content (not just headers)."""
        lines = text.split("\u2029")  # QTextEdit uses paragraph separator
        for line in lines:
            if line.startswith("+") or line.startswith("-"):
                if not line.startswith("+++") and not line.startswith("---"):
                    return True
        return False

    def _stage_selection(self) -> None:
        """Stage the selected lines."""
        if not hasattr(self, "unified_text") or not self._current_file_path:
            return

        try:
            cursor = self.unified_text.textCursor()
            if not cursor.hasSelection():
                QMessageBox.warning(self, "No Selection", "Please select lines to stage.")
                return

            # Get selected text and convert to patch
            patch = self._create_patch_from_selection()

            if patch:
                self.stage_hunk_requested.emit(patch)
                QMessageBox.information(self, "Success", "Selected lines staged successfully.")
            else:
                QMessageBox.warning(
                    self, "Invalid Selection", "Could not create patch from selection."
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stage selection: {e}")

    def _unstage_selection(self) -> None:
        """Unstage the selected lines."""
        if not hasattr(self, "unified_text") or not self._current_file_path:
            return

        try:
            cursor = self.unified_text.textCursor()
            if not cursor.hasSelection():
                QMessageBox.warning(self, "No Selection", "Please select lines to unstage.")
                return

            # Get selected text and convert to patch
            patch = self._create_patch_from_selection()

            if patch:
                self.unstage_hunk_requested.emit(patch)
                QMessageBox.information(self, "Success", "Selected lines unstaged successfully.")
            else:
                QMessageBox.warning(
                    self, "Invalid Selection", "Could not create patch from selection."
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to unstage selection: {e}")

    def _create_patch_from_selection(self) -> Optional[str]:
        """Create a patch from the current selection."""
        cursor = self.unified_text.textCursor()
        selected_text = cursor.selectedText()

        # Replace paragraph separator with newline
        selected_text = selected_text.replace("\u2029", "\n")

        # Check if selection contains a hunk header
        if "@@" not in selected_text:
            return None

        # Parse hunks from the selection
        hunks = parse_diff_hunks(selected_text)

        if not hunks or not self._current_file_path:
            return None

        # Extract index line from current diff for proper patch creation
        index_line = extract_index_line_from_diff(self._current_diff)

        # Create patch from the first hunk (simplified approach)
        # In a more sophisticated implementation, we would handle multiple hunks
        patch = create_patch_from_hunk(self._current_file_path, hunks[0], index_line=index_line)

        return patch

    def stage_hunk_at_cursor(self) -> None:
        """Stage the hunk at the current cursor position."""
        if not hasattr(self, "unified_text") or not self._current_file_path:
            return

        try:
            cursor = self.unified_text.textCursor()
            line_number = cursor.blockNumber()

            # Find the hunk at this line
            hunks = parse_diff_hunks(self._current_diff)

            # Find which hunk contains this line by checking line positions in diff text
            lines = self._current_diff.split("\n")
            target_hunk = None

            for hunk in hunks:
                # Find the position of this hunk's header in the diff
                for idx, line in enumerate(lines):
                    if line == hunk.header:
                        # Check if cursor is within this hunk's range
                        hunk_end = idx + len(hunk.lines)
                        if idx <= line_number <= hunk_end:
                            target_hunk = hunk
                            break

                if target_hunk:
                    break

            if target_hunk:
                index_line = extract_index_line_from_diff(self._current_diff)
                patch = create_patch_from_hunk(
                    self._current_file_path, target_hunk, index_line=index_line
                )
                self.stage_hunk_requested.emit(patch)
                QMessageBox.information(self, "Success", "Hunk staged successfully.")
            else:
                QMessageBox.warning(self, "No Hunk", "No hunk found at cursor position.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stage hunk: {e}")

    def unstage_hunk_at_cursor(self) -> None:
        """Unstage the hunk at the current cursor position."""
        if not hasattr(self, "unified_text") or not self._current_file_path:
            return

        try:
            cursor = self.unified_text.textCursor()
            line_number = cursor.blockNumber()

            # Find the hunk at this line
            hunks = parse_diff_hunks(self._current_diff)

            # Find which hunk contains this line by checking line positions in diff text
            lines = self._current_diff.split("\n")
            target_hunk = None

            for hunk in hunks:
                # Find the position of this hunk's header in the diff
                for idx, line in enumerate(lines):
                    if line == hunk.header:
                        # Check if cursor is within this hunk's range
                        hunk_end = idx + len(hunk.lines)
                        if idx <= line_number <= hunk_end:
                            target_hunk = hunk
                            break

                if target_hunk:
                    break

            if target_hunk:
                index_line = extract_index_line_from_diff(self._current_diff)
                patch = create_patch_from_hunk(
                    self._current_file_path, target_hunk, index_line=index_line
                )
                self.unstage_hunk_requested.emit(patch)
                QMessageBox.information(self, "Success", "Hunk unstaged successfully.")
            else:
                QMessageBox.warning(self, "No Hunk", "No hunk found at cursor position.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to unstage hunk: {e}")
