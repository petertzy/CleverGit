"""
Repository tab widget that encapsulates all repository-specific UI and state.
"""

from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QTabWidget,
)
from PySide6.QtCore import Qt, Signal

from clevergit.core.repo import Repo
from clevergit.core.log import get_log
from clevergit.ui.widgets.repo_view import RepositoryView
from clevergit.ui.widgets.status_view import StatusView
from clevergit.ui.widgets.branch_view import BranchView
from clevergit.ui.widgets.log_view import LogView
from clevergit.ui.widgets.graph_view import CommitGraphView
from clevergit.ui.widgets.stash_view import StashView
from clevergit.ui.widgets.tag_view import TagView
from clevergit.ui.widgets.github_panel import GitHubPanel
from clevergit.ui.widgets.gitlab_panel import GitLabPanel


class RepositoryTab(QWidget):
    """Widget containing all views and state for a single repository."""
    
    # Signals
    file_selected = Signal(str)  # Emitted when a file is selected
    commit_selected = Signal(str)  # Emitted when a commit is selected
    state_changed = Signal()  # Emitted when tab state changes
    
    def __init__(self, repo_path: str, parent=None) -> None:
        super().__init__(parent)
        self.repo: Optional[Repo] = None
        self.repo_path = Path(repo_path)
        self._commit_cache: Optional[List] = None
        self._selected_file: Optional[str] = None
        
        self._setup_ui()
        self._load_repository()
    
    def _setup_ui(self) -> None:
        """Setup the tab UI layout."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Repository info and branches
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Repository Info"))
        self.repo_view = RepositoryView()
        left_layout.addWidget(self.repo_view)
        
        # Create tabs for branches/stashes/tags/github/gitflow
        self.left_tabs = QTabWidget()
        
        # Branches tab
        self.branch_view = BranchView(self)
        self.left_tabs.addTab(self.branch_view, "Branches")
        
        # Stashes tab
        self.stash_view = StashView(self)
        self.left_tabs.addTab(self.stash_view, "Stashes")
        
        # Tags tab
        self.tag_view = TagView(self)
        self.left_tabs.addTab(self.tag_view, "Tags")
        
        # GitHub tab
        self.github_panel = GitHubPanel()
        self.left_tabs.addTab(self.github_panel, "GitHub")
        
        # GitLab tab
        self.gitlab_panel = GitLabPanel()
        self.left_tabs.addTab(self.gitlab_panel, "GitLab")
        
        # Git Flow tab
        from clevergit.ui.widgets.git_flow_panel import GitFlowPanel
        self.git_flow_panel = GitFlowPanel()
        self.left_tabs.addTab(self.git_flow_panel, "Git Flow")
        
        left_layout.addWidget(self.left_tabs)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Right panel: Status and Log
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        right_layout.addWidget(QLabel("File Status"))
        self.status_view = StatusView()
        self.status_view.tree.itemClicked.connect(self._on_file_selected)
        right_layout.addWidget(self.status_view)
        
        right_layout.addWidget(QLabel("Commit History"))
        self.history_tabs = QTabWidget()
        
        # Log table view
        self.log_view = LogView()
        self.log_view.table.itemClicked.connect(self._on_commit_selected)
        self.history_tabs.addTab(self.log_view, "List View")
        
        # Graph view
        self.graph_view = CommitGraphView()
        self.graph_view.commit_selected.connect(self._on_graph_commit_selected)
        self.history_tabs.addTab(self.graph_view, "Graph View")
        
        right_layout.addWidget(self.history_tabs)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
    
    def _load_repository(self) -> None:
        """Load the repository and initialize views."""
        try:
            from clevergit.git.errors import RepoNotFoundError
            self.repo = Repo.open(str(self.repo_path))
            self.refresh()
        except (RepoNotFoundError, Exception):
            pass
    
    def refresh(self) -> None:
        """Refresh all views with current repository state."""
        if not self.repo:
            return
        
        try:
            # Update repository view
            current_branch = self.repo.current_branch()
            is_clean = self.repo.is_clean()
            self.repo_view.update_info(
                str(self.repo_path),
                current_branch or "unknown",
                "Clean" if is_clean else "Dirty",
            )
            
            # Update status view
            status = self.repo.status()
            self.status_view.update_status(status)
            
            # Update branch view
            branches = self.repo.list_branches()
            self.branch_view.update_branches(branches)
            
            # Update stash view
            stashes = self.repo.stash_list()
            self.stash_view.update_stashes(stashes)
            
            # Update tag view
            tags = self.repo.list_tags()
            self.tag_view.update_tags(tags)
            
            # Update GitHub panel
            self.github_panel.set_repository(self.repo)
            
            # Update GitLab panel
            self.gitlab_panel.set_repository(self.repo)
            
            # Update Git Flow panel
            self.git_flow_panel.set_repository(self.repo)
            
            # Update log view and graph view
            log = self.repo.log(max_count=100)
            self.log_view.update_log(log[:20])
            
            # Update graph view with CommitInfo objects
            commits = get_log(self.repo_path, max_count=100)
            self.graph_view.update_commits(commits)
            
            # Cache commits
            self._commit_cache = log
            
            self.state_changed.emit()
            
        except Exception:
            pass
    
    def _on_file_selected(self, item, column) -> None:
        """Handle file selection in status view."""
        if not self.repo or not item.parent():
            return
        
        file_name = item.text(0)
        self._selected_file = file_name
        self.file_selected.emit(file_name)
    
    def _on_commit_selected(self, item) -> None:
        """Handle commit selection in log view."""
        if not self.repo:
            return
        
        commit_hash = item.text(0)
        
        # Find full SHA from cache
        commit_sha = None
        if self._commit_cache:
            for commit in self._commit_cache:
                if hasattr(commit, "short_sha") and commit.short_sha == commit_hash:
                    commit_sha = commit.sha
                    break
        
        if not commit_sha:
            commits = get_log(self.repo_path, max_count=100)
            for commit in commits:
                if commit.short_sha == commit_hash:
                    commit_sha = commit.sha
                    break
        
        if commit_sha:
            self.commit_selected.emit(commit_sha)
    
    def _on_graph_commit_selected(self, commit_sha: str) -> None:
        """Handle commit selection from graph view."""
        if self.repo:
            self.commit_selected.emit(commit_sha)
    
    def get_repo_name(self) -> str:
        """Get the repository name for display."""
        return self.repo_path.name if self.repo_path.name else self.repo_path.as_posix()
    
    @property
    def current_path(self) -> Path:
        """
        Get the current repository path.
        
        This is an alias for repo_path for backward compatibility.
        
        Returns:
            Path: The repository path
        """
        return self.repo_path
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
        if self.repo:
            try:
                return self.repo.current_branch()
            except Exception:
                pass
        return None
    
    def is_stash_visible(self) -> bool:
        """Check if stash view is visible."""
        return self.stash_view.isVisible()
    
    def toggle_stash_view(self) -> None:
        """Toggle stash view visibility."""
        self.stash_view.setVisible(not self.stash_view.isVisible())
        self.state_changed.emit()
    
    def is_tag_visible(self) -> bool:
        """Check if tag view is visible."""
        return self.tag_view.isVisible()
    
    def toggle_tag_view(self) -> None:
        """Toggle tag view visibility."""
        self.tag_view.setVisible(not self.tag_view.isVisible())
        self.state_changed.emit()
    
    def get_selected_file(self) -> Optional[str]:
        """Get the currently selected file."""
        return self._selected_file
    
    def save_branch_to_settings(self, branch_name: str) -> None:
        """
        Save the current branch to settings if parent MainWindow has settings.
        
        Args:
            branch_name: Name of the branch to save
        """
        parent = self.parent()
        if parent and hasattr(parent, 'settings'):
            parent.settings.set_repository_branch(str(self.repo_path), branch_name)
