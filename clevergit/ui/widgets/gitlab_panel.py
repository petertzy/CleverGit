"""
GitLab integration panel widget.

Provides UI for viewing and interacting with GitLab features.
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

from clevergit.integrations.gitlab import GitLabClient, GitLabAPIError, parse_gitlab_url

if TYPE_CHECKING:
    from clevergit.core.repo import Repo


class GitLabWorker(QThread):
    """Worker thread for GitLab API calls."""
    
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


class CreateMRDialog(QDialog):
    """Dialog for creating a merge request."""
    
    def __init__(self, repo: "Repo", gitlab_client: GitLabClient, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.gitlab_client = gitlab_client
        self.setWindowTitle("Create Merge Request")
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
        
        # Target branch
        target_label = QLabel("Target branch:")
        self.target_combo = QComboBox()
        layout.addWidget(target_label)
        layout.addWidget(self.target_combo)
        
        # Source branch (current branch)
        source_label = QLabel("Source branch:")
        self.source_combo = QComboBox()
        layout.addWidget(source_label)
        layout.addWidget(self.source_combo)
        
        # Description
        description_label = QLabel("Description:")
        self.description_edit = QTextEdit()
        self.description_edit.setMinimumHeight(200)
        layout.addWidget(description_label)
        layout.addWidget(self.description_edit)
        
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
            
            self.target_combo.addItems(branch_names)
            self.source_combo.addItems(branch_names)
            
            # Set default to main/master for target
            if "main" in branch_names:
                self.target_combo.setCurrentText("main")
            elif "master" in branch_names:
                self.target_combo.setCurrentText("master")
            
            # Set current branch as source
            if current_branch:
                self.source_combo.setCurrentText(current_branch)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load branches: {e}")
    
    def get_mr_data(self) -> Dict[str, Any]:
        """Get the MR data from the form."""
        return {
            "title": self.title_edit.text(),
            "target_branch": self.target_combo.currentText(),
            "source_branch": self.source_combo.currentText(),
            "description": self.description_edit.toPlainText(),
            "draft": self.draft_check.isChecked()
        }


class GitLabPanel(QWidget):
    """Main GitLab integration panel."""
    
    def __init__(self, repo: Optional["Repo"] = None, parent=None):
        super().__init__(parent)
        self.repo = repo
        self.gitlab_client: Optional[GitLabClient] = None
        self.project_path: Optional[str] = None
        
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
        
        # Project info section
        project_group = QGroupBox("Project")
        project_layout = QVBoxLayout()
        
        self.project_info_label = QLabel("No project loaded")
        project_layout.addWidget(self.project_info_label)
        
        button_row = QHBoxLayout()
        self.fork_button = QPushButton("🍴 Fork")
        self.fork_button.clicked.connect(self._fork_project)
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
        
        project_layout.addLayout(button_row)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # Tabs for different views
        self.tabs = QTabWidget()
        
        # Merge Requests tab
        self.mr_widget = self._create_mr_tab()
        self.tabs.addTab(self.mr_widget, "Merge Requests")
        
        # Issues tab
        self.issues_widget = self._create_issues_tab()
        self.tabs.addTab(self.issues_widget, "Issues")
        
        # Pipelines tab
        self.pipelines_widget = self._create_pipelines_tab()
        self.tabs.addTab(self.pipelines_widget, "CI/CD")
        
        layout.addWidget(self.tabs)
        
        self.setLayout(layout)
    
    def _create_mr_tab(self) -> QWidget:
        """Create the merge requests tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.mr_state_combo = QComboBox()
        self.mr_state_combo.addItems(["opened", "closed", "merged", "all"])
        self.mr_state_combo.currentTextChanged.connect(self._refresh_merge_requests)
        controls_layout.addWidget(QLabel("State:"))
        controls_layout.addWidget(self.mr_state_combo)
        
        self.create_mr_button = QPushButton("➕ Create MR")
        self.create_mr_button.clicked.connect(self._create_merge_request)
        self.create_mr_button.setEnabled(False)
        controls_layout.addWidget(self.create_mr_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # MR list
        self.mr_table = QTableWidget()
        self.mr_table.setColumnCount(5)
        self.mr_table.setHorizontalHeaderLabels(["!IID", "Title", "Author", "State", "Updated"])
        self.mr_table.horizontalHeader().setStretchLastSection(True)
        self.mr_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.mr_table.itemDoubleClicked.connect(self._on_mr_double_clicked)
        layout.addWidget(self.mr_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_issues_tab(self) -> QWidget:
        """Create the issues tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.issue_state_combo = QComboBox()
        self.issue_state_combo.addItems(["opened", "closed", "all"])
        self.issue_state_combo.currentTextChanged.connect(self._refresh_issues)
        controls_layout.addWidget(QLabel("State:"))
        controls_layout.addWidget(self.issue_state_combo)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Issue list
        self.issue_table = QTableWidget()
        self.issue_table.setColumnCount(5)
        self.issue_table.setHorizontalHeaderLabels(["#IID", "Title", "Author", "State", "Updated"])
        self.issue_table.horizontalHeader().setStretchLastSection(True)
        self.issue_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.issue_table)
        
        widget.setLayout(layout)
        return widget
    
    def _create_pipelines_tab(self) -> QWidget:
        """Create the CI/CD pipelines tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Pipeline runs list
        self.pipelines_table = QTableWidget()
        self.pipelines_table.setColumnCount(5)
        self.pipelines_table.setHorizontalHeaderLabels(["ID", "Status", "Ref", "Commit", "Updated"])
        self.pipelines_table.horizontalHeader().setStretchLastSection(True)
        self.pipelines_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.pipelines_table)
        
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
                    parsed = parse_gitlab_url(origin_url)
                    if parsed and ("gitlab" in origin_url.lower()):
                        self.project_path = parsed
                        self.project_info_label.setText(self.project_path)
                        self._enable_gitlab_features()
                        return
        except Exception as e:
            pass
        
        self.project_info_label.setText("Not a GitLab project")
        self.project_path = None
    
    def _enable_gitlab_features(self):
        """Enable GitLab features if authenticated."""
        if self.gitlab_client and self.project_path:
            self.fork_button.setEnabled(True)
            self.star_button.setEnabled(True)
            self.refresh_button.setEnabled(True)
            self.create_mr_button.setEnabled(True)
            self._update_star_button()
            self._refresh_data()
    
    def _authenticate(self):
        """Authenticate with GitLab."""
        from PySide6.QtWidgets import QInputDialog
        
        token, ok = QInputDialog.getText(
            self,
            "GitLab Authentication",
            "Enter your GitLab personal access token:",
            QLineEdit.Password
        )
        
        if ok and token:
            try:
                self.gitlab_client = GitLabClient(token)
                user = self.gitlab_client.get_authenticated_user()
                self.token_label.setText(f"Authenticated as {user['username']}")
                self.auth_button.setText("Change Token")
                self._enable_gitlab_features()
            except Exception as e:
                QMessageBox.critical(self, "Authentication Failed", str(e))
    
    def _fork_project(self):
        """Fork the current project."""
        if not self.gitlab_client or not self.project_path:
            return
        
        reply = QMessageBox.question(
            self,
            "Fork Project",
            f"Fork {self.project_path} to your namespace?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            worker = GitLabWorker(
                self.gitlab_client.fork_project,
                self.project_path
            )
            worker.finished.connect(lambda result: QMessageBox.information(
                self,
                "Success",
                "Project forked successfully!"
            ))
            worker.error.connect(lambda error: QMessageBox.critical(
                self,
                "Error",
                f"Failed to fork project: {error}"
            ))
            worker.start()
    
    def _toggle_star(self):
        """Toggle star status of the project."""
        if not self.gitlab_client or not self.project_path:
            return
        
        try:
            is_starred = self.gitlab_client.is_project_starred(self.project_path)
            
            if is_starred:
                self.gitlab_client.unstar_project(self.project_path)
                QMessageBox.information(self, "Success", "Project unstarred!")
            else:
                self.gitlab_client.star_project(self.project_path)
                QMessageBox.information(self, "Success", "Project starred!")
            
            self._update_star_button()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _update_star_button(self):
        """Update the star button text based on star status."""
        if not self.gitlab_client or not self.project_path:
            return
        
        try:
            is_starred = self.gitlab_client.is_project_starred(self.project_path)
            self.star_button.setText("⭐ Unstar" if is_starred else "⭐ Star")
        except Exception:
            pass
    
    def _refresh_data(self):
        """Refresh all GitLab data."""
        self._refresh_merge_requests()
        self._refresh_issues()
        self._refresh_pipelines()
    
    def _refresh_merge_requests(self):
        """Refresh merge requests list."""
        if not self.gitlab_client or not self.project_path:
            return
        
        state = self.mr_state_combo.currentText()
        
        worker = GitLabWorker(
            self.gitlab_client.list_merge_requests,
            self.project_path,
            state
        )
        worker.finished.connect(self._display_merge_requests)
        worker.error.connect(lambda error: QMessageBox.warning(
            self,
            "Error",
            f"Failed to fetch merge requests: {error}"
        ))
        worker.start()
    
    def _display_merge_requests(self, mrs: List[Dict[str, Any]]):
        """Display merge requests in the table."""
        self.mr_table.setRowCount(len(mrs))
        
        for i, mr in enumerate(mrs):
            self.mr_table.setItem(i, 0, QTableWidgetItem(str(mr["iid"])))
            self.mr_table.setItem(i, 1, QTableWidgetItem(mr["title"]))
            self.mr_table.setItem(i, 2, QTableWidgetItem(mr["author"]["username"]))
            self.mr_table.setItem(i, 3, QTableWidgetItem(mr["state"]))
            self.mr_table.setItem(i, 4, QTableWidgetItem(mr["updated_at"]))
    
    def _refresh_issues(self):
        """Refresh issues list."""
        if not self.gitlab_client or not self.project_path:
            return
        
        state = self.issue_state_combo.currentText()
        
        worker = GitLabWorker(
            self.gitlab_client.list_issues,
            self.project_path,
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
        self.issue_table.setRowCount(len(issues))
        
        for i, issue in enumerate(issues):
            self.issue_table.setItem(i, 0, QTableWidgetItem(str(issue["iid"])))
            self.issue_table.setItem(i, 1, QTableWidgetItem(issue["title"]))
            self.issue_table.setItem(i, 2, QTableWidgetItem(issue["author"]["username"]))
            self.issue_table.setItem(i, 3, QTableWidgetItem(issue["state"]))
            self.issue_table.setItem(i, 4, QTableWidgetItem(issue["updated_at"]))
    
    def _refresh_pipelines(self):
        """Refresh CI/CD pipelines status."""
        if not self.gitlab_client or not self.project_path:
            return
        
        worker = GitLabWorker(
            self.gitlab_client.list_pipelines,
            self.project_path
        )
        worker.finished.connect(self._display_pipelines)
        worker.error.connect(lambda error: self._handle_pipeline_error(error))
        worker.start()
    
    def _handle_pipeline_error(self, error: str):
        """Handle pipeline fetch errors gracefully."""
        # Log error but don't show message box as pipelines may not be enabled
        # Only clear the table to indicate no pipelines available
        self.pipelines_table.setRowCount(0)
    
    def _display_pipelines(self, pipelines: List[Dict[str, Any]]):
        """Display pipelines in the table."""
        self.pipelines_table.setRowCount(len(pipelines))
        
        for i, pipeline in enumerate(pipelines):
            self.pipelines_table.setItem(i, 0, QTableWidgetItem(str(pipeline["id"])))
            
            # Color code status
            status_item = QTableWidgetItem(pipeline["status"])
            status = pipeline.get("status")
            if status == "success":
                status_item.setForeground(QColor("green"))
            elif status == "failed":
                status_item.setForeground(QColor("red"))
            elif status == "running":
                status_item.setForeground(QColor("blue"))
            self.pipelines_table.setItem(i, 1, status_item)
            
            self.pipelines_table.setItem(i, 2, QTableWidgetItem(pipeline.get("ref", "")))
            self.pipelines_table.setItem(i, 3, QTableWidgetItem(pipeline.get("sha", "")[:7]))
            self.pipelines_table.setItem(i, 4, QTableWidgetItem(pipeline.get("updated_at", "")))
    
    def _create_merge_request(self):
        """Show dialog to create a merge request."""
        if not self.gitlab_client or not self.project_path or not self.repo:
            return
        
        dialog = CreateMRDialog(self.repo, self.gitlab_client, self)
        if dialog.exec() == QDialog.Accepted:
            mr_data = dialog.get_mr_data()
            
            worker = GitLabWorker(
                self.gitlab_client.create_merge_request,
                self.project_path,
                mr_data["title"],
                mr_data["source_branch"],
                mr_data["target_branch"],
                mr_data.get("description"),
                mr_data.get("draft", False)
            )
            worker.finished.connect(lambda result: self._on_mr_created(result))
            worker.error.connect(lambda error: QMessageBox.critical(
                self,
                "Error",
                f"Failed to create merge request: {error}"
            ))
            worker.start()
    
    def _on_mr_created(self, mr: Dict[str, Any]):
        """Handle successful MR creation."""
        QMessageBox.information(
            self,
            "Success",
            f"Merge request !{mr['iid']} created successfully!"
        )
        self._refresh_merge_requests()
    
    def _on_mr_double_clicked(self, item):
        """Handle double-click on MR."""
        row = item.row()
        mr_iid = self.mr_table.item(row, 0).text()
        
        if self.gitlab_client and self.project_path:
            # Open MR in browser
            import webbrowser
            # Construct GitLab URL from project path
            base_url = self.gitlab_client.base_url
            url = f"{base_url}/{self.project_path}/-/merge_requests/{mr_iid}"
            webbrowser.open(url)
