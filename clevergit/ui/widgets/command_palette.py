"""
Command palette widget for quick search and command execution.
"""

from typing import Optional, List, Dict, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QWidget,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SearchCategory(Enum):
    """Categories for search results."""
    FILE = "📄 File"
    COMMIT = "📝 Commit"
    BRANCH = "🌿 Branch"
    COMMAND = "⚡ Command"


@dataclass
class SearchResult:
    """Represents a search result item."""
    category: SearchCategory
    title: str
    description: str
    data: Any = None
    score: float = 0.0


class FuzzyMatcher:
    """Simple fuzzy matching algorithm for search."""
    
    @staticmethod
    def match(pattern: str, text: str) -> Tuple[bool, float]:
        """
        Perform fuzzy matching between pattern and text.
        
        Args:
            pattern: Search pattern (query)
            text: Text to match against
            
        Returns:
            Tuple of (matches, score) where score is 0.0-1.0
        """
        if not pattern:
            return True, 1.0
        
        pattern = pattern.lower()
        text = text.lower()
        
        # Exact match - highest score
        if pattern == text:
            return True, 1.0
        
        # Contains match
        if pattern in text:
            # Score based on position and length
            position_score = 1.0 - (text.index(pattern) / len(text))
            length_score = len(pattern) / len(text)
            return True, (position_score * 0.3 + length_score * 0.7)
        
        # Character-by-character fuzzy match
        pattern_idx = 0
        text_idx = 0
        matches = []
        
        while pattern_idx < len(pattern) and text_idx < len(text):
            if pattern[pattern_idx] == text[text_idx]:
                matches.append(text_idx)
                pattern_idx += 1
            text_idx += 1
        
        # All pattern characters must be found in order
        if pattern_idx != len(pattern):
            return False, 0.0
        
        # Score based on consecutive matches and gaps
        consecutive_bonus = 0
        for i in range(len(matches) - 1):
            if matches[i + 1] == matches[i] + 1:
                consecutive_bonus += 0.1
        
        base_score = len(pattern) / len(text)
        final_score = min(1.0, base_score * 0.5 + consecutive_bonus)
        
        return True, final_score


class CommandPalette(QDialog):
    """
    Command palette for quick search and command execution.
    
    Provides fuzzy search for:
    - Files in the repository
    - Commits
    - Branches
    - Quick commands
    """
    
    # Signals
    file_selected = Signal(str)  # Emitted when a file is selected
    commit_selected = Signal(str)  # Emitted when a commit is selected
    branch_selected = Signal(str)  # Emitted when a branch is selected
    command_executed = Signal(str)  # Emitted when a command is executed
    
    def __init__(self, parent: Optional[QWidget] = None, repo=None) -> None:
        """
        Initialize command palette.
        
        Args:
            parent: Parent widget
            repo: Repository instance for searching
        """
        super().__init__(parent)
        self.repo = repo
        self._all_results: List[SearchResult] = []
        self._filtered_results: List[SearchResult] = []
        self._commands: Dict[str, Callable] = {}
        
        self.setWindowTitle("Command Palette")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self._setup_ui()
        self._load_available_items()
        self._register_default_commands()
        
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header with instructions
        header = QLabel("🔍 Search files, commits, branches, or type a command...")
        header_font = QFont()
        header_font.setPointSize(10)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search...")
        self.search_input.textChanged.connect(self._on_search_changed)
        input_font = QFont()
        input_font.setPointSize(12)
        self.search_input.setFont(input_font)
        layout.addWidget(self.search_input)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemActivated.connect(self._on_item_activated)
        self.results_list.itemClicked.connect(self._on_item_activated)
        layout.addWidget(self.results_list)
        
        # Footer with shortcuts
        footer_layout = QHBoxLayout()
        footer = QLabel("↑↓ Navigate | Enter Select | Esc Close")
        footer.setStyleSheet("color: gray;")
        footer_layout.addWidget(footer)
        layout.addLayout(footer_layout)
        
        # Set initial focus to search input
        self.search_input.setFocus()
    
    def _register_default_commands(self) -> None:
        """Register default quick commands."""
        self._commands = {
            "refresh": lambda: self.command_executed.emit("refresh"),
            "commit": lambda: self.command_executed.emit("commit"),
            "pull": lambda: self.command_executed.emit("pull"),
            "push": lambda: self.command_executed.emit("push"),
            "fetch": lambda: self.command_executed.emit("fetch"),
            "checkout": lambda: self.command_executed.emit("checkout"),
            "merge": lambda: self.command_executed.emit("merge"),
            "stash": lambda: self.command_executed.emit("stash"),
            "tag": lambda: self.command_executed.emit("tag"),
            "diff": lambda: self.command_executed.emit("diff"),
            "blame": lambda: self.command_executed.emit("blame"),
        }
        
    def register_command(self, name: str, callback: Callable) -> None:
        """
        Register a custom command.
        
        Args:
            name: Command name
            callback: Function to call when command is executed
        """
        self._commands[name] = callback
        
    def _load_available_items(self) -> None:
        """Load all searchable items (files, commits, branches, commands)."""
        self._all_results = []
        
        if self.repo is None:
            # Add commands only if no repo is available
            self._load_commands()
            return
        
        try:
            # Load files
            self._load_files()
            
            # Load recent commits
            self._load_commits()
            
            # Load branches
            self._load_branches()
            
            # Load commands
            self._load_commands()
            
        except Exception as e:
            print(f"Error loading items: {e}")
            # Still load commands even if repo operations fail
            self._load_commands()
    
    def _load_files(self) -> None:
        """Load files from repository."""
        try:
            # Get tracked files using git ls-files
            import subprocess
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.repo.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                for file_path in files[:500]:  # Limit to 500 files for performance
                    if file_path:
                        self._all_results.append(SearchResult(
                            category=SearchCategory.FILE,
                            title=file_path,
                            description=f"File: {file_path}",
                            data=file_path
                        ))
        except Exception as e:
            print(f"Error loading files: {e}")
    
    def _load_commits(self, max_count: int = 100) -> None:
        """Load recent commits."""
        try:
            commits = self.repo.log(max_count=max_count)
            for commit in commits:
                # Format: short SHA + message
                short_sha = commit.sha[:7] if len(commit.sha) > 7 else commit.sha
                title = f"{short_sha} {commit.message}"
                description = f"By {commit.author} on {commit.date.strftime('%Y-%m-%d')}"
                
                self._all_results.append(SearchResult(
                    category=SearchCategory.COMMIT,
                    title=title,
                    description=description,
                    data=commit.sha
                ))
        except Exception as e:
            print(f"Error loading commits: {e}")
    
    def _load_branches(self) -> None:
        """Load branches."""
        try:
            branches = self.repo.list_branches()
            for branch in branches:
                marker = "✓ " if branch.is_current else ""
                title = f"{marker}{branch.name}"
                description = f"Branch: {branch.name}"
                
                self._all_results.append(SearchResult(
                    category=SearchCategory.BRANCH,
                    title=title,
                    description=description,
                    data=branch.name
                ))
        except Exception as e:
            print(f"Error loading branches: {e}")
    
    def _load_commands(self) -> None:
        """Load available commands."""
        for cmd_name in self._commands.keys():
            self._all_results.append(SearchResult(
                category=SearchCategory.COMMAND,
                title=cmd_name,
                description=f"Command: {cmd_name}",
                data=cmd_name
            ))
    
    def _on_search_changed(self, text: str) -> None:
        """Handle search text change."""
        self._filter_results(text)
        self._update_results_display()
        
        # Auto-select first item
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
    
    def _filter_results(self, query: str) -> None:
        """Filter results based on search query."""
        if not query:
            # Show all results if query is empty
            self._filtered_results = self._all_results[:50]  # Limit to 50 for performance
            return
        
        # Apply fuzzy matching
        matches: List[Tuple[SearchResult, float]] = []
        for result in self._all_results:
            # Match against both title and description
            title_match, title_score = FuzzyMatcher.match(query, result.title)
            desc_match, desc_score = FuzzyMatcher.match(query, result.description)
            
            if title_match or desc_match:
                # Use the higher score
                score = max(title_score, desc_score * 0.8)  # Slight preference for title matches
                matches.append((result, score))
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 50 results
        self._filtered_results = [result for result, score in matches[:50]]
    
    def _update_results_display(self) -> None:
        """Update the results list display."""
        self.results_list.clear()
        
        if not self._filtered_results:
            item = QListWidgetItem("No results found")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.results_list.addItem(item)
            return
        
        for result in self._filtered_results:
            # Create list item with category icon and title
            display_text = f"{result.category.value}: {result.title}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)
    
    def _on_item_activated(self, item: QListWidgetItem) -> None:
        """Handle item selection."""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result is None:
            return
        
        # Handle different result types
        if result.category == SearchCategory.FILE:
            self.file_selected.emit(result.data)
            self.accept()
        elif result.category == SearchCategory.COMMIT:
            self.commit_selected.emit(result.data)
            self.accept()
        elif result.category == SearchCategory.BRANCH:
            self.branch_selected.emit(result.data)
            self.accept()
        elif result.category == SearchCategory.COMMAND:
            # Execute command
            if result.data in self._commands:
                self._commands[result.data]()
            self.accept()
    
    def keyPressEvent(self, event) -> None:
        """Handle key press events for navigation."""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Down:
            # Move to next item
            current = self.results_list.currentRow()
            if current < self.results_list.count() - 1:
                self.results_list.setCurrentRow(current + 1)
            event.accept()
        elif event.key() == Qt.Key.Key_Up:
            # Move to previous item
            current = self.results_list.currentRow()
            if current > 0:
                self.results_list.setCurrentRow(current - 1)
            event.accept()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Activate current item
            current_item = self.results_list.currentItem()
            if current_item:
                self._on_item_activated(current_item)
            event.accept()
        else:
            # Pass other events to parent
            super().keyPressEvent(event)
