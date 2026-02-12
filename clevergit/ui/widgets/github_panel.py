"""
GitHub integration panel widget.

Provides UI for viewing and interacting with GitHub features.
"""

from typing import Optional, List, Dict, Any, TYPE_CHECKING
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QTextEdit,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QColor

from clevergit.integrations.github import GitHubClient, GitHubAPIError, parse_github_url

if TYPE_CHECKING:
    from clevergit.core.repo import Repo


class GitHubWorker(QThread):
    """Worker thread for GitHub API calls."""
    
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Execute the function in a separate thread."""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class CreatePRDialog(QDialog):
    """Dialog for creating a pull request."""
    
    def __init__(self, repo: "Repo", github_client: GitHubClient, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.github_client = github_client
        self.setWindowTitle("Create Pull Request")
        self.setMinimumWidth(500)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Title:")
        self.title_edit = QLineEdit()
        layout.addWidget(title_label)
        layout.addWidget(self.title_edit)
        
        # Base branch
        base_label = QLabel("Base branch:")
        self.base_combo = QComboBox()
        layout.addWidget(base_label)
        layout.addWidget(self.base_combo)
        
        # Head branch (current branch)
        head_label = QLabel("Head branch:")
        self.head_combo = QComboBox()
        layout.addWidget(head_label)
        layout.addWidget(self.head_combo)
        
        # Body
        body_label = QLabel("Description:")
        self.body_edit = QTextEdit()
        self.body_edit.setMinimumHeight(200)
        layout.addWidget(body_label)
        layout.addWidget(self.body_edit)
        
        # Draft checkbox
        self.draft_check = QPushButton("Create as draft")
        self.draft_check.setCheckable(True)
        layout.addWidget(self.draft_check)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Load branches
        self._load_branches()
    
    def _load_branches(self):
        """Load branches from repository."""
        try:
            branches = self.repo.list_branches()
            branch_names = [b.name for b in branches if not b.is_remote]
            
            current_branch = self.repo.current_branch()
            
            self.base_combo.addItems(branch_names)
            self.head_combo.addItems(branch_names)
            
            # Set default to main/master for base
            if "main" in branch_names:
                self.base_combo.setCurrentText("main")
            elif "master" in branch_names:
                self.base_combo.setCurrentText("master")
            
            # Set current branch as head
            if current_branch:
                self.head_combo.setCurrentText(current_branch)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load branches: {e}")
    
    def get_pr_data(self) -> Dict[str, Any]:
        """Get the PR data from the form."""
        return {
            "title": self.title_edit.text(),
            "base": self.base_combo.currentText(),
            "head": self.head_combo.currentText(),
            "body": self.body_edit.toPlainText(),
            "draft": self.draft_check.isChecked()
        }


class GitHubPanel(QWidget):
    """Main GitHub integration panel."""
    
    def __init__(self, repo: Optional["Repo"] = None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.github_client: Optional[GitHubClient] = None
        self.owner: Optional[str] = None
        self.repo_name: Optional[str] = None
        
        self._setup_ui()
        
        if repo:
            self.set_repository(repo)
    
    def _setup_ui(self):
        """Setup the panel UI."""
        layout = QVBoxLayout()
        
        # Authentication section
        auth_group = QGroupBox("Authentication")
        auth_layout = QHBoxLayout()
        
        self.token_label = QLabel("Not authenticated")
        auth_layout.addWidget(self.token_label)
        
        self.auth_button = QPushButton("Authenticate")
        self.auth_button.clicked.connect(self._authenticate)
        auth_layout.addWidget(self.auth_button)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        # Repository info section
        repo_group = QGroupBox("Repository")
        repo_layout = QVBoxLayout()
        
        self.repo_info_label = QLabel("No repository loaded")
        repo_layout.addWidget(self.repo_info_label)
        
        button_row = QHBoxLayout()
        self.fork_button = QPushButton("🍴 Fork")
        self.fork_button.clicked.connect(self._fork_repository)
        self.fork_button.setEnabled(False)
        button_row.addWidget(self.fork_button)
        
        self.star_button = QPushButton("⭐ Star")
        self.star_button.clicked.connect(self._toggle_star)
        self.star_button.setEnabled(False)
        button_row.addWidget(self.star_button)
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self._refresh_data)
        self.refresh_button.setEnabled(False)
        button_row.addWidget(self.refresh_button)
        
        repo_layout.addLayout(button_row)
        repo_group.setLayout(repo_layout)
        layout.addWidget(repo_group)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # Pull Requests tab
        self.pr_widget = self._create_pr_tab()
        self.tabs.addTab(self.pr_widget, "Pull Requests")
        
        # Issues tab
        self.issues_widget = self._create_issues_tab()
        self.tabs.addTab(self.issues_widget, "Issues")
        
        # Actions tab
        self.actions_widget = self._create_actions_tab()
        self.tabs.addTab(self.actions_widget, "Actions")
        
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
    
    def _create_pr_tab(self) -> QWidget:
        """Create the pull requests tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.pr_state_combo = QComboBox()
        self.pr_state_combo.addItems(["open", "closed", "all"])
        self.pr_state_combo.currentTextChanged.connect(self._refresh_pull_requests)
        controls_layout.addWidget(QLabel("State:"))
        controls_layout.addWidget(self.pr_state_combo)
        
        self.create_pr_button = QPushButton("➕ Create PR")
        self.create_pr_button.clicked.connect(self._create_pull_request)
        self.create_pr_button.setEnabled(False)
        controls_layout.addWidget(self.create_pr_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # PR list
        self.pr_table = QTableWidget()
        self.pr_table.setColumnCount(5)
        self.pr_table.setHorizontalHeaderLabels(["#", "Title", "Author", "State", "Updated"])
        self.pr_table.horizontalHeader().setStretchLastSection(True)
        self.pr_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pr_table.itemDoubleClicked.connect(self._on_pr_double_clicked)
        layout.addWidget(self.pr_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_issues_tab(self) -> QWidget:
        """Create the issues tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.issue_state_combo = QComboBox()
        self.issue_state_combo.addItems(["open", "closed", "all"])
        self.issue_state_combo.currentTextChanged.connect(self._refresh_issues)
        controls_layout.addWidget(QLabel("State:"))
        controls_layout.addWidget(self.issue_state_combo)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Issue list
        self.issue_table = QTableWidget()
        self.issue_table.setColumnCount(5)
        self.issue_table.setHorizontalHeaderLabels(["#", "Title", "Author", "State", "Updated"])
        self.issue_table.horizontalHeader().setStretchLastSection(True)
        self.issue_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.issue_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_actions_tab(self) -> QWidget:
        """Create the GitHub Actions tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Workflow runs list
        self.actions_table = QTableWidget()
        self.actions_table.setColumnCount(5)
        self.actions_table.setHorizontalHeaderLabels(["Workflow", "Status", "Branch", "Commit", "Updated"])
        self.actions_table.horizontalHeader().setStretchLastSection(True)
        self.actions_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.actions_table)
        
        widget.setLayout(layout)
        return widget
    
    def set_repository(self, repo: "Repo"):
        """Set the current repository."""
        self.repo = repo
        
        # Try to parse repository URL
        try:
            remotes = repo.list_remotes()
            if remotes:
                # Try to get origin remote
                origin_url = None
                for remote in remotes:
                    if remote["name"] == "origin":
                        origin_url = remote["url"]
                        break
                
                if not origin_url and remotes:
                    origin_url = remotes[0]["url"]
                
                if origin_url:
                    parsed = parse_github_url(origin_url)
                    if parsed:
                        self.owner, self.repo_name = parsed
                        self.repo_info_label.setText(f"{self.owner}/{self.repo_name}")
                        self._enable_github_features()
                        return
        except Exception as e:
            pass
        
        self.repo_info_label.setText("Not a GitHub repository")
        self.owner = None
        self.repo_name = None
    
    def _enable_github_features(self):
        """Enable GitHub features if authenticated."""
        if self.github_client and self.owner and self.repo_name:
            self.fork_button.setEnabled(True)
            self.star_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
            self.create_pr_button.setEnabled(True)
            self._update_star_button()
            self._refresh_data()
    
    def _authenticate(self):
        """Authenticate with GitHub."""
        from PySide6.QtWidgets import QInputDialog
        
        token, ok = QInputDialog.getText(
            self,
            "GitHub Authentication",
            "Enter your GitHub personal access token:",
            QLineEdit.Password
        )
        
        if ok and token:
            try:
                self.github_client = GitHubClient(token)
                user = self.github_client.get_authenticated_user()
                self.token_label.setText(f"Authenticated as {user['login']}")
                self.auth_button.setText("Change Token")
                self._enable_github_features()
            except Exception as e:
                QMessageBox.critical(self, "Authentication Failed", str(e))
    
    def _fork_repository(self):
        """Fork the current repository."""
        if not self.github_client or not self.owner or not self.repo_name:
            return
        
        reply = QMessageBox.question(
            self,
            "Fork Repository",
            f"Fork {self.owner}/{self.repo_name} to your account?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            worker = GitHubWorker(
                self.github_client.fork_repository,
                self.owner,
                self.repo_name
            )
            worker.finished.connect(lambda result: QMessageBox.information(
                self,
                "Success",
                "Repository forked successfully!"
            ))
            worker.error.connect(lambda error: QMessageBox.critical(
                self,
                "Error",
                f"Failed to fork repository: {error}"
            ))
            worker.start()
    
    def _toggle_star(self):
        """Toggle star status of the repository."""
        if not self.github_client or not self.owner or not self.repo_name:
            return
        
        try:
            is_starred = self.github_client.is_repository_starred(self.owner, self.repo_name)
            
            if is_starred:
                self.github_client.unstar_repository(self.owner, self.repo_name)
                QMessageBox.information(self, "Success", "Repository unstarred!")
            else:
                self.github_client.star_repository(self.owner, self.repo_name)
                QMessageBox.information(self, "Success", "Repository starred!")
            
            self._update_star_button()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _update_star_button(self):
        """Update the star button text based on star status."""
        if not self.github_client or not self.owner or not self.repo_name:
            return
        
        try:
            is_starred = self.github_client.is_repository_starred(self.owner, self.repo_name)
            self.star_button.setText("⭐ Unstar" if is_starred else "⭐ Star")
        except Exception:
            pass
    
    def _refresh_data(self):
        """Refresh all GitHub data."""
        self._refresh_pull_requests()
        self._refresh_issues()
        self._refresh_actions()
    
    def _refresh_pull_requests(self):
        """Refresh pull requests list."""
        if not self.github_client or not self.owner or not self.repo_name:
            return
        
        state = self.pr_state_combo.currentText()
        
        worker = GitHubWorker(
            self.github_client.list_pull_requests,
            self.owner,
            self.repo_name,
            state
        )
        worker.finished.connect(self._display_pull_requests)
        worker.error.connect(lambda error: QMessageBox.warning(
            self,
            "Error",
            f"Failed to fetch pull requests: {error}"
        ))
        worker.start()
    
    def _display_pull_requests(self, prs: List[Dict[str, Any]]):
        """Display pull requests in the table."""
        self.pr_table.setRowCount(len(prs))
        
        for i, pr in enumerate(prs):
            self.pr_table.setItem(i, 0, QTableWidgetItem(str(pr["number"])))
            self.pr_table.setItem(i, 1, QTableWidgetItem(pr["title"]))
            self.pr_table.setItem(i, 2, QTableWidgetItem(pr["user"]["login"]))
            self.pr_table.setItem(i, 3, QTableWidgetItem(pr["state"]))
            self.pr_table.setItem(i, 4, QTableWidgetItem(pr["updated_at"]))
    
    def _refresh_issues(self):
        """Refresh issues list."""
        if not self.github_client or not self.owner or not self.repo_name:
            return
        
        state = self.issue_state_combo.currentText()
        
        worker = GitHubWorker(
            self.github_client.list_issues,
            self.owner,
            self.repo_name,
            state
        )
        worker.finished.connect(self._display_issues)
        worker.error.connect(lambda error: QMessageBox.warning(
            self,
            "Error",
            f"Failed to fetch issues: {error}"
        ))
        worker.start()
    
    def _display_issues(self, issues: List[Dict[str, Any]]):
        """Display issues in the table."""
        # Filter out pull requests (GitHub API returns PRs as issues)
        issues = [issue for issue in issues if "pull_request" not in issue]
        
        self.issue_table.setRowCount(len(issues))
        
        for i, issue in enumerate(issues):
            self.issue_table.setItem(i, 0, QTableWidgetItem(str(issue["number"])))
            self.issue_table.setItem(i, 1, QTableWidgetItem(issue["title"]))
            self.issue_table.setItem(i, 2, QTableWidgetItem(issue["user"]["login"]))
            self.issue_table.setItem(i, 3, QTableWidgetItem(issue["state"]))
            self.issue_table.setItem(i, 4, QTableWidgetItem(issue["updated_at"]))
    
    def _refresh_actions(self):
        """Refresh GitHub Actions status."""
        if not self.github_client or not self.owner or not self.repo_name:
            return
        
        worker = GitHubWorker(
            self.github_client.list_workflow_runs,
            self.owner,
            self.repo_name
        )
        worker.finished.connect(self._display_actions)
        worker.error.connect(lambda error: None)  # Silently ignore if Actions not available
        worker.start()
    
    def _display_actions(self, runs: List[Dict[str, Any]]):
        """Display workflow runs in the table."""
        self.actions_table.setRowCount(len(runs))
        
        for i, run in enumerate(runs):
            self.actions_table.setItem(i, 0, QTableWidgetItem(run["name"]))
            
            # Color code status
            status_item = QTableWidgetItem(run["status"])
            conclusion = run.get("conclusion")
            if conclusion == "success":
                status_item.setForeground(QColor("green"))
            elif conclusion == "failure":
                status_item.setForeground(QColor("red"))
            self.actions_table.setItem(i, 1, status_item)
            
            self.actions_table.setItem(i, 2, QTableWidgetItem(run["head_branch"]))
            self.actions_table.setItem(i, 3, QTableWidgetItem(run["head_sha"][:7]))
            self.actions_table.setItem(i, 4, QTableWidgetItem(run["updated_at"]))
    
    def _create_pull_request(self):
        """Show dialog to create a pull request."""
        if not self.github_client or not self.owner or not self.repo_name or not self.repo:
            return
        
        dialog = CreatePRDialog(self.repo, self.github_client, self)
        if dialog.exec() == QDialog.Accepted:
            pr_data = dialog.get_pr_data()
            
            worker = GitHubWorker(
                self.github_client.create_pull_request,
                self.owner,
                self.repo_name,
                pr_data["title"],
                pr_data["head"],
                pr_data["base"],
                pr_data.get("body"),
                pr_data.get("draft", False)
            )
            worker.finished.connect(lambda result: self._on_pr_created(result))
            worker.error.connect(lambda error: QMessageBox.critical(
                self,
                "Error",
                f"Failed to create pull request: {error}"
            ))
            worker.start()
    
    def _on_pr_created(self, pr: Dict[str, Any]):
        """Handle successful PR creation."""
        QMessageBox.information(
            self,
            "Success",
            f"Pull request #{pr['number']} created successfully!"
        )
        self._refresh_pull_requests()
    
    def _on_pr_double_clicked(self, item):
        """Handle double-click on PR."""
        row = item.row()
        pr_number = self.pr_table.item(row, 0).text()
        
        if self.github_client and self.owner and self.repo_name:
            # Open PR in browser
            import webbrowser
            url = f"https://github.com/{self.owner}/{self.repo_name}/pull/{pr_number}"
            webbrowser.open(url)
