"""
Main application window for CleverGit GUI.
"""

from pathlib import Path
from typing import Optional, List, Literal
import uuid

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QLabel,
    QTabWidget,
    QMenu,
    QApplication,
)
from PySide6.QtCore import Qt

from clevergit.core.repo import Repo
from clevergit.git.errors import RepoNotFoundError
from clevergit.ui.settings import Settings
from clevergit.ui.shortcuts import ShortcutManager
from clevergit.ui.widgets.repository_tab import RepositoryTab
from clevergit.ui.widgets.welcome_screen import WelcomeScreen
from clevergit.ui.widgets.commit_dialog import CommitDialog
from clevergit.ui.widgets.clone_dialog import CloneDialog
from clevergit.ui.widgets.diff_viewer import DiffViewer
from clevergit.ui.widgets.blame_view import BlameView
from clevergit.ui.widgets.shortcuts_dialog import ShortcutHelpDialog
from clevergit.ui.widgets.command_palette import CommandPalette

# Global list to track all open windows
_windows: List["MainWindow"] = []

# Default fallback screen dimensions (typical small laptop resolution)
# Used when screen detection fails
_DEFAULT_SCREEN_WIDTH = 1366
_DEFAULT_SCREEN_HEIGHT = 768

# Screen size thresholds for adaptive sizing
# Screens smaller than these thresholds use reduced percentages
_SMALL_SCREEN_WIDTH_THRESHOLD = 1366
_SMALL_SCREEN_HEIGHT_THRESHOLD = 768

# Maximum window size as percentage of screen
# Ensures windows don't feel too large on any screen
_MAX_MAIN_WINDOW_SCREEN_PCT = 0.90  # Main window: 90% of screen max
_MAX_DIALOG_SCREEN_PCT = 0.85  # Dialogs: 85% of screen max

# Adaptive window sizing percentages
# Main window percentages
_MAIN_WINDOW_WIDTH_PCT_LARGE = 0.75  # For screens >= 1366px wide
_MAIN_WINDOW_WIDTH_PCT_SMALL = 0.70  # For screens < 1366px wide
_MAIN_WINDOW_HEIGHT_PCT_LARGE = 0.85  # For screens >= 768px tall
_MAIN_WINDOW_HEIGHT_PCT_SMALL = 0.80  # For screens < 768px tall

# Diff dialog percentages
_DIFF_WINDOW_WIDTH_PCT_LARGE = 0.65  # For screens >= 1366px wide
_DIFF_WINDOW_WIDTH_PCT_SMALL = 0.60  # For screens < 1366px wide
_DIFF_WINDOW_HEIGHT_PCT_LARGE = 0.75  # For screens >= 768px tall
_DIFF_WINDOW_HEIGHT_PCT_SMALL = 0.70  # For screens < 768px tall

# Blame dialog percentages
_BLAME_WINDOW_WIDTH_PCT_LARGE = 0.70  # For screens >= 1366px wide
_BLAME_WINDOW_WIDTH_PCT_SMALL = 0.65  # For screens < 1366px wide
_BLAME_WINDOW_HEIGHT_PCT_LARGE = 0.75  # For screens >= 768px tall
_BLAME_WINDOW_HEIGHT_PCT_SMALL = 0.70  # For screens < 768px tall

# Absolute minimum and maximum window dimensions (in pixels)
# Main window limits
_MIN_MAIN_WINDOW_WIDTH = 800
_MAX_MAIN_WINDOW_WIDTH = 1400
_MIN_MAIN_WINDOW_HEIGHT = 500
_MAX_MAIN_WINDOW_HEIGHT = 900

# Diff dialog limits
_MIN_DIFF_WINDOW_WIDTH = 700
_MAX_DIFF_WINDOW_WIDTH = 1200
_MIN_DIFF_WINDOW_HEIGHT = 450
_MAX_DIFF_WINDOW_HEIGHT = 800

# Blame dialog limits
_MIN_BLAME_WINDOW_WIDTH = 750
_MAX_BLAME_WINDOW_WIDTH = 1300
_MIN_BLAME_WINDOW_HEIGHT = 450
_MAX_BLAME_WINDOW_HEIGHT = 800

# Window type constants
WINDOW_TYPE_MAIN = "main"
WINDOW_TYPE_DIFF = "diff"
WINDOW_TYPE_BLAME = "blame"


class MainWindow(QMainWindow):
    """Main application window with multi-tab and multi-window support."""

    def __init__(self, window_id: Optional[str] = None) -> None:
        super().__init__()
        self.window_id = window_id or str(uuid.uuid4())
        self.settings = Settings()
        self.shortcut_manager = ShortcutManager(self.settings)
        self._diff_dialogs: list = []
        self._blame_windows: list = []

        # Track this window
        _windows.append(self)

        self.setWindowTitle("CleverGit")

        self._setup_ui()
        self._restore_window_geometry()
        self._setup_menu()
        self._setup_shortcuts()
        self._restore_session()

    def _setup_ui(self) -> None:
        """Setup the main UI layout with tab support."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Top toolbar
        toolbar_layout = QHBoxLayout()

        self.clone_button = QPushButton("⬇️ Clone")
        self.clone_button.clicked.connect(self._clone_repository)
        toolbar_layout.addWidget(self.clone_button)

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

        self.pull_button = QPushButton("⬇️ Pull")
        self.pull_button.clicked.connect(self._pull)
        self.pull_button.setEnabled(False)
        toolbar_layout.addWidget(self.pull_button)

        self.push_button = QPushButton("⬆️ Push")
        self.push_button.clicked.connect(self._push)
        self.push_button.setEnabled(False)
        toolbar_layout.addWidget(self.push_button)

        self.diff_button = QPushButton("📊 View Diff")
        self.diff_button.clicked.connect(self._show_diff_viewer)
        self.diff_button.setEnabled(False)
        toolbar_layout.addWidget(self.diff_button)

        self.stash_button = QPushButton("📦 Stash")
        self.stash_button.clicked.connect(self._toggle_stash_view)
        self.stash_button.setEnabled(False)
        toolbar_layout.addWidget(self.stash_button)

        self.tag_button = QPushButton("🏷️ Tags")
        self.tag_button.clicked.connect(self._toggle_tag_view)
        self.tag_button.setEnabled(False)
        toolbar_layout.addWidget(self.tag_button)

        self.blame_button = QPushButton("👤 Blame")
        self.blame_button.clicked.connect(self._show_blame_for_file)
        self.blame_button.setEnabled(False)
        toolbar_layout.addWidget(self.blame_button)

        self.path_label = QLabel("No repository opened")
        toolbar_layout.addWidget(self.path_label)
        toolbar_layout.addStretch()

        main_layout.addLayout(toolbar_layout)

        # Tab widget for multiple repositories
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self._show_tab_context_menu)

        # Welcome screen (shown when no tabs)
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.open_repository_clicked.connect(self._open_repository)
        self.welcome_screen.clone_repository_clicked.connect(self._clone_repository)

        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.welcome_screen)

        # Initially show welcome screen
        self._update_ui_state()

    def _setup_menu(self) -> None:
        """Setup application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_tab_action = file_menu.addAction("New Tab")
        new_tab_action.triggered.connect(self._open_repository)
        self.shortcut_manager.register_action("file.new_tab", new_tab_action)

        new_window_action = file_menu.addAction("New Window")
        new_window_action.triggered.connect(self._new_window)
        self.shortcut_manager.register_action("file.new_window", new_window_action)

        file_menu.addSeparator()

        clone_action = file_menu.addAction("Clone Repository")
        clone_action.triggered.connect(self._clone_repository)
        self.shortcut_manager.register_action("file.clone", clone_action)

        open_action = file_menu.addAction("Open Repository")
        open_action.triggered.connect(self._open_repository)
        self.shortcut_manager.register_action("file.open", open_action)

        close_tab_action = file_menu.addAction("Close Tab")
        close_tab_action.triggered.connect(self._close_current_tab)
        self.shortcut_manager.register_action("file.close_tab", close_tab_action)

        file_menu.addSeparator()

        # Recent repositories submenu
        self.recent_menu = file_menu.addMenu("Recent Repositories")
        self._update_recent_menu()

        file_menu.addSeparator()

        restore_session_action = file_menu.addAction("Restore Session")
        restore_session_action.triggered.connect(self._restore_session)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        self.shortcut_manager.register_action("file.exit", exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        refresh_action = edit_menu.addAction("Refresh")
        refresh_action.triggered.connect(self._refresh)
        self.shortcut_manager.register_action("edit.refresh", refresh_action)

        edit_menu.addSeparator()

        diff_action = edit_menu.addAction("View Diff")
        diff_action.triggered.connect(self._show_diff_viewer)
        self.shortcut_manager.register_action("edit.view_diff", diff_action)

        blame_action = edit_menu.addAction("Blame File")
        blame_action.triggered.connect(self._show_blame_for_file)
        self.shortcut_manager.register_action("edit.blame", blame_action)

        # Commit menu
        commit_menu = menubar.addMenu("Commit")

        commit_action = commit_menu.addAction("New Commit")
        commit_action.triggered.connect(self._show_commit_dialog)
        self.shortcut_manager.register_action("commit.new", commit_action)

        # Remote menu
        remote_menu = menubar.addMenu("Remote")

        pull_action = remote_menu.addAction("Pull")
        pull_action.triggered.connect(self._pull)
        self.shortcut_manager.register_action("remote.pull", pull_action)

        push_action = remote_menu.addAction("Push")
        push_action.triggered.connect(self._push)
        self.shortcut_manager.register_action("remote.push", push_action)

        # View menu
        view_menu = menubar.addMenu("View")

        command_palette_action = view_menu.addAction("Command Palette")
        command_palette_action.triggered.connect(self._show_command_palette)
        self.shortcut_manager.register_action("search.command_palette", command_palette_action)

        view_menu.addSeparator()

        theme_menu = view_menu.addMenu("Theme")

        light_theme_action = theme_menu.addAction("Light")
        light_theme_action.triggered.connect(lambda: self._set_theme("light"))

        dark_theme_action = theme_menu.addAction("Dark")
        dark_theme_action.triggered.connect(lambda: self._set_theme("dark"))

        theme_menu.addSeparator()

        system_theme_action = theme_menu.addAction("Follow System")
        system_theme_action.triggered.connect(self._use_system_theme)

        # Help menu
        help_menu = menubar.addMenu("Help")

        shortcuts_action = help_menu.addAction("Keyboard Shortcuts")
        shortcuts_action.triggered.connect(self._show_shortcuts_help)
        self.shortcut_manager.register_action("help.shortcuts", shortcuts_action)

        help_menu.addSeparator()

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)

    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts for tab navigation."""
        # Tab navigation shortcuts
        self.shortcut_manager.register_shortcut("tab.next", self, self._next_tab)
        self.shortcut_manager.register_shortcut("tab.previous", self, self._previous_tab)

        # Command palette shortcut
        self.shortcut_manager.register_shortcut(
            "search.command_palette", self, self._show_command_palette
        )

    def _enforce_window_size(self) -> None:
        """Keep the main window aligned to the current screen size."""
        if self.isMaximized():
            return
        x, y, width, height = self._get_adaptive_window_size(WINDOW_TYPE_MAIN)
        self.setGeometry(x, y, width, height)

    def _log_window_size(self) -> None:
        """Log current window size for debugging."""
        pass

    def _final_size_enforcement(self) -> None:
        """Final enforcement of window size after all UI initialization is complete."""
        self._enforce_window_size()

    def _get_current_tab(self) -> Optional[RepositoryTab]:
        """Get the currently active repository tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            return self.tab_widget.widget(current_index)
        return None

    def _update_ui_state(self) -> None:
        """Update UI based on current tab state."""
        has_tabs = self.tab_widget.count() > 0

        # Show/hide welcome screen
        self.welcome_screen.setVisible(not has_tabs)
        self.tab_widget.setVisible(has_tabs)

        # Update toolbar buttons
        current_tab = self._get_current_tab()
        if current_tab and current_tab.repo:
            self.commit_button.setEnabled(True)
            self.pull_button.setEnabled(True)
            self.push_button.setEnabled(True)
            self.diff_button.setEnabled(True)
            self.stash_button.setEnabled(True)
            self.tag_button.setEnabled(True)
            self.refresh_button.setEnabled(True)

            # Update stash/tag button state
            if current_tab.is_stash_visible():
                self.stash_button.setText("📦 Stash ▼")
            else:
                self.stash_button.setText("📦 Stash")

            if current_tab.is_tag_visible():
                self.tag_button.setText("🏷️ Tags ▼")
            else:
                self.tag_button.setText("🏷️ Tags")

            # Enable blame if file is selected
            self.blame_button.setEnabled(current_tab.get_selected_file() is not None)

            # Update path label and window title
            self.path_label.setText(f"📂 {current_tab.repo_path}")
            repo_name = current_tab.get_repo_name()
            branch = current_tab.get_current_branch()
            if branch:
                self.setWindowTitle(f"CleverGit - {repo_name} ({branch})")
            else:
                self.setWindowTitle(f"CleverGit - {repo_name}")
        else:
            self.commit_button.setEnabled(False)
            self.pull_button.setEnabled(False)
            self.push_button.setEnabled(False)
            self.diff_button.setEnabled(False)
            self.stash_button.setEnabled(False)
            self.tag_button.setEnabled(False)
            self.blame_button.setEnabled(False)
            self.refresh_button.setEnabled(False)
            self.path_label.setText("No repository opened")
            self.setWindowTitle("CleverGit")

    def _add_repository_tab(self, repo_path: str) -> None:
        """Add a new repository tab."""
        # Check if repo is already open in a tab
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if isinstance(tab, RepositoryTab) and str(tab.repo_path) == repo_path:
                self.tab_widget.setCurrentIndex(i)
                return

        # Create new tab
        tab = RepositoryTab(repo_path, self)
        tab.file_selected.connect(self._on_tab_file_selected)
        tab.commit_selected.connect(self._on_tab_commit_selected)
        tab.state_changed.connect(self._update_ui_state)

        repo_name = Path(repo_path).name
        index = self.tab_widget.addTab(tab, repo_name)
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.setTabToolTip(index, repo_path)

        # Save to recent and settings
        self.settings.add_recent_repository(repo_path)
        self._update_recent_menu()

        self._update_ui_state()
        self._save_session()

        # Keep the main window matched to screen size after opening a repository
        # Use a timer to ensure layout is complete before resizing
        from PySide6.QtCore import QTimer

        QTimer.singleShot(100, self._enforce_window_size)

    def _close_tab(self, index: int) -> None:
        """Close a tab at the given index."""
        if index < 0 or index >= self.tab_widget.count():
            return

        tab = self.tab_widget.widget(index)
        if isinstance(tab, RepositoryTab) and tab.repo:
            # Save current branch before closing
            try:
                branch = tab.get_current_branch()
                if branch:
                    self.settings.set_repository_branch(str(tab.repo_path), branch)
            except Exception:
                pass

        self.tab_widget.removeTab(index)
        self._update_ui_state()
        self._save_session()

    def _close_current_tab(self) -> None:
        """Close the currently active tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self._close_tab(current_index)

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change."""
        self._update_ui_state()
        self._save_session()

    def _next_tab(self) -> None:
        """Switch to next tab."""
        if self.tab_widget.count() > 0:
            current = self.tab_widget.currentIndex()
            next_index = (current + 1) % self.tab_widget.count()
            self.tab_widget.setCurrentIndex(next_index)

    def _previous_tab(self) -> None:
        """Switch to previous tab."""
        if self.tab_widget.count() > 0:
            current = self.tab_widget.currentIndex()
            prev_index = (current - 1) % self.tab_widget.count()
            self.tab_widget.setCurrentIndex(prev_index)

    def _show_tab_context_menu(self, pos) -> None:
        """Show context menu for tab bar."""
        # Get tab index at position
        tab_bar = self.tab_widget.tabBar()
        index = -1
        for i in range(self.tab_widget.count()):
            if tab_bar.tabRect(i).contains(pos):
                index = i
                break

        if index < 0:
            return

        menu = QMenu(self)

        close_action = menu.addAction("Close")
        close_action.triggered.connect(lambda: self._close_tab(index))

        close_others_action = menu.addAction("Close Others")
        close_others_action.triggered.connect(lambda: self._close_other_tabs(index))

        close_all_action = menu.addAction("Close All")
        close_all_action.triggered.connect(self._close_all_tabs)

        menu.exec(tab_bar.mapToGlobal(pos))

    def _close_other_tabs(self, keep_index: int) -> None:
        """Close all tabs except the one at keep_index."""
        # Close tabs after keep_index
        while self.tab_widget.count() > keep_index + 1:
            self._close_tab(keep_index + 1)

        # Close tabs before keep_index
        while keep_index > 0:
            self._close_tab(0)
            keep_index -= 1

    def _close_all_tabs(self) -> None:
        """Close all tabs."""
        while self.tab_widget.count() > 0:
            self._close_tab(0)

    def _new_window(self) -> None:
        """Create a new main window."""
        window = MainWindow()
        window.show()

    def _save_session(self) -> None:
        """Save current session state."""
        # Save tab list for this window
        tabs = []
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if isinstance(tab, RepositoryTab):
                tabs.append(str(tab.repo_path))

        self.settings.set_open_tabs(tabs, self.window_id)
        self.settings.set_active_tab(self.tab_widget.currentIndex(), self.window_id)

        # Save all windows' session state
        windows_state = []
        for window in _windows:
            tabs = []
            for i in range(window.tab_widget.count()):
                tab = window.tab_widget.widget(i)
                if isinstance(tab, RepositoryTab):
                    tabs.append(str(tab.repo_path))

            windows_state.append(
                {
                    "window_id": window.window_id,
                    "tabs": tabs,
                    "active_tab": window.tab_widget.currentIndex(),
                }
            )

        self.settings.set_session_windows(windows_state)

    def _restore_session(self) -> None:
        """Restore previous session."""
        tabs = self.settings.get_open_tabs(self.window_id)
        active_tab = self.settings.get_active_tab(self.window_id)

        # If no saved tabs, try to load last repository as single tab
        if not tabs:
            last_repo = self.settings.get_last_repository()
            if last_repo and Path(last_repo).exists():
                tabs = [last_repo]

        # Restore tabs
        for repo_path in tabs:
            if Path(repo_path).exists():
                try:
                    self._add_repository_tab(repo_path)
                except Exception:
                    pass

        # Restore active tab
        if 0 <= active_tab < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(active_tab)

        self._update_ui_state()

    def _get_adaptive_window_size(
        self, size_type: Literal["main", "diff", "blame"] = "main"
    ) -> tuple[int, int, int, int]:
        """Calculate adaptive window size based on available screen dimensions.

        Args:
            size_type: Type of window - "main", "diff", or "blame"

        Returns:
            Tuple of (x, y, width, height) for window geometry
        """
        # Get the primary screen
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            screen_x = screen_geometry.x()
            screen_y = screen_geometry.y()
        else:
            # Fallback to default if screen detection fails
            screen_width = _DEFAULT_SCREEN_WIDTH
            screen_height = _DEFAULT_SCREEN_HEIGHT
            screen_x = 0
            screen_y = 0

        # Calculate window dimensions as percentage of screen size
        if size_type == WINDOW_TYPE_MAIN:
            window_handle = self.windowHandle()
            if window_handle:
                margins = window_handle.frameMargins()
                screen_x += margins.left()
                screen_y += margins.top()
                screen_width = max(1, screen_width - margins.left() - margins.right())
                screen_height = max(1, screen_height - margins.top() - margins.bottom())
            return screen_x, screen_y, screen_width, screen_height
        elif size_type == WINDOW_TYPE_DIFF:
            # Diff dialog: adaptive sizing with min/max constraints
            width_pct = 0.75  # 75% of screen width
            height_pct = 0.75  # 75% of screen height
            # Apply percentage, absolute limits, and screen percentage cap in one operation
            width = min(
                max(int(screen_width * width_pct), _MIN_DIFF_WINDOW_WIDTH),
                _MAX_DIFF_WINDOW_WIDTH,
                int(screen_width * _MAX_DIALOG_SCREEN_PCT),
            )
            height = min(
                max(int(screen_height * height_pct), _MIN_DIFF_WINDOW_HEIGHT),
                _MAX_DIFF_WINDOW_HEIGHT,
                int(screen_height * _MAX_DIALOG_SCREEN_PCT),
            )
        else:  # WINDOW_TYPE_BLAME
            # Blame dialog: adaptive sizing with min/max constraints
            width_pct = 0.75  # 75% of screen width
            height_pct = 0.75  # 75% of screen height
            # Apply percentage, absolute limits, and screen percentage cap in one operation
            width = min(
                max(int(screen_width * width_pct), _MIN_BLAME_WINDOW_WIDTH),
                _MAX_BLAME_WINDOW_WIDTH,
                int(screen_width * _MAX_DIALOG_SCREEN_PCT),
            )
            height = min(
                max(int(screen_height * height_pct), _MIN_BLAME_WINDOW_HEIGHT),
                _MAX_BLAME_WINDOW_HEIGHT,
                int(screen_height * _MAX_DIALOG_SCREEN_PCT),
            )

        # Align window to top-left corner of the current screen
        x = screen_x
        y = screen_y

        return x, y, width, height

    def _restore_window_geometry(self) -> None:
        """Restore window geometry from settings."""
        x, y, width, height = self._get_adaptive_window_size(WINDOW_TYPE_MAIN)
        self.setWindowState(self.windowState() & ~Qt.WindowMaximized)
        self.setGeometry(x, y, width, height)
        self.setWindowState(self.windowState() | Qt.WindowMaximized)

    def showEvent(self, event) -> None:
        """Ensure final windowed geometry is correct after native frame creation."""
        super().showEvent(event)
        self._enforce_window_size()

    def _on_tab_file_selected(self, file_name: str) -> None:
        """Handle file selection in current tab."""
        self._update_ui_state()

        current_tab = self._get_current_tab()
        if not current_tab or not current_tab.repo:
            return

        try:
            from clevergit.core.diff import get_working_tree_diff

            diff_result = get_working_tree_diff(current_tab.repo_path, file_path=file_name)

            if not diff_result.diff_text:
                QMessageBox.information(
                    self, "No Changes", f"No changes to display for {file_name}"
                )
                return

            self._create_diff_window(f"Diff Viewer - {file_name}", diff_result)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to show diff for file:\n{e}")

    def _on_tab_commit_selected(self, commit_sha: str) -> None:
        """Handle commit selection in current tab."""
        current_tab = self._get_current_tab()
        if not current_tab or not current_tab.repo:
            return

        try:
            from clevergit.core.diff import get_commit_diff

            diff_result = get_commit_diff(current_tab.repo_path, commit_sha)
            short_sha = commit_sha[:7]
            self._create_diff_window(f"Diff Viewer - Commit {short_sha}", diff_result)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to show commit diff:\n{e}")

    def _restore_repository_branch(self, repo_path: str) -> None:
        """Restore the last active branch for a repository if it was saved.

        Args:
            repo_path: The path to the repository
        """
        saved_branch = self.settings.get_repository_branch(repo_path)
        if not saved_branch or not self.repo:
            return

        try:
            current_branch = self.repo.current_branch()
            # Only switch if we're not already on the saved branch
            if current_branch != saved_branch:
                # Check if the saved branch still exists
                branches = self.repo.list_branches()
                branch_names = [b.name for b in branches]
                if saved_branch in branch_names:
                    self.repo.checkout(saved_branch)
        except Exception:
            # If we can't restore the branch, just continue with current branch
            pass

    def _clone_repository(self) -> None:
        """Show clone repository dialog."""
        dialog = CloneDialog(self)
        if dialog.exec():
            cloned_path = dialog.get_cloned_path()
            if cloned_path:
                try:
                    # Verify it's a valid repo
                    Repo.open(cloned_path)
                    self._add_repository_tab(cloned_path)
                    self.settings.set_last_repository(cloned_path)
                    QMessageBox.information(self, "Success", f"Repository cloned to: {cloned_path}")
                except Exception as e:
                    QMessageBox.warning(
                        self, "Warning", f"Repository cloned successfully, but failed to open:\n{e}"
                    )

    def _open_repository(self) -> None:
        """Open a repository dialog."""
        path = QFileDialog.getExistingDirectory(
            self, "Select Repository Directory", str(Path.home())
        )

        if not path:
            return

        try:
            # Verify it's a valid repo
            Repo.open(path)
            self._add_repository_tab(path)
            self.settings.set_last_repository(path)
            QMessageBox.information(self, "Success", f"Opened repository: {path}")
        except RepoNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Failed to open repository:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

    def _refresh(self) -> None:
        """Refresh current tab."""
        current_tab = self._get_current_tab()
        if not current_tab:
            QMessageBox.warning(self, "Warning", "No repository opened")
            return

        current_tab.refresh()
        self._update_ui_state()

    def _show_commit_dialog(self) -> None:
        """Show commit dialog for current tab."""
        current_tab = self._get_current_tab()
        if not current_tab or not current_tab.repo:
            QMessageBox.warning(self, "Warning", "No repository opened")
            return

        dialog = CommitDialog(self, current_tab.repo)
        if dialog.exec():
            current_tab.refresh()
            QMessageBox.information(self, "Success", "Commit created successfully")

    def _pull(self) -> None:
        """Pull from remote repository in current tab."""
        current_tab = self._get_current_tab()
        if not current_tab or not current_tab.repo:
            QMessageBox.warning(self, "Warning", "No repository opened")
            return

        # Check if repository is clean before pulling
        if not current_tab.repo.is_clean():
            reply = QMessageBox.question(
                self,
                "Uncommitted Changes",
                "You have uncommitted changes. Pull anyway?\n\n" "This may cause conflicts.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        # Show confirmation
        reply = QMessageBox.question(
            self,
            "Pull from Remote",
            "Pull latest changes from remote?\n\n" "This will fetch and merge changes from origin.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                QMessageBox.information(
                    self, "Pulling", "Pulling changes from remote...\n\nPlease wait."
                )
                current_tab.repo.pull()
                current_tab.refresh()
                QMessageBox.information(self, "Success", "Successfully pulled from remote")
            except Exception as e:
                error_msg = str(e)
                QMessageBox.critical(self, "Error", f"Failed to pull:\n{error_msg}")

    def _push(self) -> None:
        """Push to remote repository in current tab."""
        current_tab = self._get_current_tab()
        if not current_tab or not current_tab.repo:
            QMessageBox.warning(self, "Warning", "No repository opened")
            return

        current_branch = current_tab.repo.current_branch()
        if not current_branch:
            QMessageBox.warning(self, "Warning", "No current branch found")
            return

        # Show confirmation
        reply = QMessageBox.question(
            self,
            "Push to Remote",
            f"Push commits from '{current_branch}' to origin?\n\n"
            "This will upload your local commits to the remote repository.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                QMessageBox.information(
                    self, "Pushing", "Pushing changes to remote...\n\nPlease wait."
                )
                current_tab.repo.push()
                current_tab.refresh()
                QMessageBox.information(
                    self, "Success", f"Successfully pushed '{current_branch}' to remote"
                )
            except Exception as e:
                error_msg = str(e)

                # Check if we need to set upstream
                if (
                    "no upstream" in error_msg.lower()
                    or "has no upstream branch" in error_msg.lower()
                ):
                    upstream_reply = QMessageBox.question(
                        self,
                        "Set Upstream Branch",
                        f"Branch '{current_branch}' has no upstream branch.\n\n"
                        "Do you want to push and set the upstream branch?",
                        QMessageBox.Yes | QMessageBox.No,
                    )

                    if upstream_reply == QMessageBox.Yes:
                        try:
                            current_tab.repo.push(set_upstream=True)
                            current_tab.refresh()
                            QMessageBox.information(
                                self,
                                "Success",
                                f"Successfully pushed '{current_branch}' and set upstream",
                            )
                        except Exception as e2:
                            QMessageBox.critical(self, "Error", f"Failed to push:\n{e2}")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to push:\n{error_msg}")

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.information(
            self,
            "About CleverGit",
            "CleverGit v0.1.0\n\n"
            "A powerful Git client with high-level abstractions.\n\n"
            "Made with Python and PySide6",
        )

    def _show_shortcuts_help(self) -> None:
        """Show keyboard shortcuts help dialog."""
        dialog = ShortcutHelpDialog(self.shortcut_manager, self)
        dialog.exec()

    def _show_command_palette(self) -> None:
        """Show command palette dialog."""
        current_tab = self._get_current_tab()
        repo = current_tab.repo if current_tab else None

        palette = CommandPalette(self, repo)

        # Connect signals to handle different selection types
        palette.file_selected.connect(self._on_palette_file_selected)
        palette.commit_selected.connect(self._on_palette_commit_selected)
        palette.branch_selected.connect(self._on_palette_branch_selected)
        palette.command_executed.connect(self._on_palette_command_executed)

        palette.exec()

    def _on_palette_file_selected(self, file_path: str) -> None:
        """Handle file selection from command palette."""
        current_tab = self._get_current_tab()
        if current_tab:
            # TODO: Navigate to/highlight the file in the status view
            QMessageBox.information(self, "File Selected", f"Selected: {file_path}")

    def _on_palette_commit_selected(self, commit_sha: str) -> None:
        """Handle commit selection from command palette."""
        current_tab = self._get_current_tab()
        if current_tab:
            # TODO: Navigate to the commit in the log view
            QMessageBox.information(self, "Commit Selected", f"Selected commit: {commit_sha[:7]}")

    def _on_palette_branch_selected(self, branch_name: str) -> None:
        """Handle branch selection from command palette."""
        current_tab = self._get_current_tab()
        if current_tab and current_tab.repo:
            reply = QMessageBox.question(
                self,
                "Checkout Branch",
                f"Checkout branch '{branch_name}'?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                try:
                    current_tab.repo.checkout(branch_name)
                    current_tab.refresh()
                    self._update_ui_state()
                    QMessageBox.information(self, "Success", f"Checked out branch: {branch_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to checkout branch:\n{e}")

    def _on_palette_command_executed(self, command: str) -> None:
        """Handle command execution from command palette."""
        # Map command names to methods
        command_map = {
            "refresh": self._refresh,
            "commit": self._show_commit_dialog,
            "pull": self._pull,
            "push": self._push,
            "diff": self._show_diff_viewer,
            "blame": self._show_blame_for_file,
            "stash": self._toggle_stash_view,
            "tag": self._toggle_tag_view,
        }

        if command in command_map:
            command_map[command]()
        else:
            QMessageBox.warning(self, "Unknown Command", f"Command not implemented: {command}")

    def _toggle_stash_view(self) -> None:
        """Toggle the stash view visibility in current tab."""
        current_tab = self._get_current_tab()
        if current_tab:
            current_tab.toggle_stash_view()
            self._update_ui_state()

    def _toggle_tag_view(self) -> None:
        """Toggle the tag view visibility in current tab."""
        current_tab = self._get_current_tab()
        if current_tab:
            current_tab.toggle_tag_view()
            self._update_ui_state()

    def _update_recent_menu(self) -> None:
        """Update the recent repositories menu."""
        self.recent_menu.clear()

        recent_repos = self.settings.get_recent_repositories()

        if not recent_repos:
            no_recent = self.recent_menu.addAction("No recent repositories")
            no_recent.setEnabled(False)
            return

        for repo_path in recent_repos:
            path_obj = Path(repo_path)
            display_name = path_obj.name if path_obj.name else path_obj.as_posix()

            # Create a submenu for each repository
            repo_submenu = self.recent_menu.addMenu(display_name)
            repo_submenu.setToolTip(repo_path)

            # Add "Open" action
            open_action = repo_submenu.addAction("Open")
            open_action.triggered.connect(
                lambda checked=False, p=repo_path: self._open_recent_repository(p)
            )

            # Add "Remove from List" action
            remove_action = repo_submenu.addAction("Remove from List")
            remove_action.triggered.connect(
                lambda checked=False, p=repo_path: self._remove_recent_repository(p)
            )

    def _remove_recent_repository(self, path: str) -> None:
        """Remove a repository from the recent list."""
        self.settings.remove_recent_repository(path)
        self._update_recent_menu()

    def _open_recent_repository(self, path: str) -> None:
        """Open a repository from the recent list."""
        repo_path = Path(path)

        if not repo_path.exists():
            QMessageBox.warning(self, "Warning", f"Repository path no longer exists:\n{path}")
            return

        try:
            Repo.open(path)
            self._add_repository_tab(path)
        except RepoNotFoundError as e:
            QMessageBox.critical(self, "Error", f"Failed to open repository:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

    def _create_diff_window(self, title: str, diff_result) -> None:
        """Create and show a diff viewer window.

        Args:
            title: Window title
            diff_result: DiffResult object containing diff data
        """
        # Create diff viewer dialog
        diff_dialog = QWidget()
        diff_dialog.setWindowTitle(title)
        x, y, width, height = self._get_adaptive_window_size(WINDOW_TYPE_DIFF)
        diff_dialog.setGeometry(x, y, width, height)

        layout = QVBoxLayout()
        viewer = DiffViewer()
        viewer.set_diff(
            diff_result.diff_text,
            stats={
                "files_changed": diff_result.stats.files_changed,
                "insertions": diff_result.stats.insertions,
                "deletions": diff_result.stats.deletions,
            },
        )
        layout.addWidget(viewer)
        diff_dialog.setLayout(layout)

        # Keep reference to prevent garbage collection
        self._diff_dialogs.append(diff_dialog)
        diff_dialog.show()

    def _create_blame_window(
        self, title: str, blame_list: List, file_path: str, repo_path: Path
    ) -> None:
        """Create and show a blame viewer window.

        Args:
            title: Window title
            blame_list: List of BlameInfo objects
            file_path: Path to the file being blamed
            repo_path: Path to the repository
        """
        blame_dialog = QWidget()
        blame_dialog.setWindowTitle(title)
        x, y, width, height = self._get_adaptive_window_size(WINDOW_TYPE_BLAME)
        blame_dialog.setGeometry(x, y, width, height)

        layout = QVBoxLayout()
        blame_view = BlameView()

        # Connect commit click signal to show commit details
        blame_view.commit_clicked.connect(lambda sha: self._show_commit_details(sha, repo_path))

        # Connect refresh signal to re-fetch blame data
        blame_view.refresh_requested.connect(
            lambda fp: self._refresh_blame_window(blame_view, fp, repo_path)
        )

        blame_view.update_blame(blame_list, file_path)
        layout.addWidget(blame_view)
        blame_dialog.setLayout(layout)

        # Keep reference to prevent garbage collection
        self._blame_windows.append(blame_dialog)
        blame_dialog.show()

    def _show_blame_for_file(self) -> None:
        """Show blame information for the selected file in current tab."""
        current_tab = self._get_current_tab()
        if not current_tab or not current_tab.repo:
            QMessageBox.warning(self, "Warning", "No repository opened")
            return

        selected_file = current_tab.get_selected_file()
        if not selected_file:
            QMessageBox.warning(self, "Warning", "No file selected. Please select a file first.")
            return

        try:
            from clevergit.core.blame import get_blame

            blame_list = get_blame(current_tab.repo_path, selected_file)

            if not blame_list:
                QMessageBox.information(
                    self, "No Blame Data", f"No blame data available for {selected_file}"
                )
                return

            self._create_blame_window(
                f"Blame - {selected_file}", blame_list, selected_file, current_tab.repo_path
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show blame:\n{e}")

    def _show_commit_details(self, commit_sha: str, repo_path: Path) -> None:
        """Show details for a specific commit.

        Args:
            commit_sha: The commit SHA to show details for
            repo_path: The path to the repository
        """
        try:
            from clevergit.core.diff import get_commit_diff

            diff_result = get_commit_diff(repo_path, commit_sha)
            self._create_diff_window(f"Commit Details - {commit_sha[:7]}", diff_result)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to show commit details:\n{e}")

    def _refresh_blame_window(self, blame_view: BlameView, file_path: str, repo_path: Path) -> None:
        """Refresh blame information for a blame window.

        Args:
            blame_view: The BlameView widget to refresh
            file_path: Path to the file being blamed
            repo_path: The path to the repository
        """
        try:
            from clevergit.core.blame import get_blame

            blame_list = get_blame(repo_path, file_path)

            if not blame_list:
                QMessageBox.information(
                    self, "No Blame Data", f"No blame data available for {file_path}"
                )
                return

            blame_view.update_blame(blame_list, file_path)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh blame:\n{e}")

    def _show_diff_viewer(self) -> None:
        """Show the diff viewer window with working tree changes for current tab."""
        current_tab = self._get_current_tab()
        if not current_tab or not current_tab.repo:
            QMessageBox.warning(self, "Warning", "No repository opened")
            return

        try:
            from clevergit.core.diff import get_working_tree_diff

            diff_result = get_working_tree_diff(current_tab.repo_path)
            self._create_diff_window("Diff Viewer - Working Tree Changes", diff_result)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show diff:\n{e}")

    def _set_theme(self, theme_name: str) -> None:
        """Set application theme.

        Args:
            theme_name: Name of the theme to apply
        """
        from clevergit.ui.themes import get_theme_manager

        theme_manager = get_theme_manager()
        if theme_manager.set_theme(theme_name):
            # Save the theme preference
            self.settings.set_theme(theme_name)
            QMessageBox.information(
                self,
                "Theme Changed",
                f"Theme changed to {theme_name}. Some changes may require restart.",
            )

    def _use_system_theme(self) -> None:
        """Enable system theme following."""
        from clevergit.ui.themes import get_theme_manager

        theme_manager = get_theme_manager()
        theme_manager.apply_system_theme()

        # Save preference
        current_theme = theme_manager.get_current_theme()
        if current_theme:
            self.settings.set_theme(current_theme.name)

        QMessageBox.information(self, "System Theme", "Following system theme preference.")

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        # Don't save window geometry - always use adaptive screen size on startup

        # Save session
        self._save_session()

        # Remove from windows list
        if self in _windows:
            _windows.remove(self)

        # Accept the close event
        event.accept()
