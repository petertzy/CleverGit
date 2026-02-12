"""
Git Flow panel widget.

Provides UI for Git Flow workflow management.
"""

from typing import TYPE_CHECKING, Optional, Dict, List
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QDialog,
    QLineEdit,
    QTextEdit,
    QDialogButtonBox,
    QGroupBox,
    QComboBox,
    QTabWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

if TYPE_CHECKING:
    from clevergit.core.repo import Repo

from clevergit.core.git_flow import GitFlow, GitFlowConfig
from clevergit.git.errors import BranchError, UncommittedChangesError


class GitFlowInitDialog(QDialog):
    """Dialog for initializing Git Flow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Initialize Git Flow")
        self.setMinimumWidth(450)

        layout = QVBoxLayout()

        # Info label
        info_label = QLabel(
            "Git Flow uses two main branches:\n"
            "• Master/Main - Production-ready code\n"
            "• Develop - Integration branch for features"
        )
        layout.addWidget(info_label)

        # Master branch
        master_label = QLabel("Production branch name:")
        layout.addWidget(master_label)

        self.master_input = QLineEdit("main")
        layout.addWidget(self.master_input)

        # Develop branch
        develop_label = QLabel("Development branch name:")
        layout.addWidget(develop_label)

        self.develop_input = QLineEdit("develop")
        layout.addWidget(self.develop_input)

        # Prefixes group
        prefix_group = QGroupBox("Branch Prefixes")
        prefix_layout = QVBoxLayout()

        feature_label = QLabel("Feature prefix:")
        prefix_layout.addWidget(feature_label)
        self.feature_input = QLineEdit("feature/")
        prefix_layout.addWidget(self.feature_input)

        release_label = QLabel("Release prefix:")
        prefix_layout.addWidget(release_label)
        self.release_input = QLineEdit("release/")
        prefix_layout.addWidget(self.release_input)

        hotfix_label = QLabel("Hotfix prefix:")
        prefix_layout.addWidget(hotfix_label)
        self.hotfix_input = QLineEdit("hotfix/")
        prefix_layout.addWidget(self.hotfix_input)

        prefix_group.setLayout(prefix_layout)
        layout.addWidget(prefix_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_config(self) -> GitFlowConfig:
        """Get Git Flow configuration from dialog."""
        return GitFlowConfig(
            master_branch=self.master_input.text(),
            develop_branch=self.develop_input.text(),
            feature_prefix=self.feature_input.text(),
            release_prefix=self.release_input.text(),
            hotfix_prefix=self.hotfix_input.text(),
        )


class FeatureDialog(QDialog):
    """Dialog for starting a feature."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start Feature")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        label = QLabel("Feature name:")
        layout.addWidget(label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., user-authentication")
        layout.addWidget(self.name_input)

        info_label = QLabel("This will create a new branch from 'develop'")
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_name(self) -> str:
        """Get feature name from dialog."""
        return self.name_input.text()


class ReleaseDialog(QDialog):
    """Dialog for starting a release."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start Release")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()

        label = QLabel("Version number:")
        layout.addWidget(label)

        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("e.g., 1.0.0")
        layout.addWidget(self.version_input)

        info_label = QLabel("This will create a new release branch from 'develop'")
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_version(self) -> str:
        """Get version from dialog."""
        return self.version_input.text()


class FinishBranchDialog(QDialog):
    """Dialog for finishing a feature/release/hotfix."""

    def __init__(self, branch_type: str, branches: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Finish {branch_type.title()}")
        self.setMinimumWidth(450)

        layout = QVBoxLayout()

        label = QLabel(f"Select {branch_type} to finish:")
        layout.addWidget(label)

        self.branch_combo = QComboBox()
        self.branch_combo.addItems(branches)
        layout.addWidget(self.branch_combo)

        # Tag message for releases and hotfixes
        if branch_type in ["release", "hotfix"]:
            tag_label = QLabel("Tag message (optional):")
            layout.addWidget(tag_label)

            self.tag_message = QTextEdit()
            self.tag_message.setMaximumHeight(80)
            self.tag_message.setPlaceholderText("Optional message for the version tag")
            layout.addWidget(self.tag_message)
        else:
            self.tag_message = None

        info_text = {
            "feature": "This will merge the feature into 'develop' and delete the branch",
            "release": "This will merge into 'main', tag the release, merge back to 'develop', and delete the branch",
            "hotfix": "This will merge into 'main', tag the hotfix, merge back to 'develop', and delete the branch",
        }
        info_label = QLabel(info_text.get(branch_type, ""))
        info_label.setStyleSheet("color: gray;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_branch(self) -> str:
        """Get selected branch."""
        return self.branch_combo.currentText()

    def get_tag_message(self) -> Optional[str]:
        """Get tag message if applicable."""
        if self.tag_message:
            text = self.tag_message.toPlainText().strip()
            return text if text else None
        return None


class GitFlowPanel(QWidget):
    """Git Flow workflow panel."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.repo: Optional["Repo"] = None
        self.git_flow: Optional[GitFlow] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the panel UI."""
        layout = QVBoxLayout()

        # Status section
        status_group = QGroupBox("Git Flow Status")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("Not initialized")
        font = QFont()
        font.setBold(True)
        self.status_label.setFont(font)
        status_layout.addWidget(self.status_label)

        self.config_label = QLabel("")
        self.config_label.setWordWrap(True)
        status_layout.addWidget(self.config_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Initialize button
        self.init_button = QPushButton("Initialize Git Flow")
        self.init_button.clicked.connect(self._initialize_git_flow)
        layout.addWidget(self.init_button)

        # Workflow tabs
        self.workflow_tabs = QTabWidget()

        # Feature tab
        feature_widget = self._create_workflow_tab(
            "Features", "Start Feature", "Finish Feature", self._start_feature, self._finish_feature
        )
        self.workflow_tabs.addTab(feature_widget, "Features")

        # Release tab
        release_widget = self._create_workflow_tab(
            "Releases", "Start Release", "Finish Release", self._start_release, self._finish_release
        )
        self.workflow_tabs.addTab(release_widget, "Releases")

        # Hotfix tab
        hotfix_widget = self._create_workflow_tab(
            "Hotfixes", "Start Hotfix", "Finish Hotfix", self._start_hotfix, self._finish_hotfix
        )
        self.workflow_tabs.addTab(hotfix_widget, "Hotfixes")

        self.workflow_tabs.setEnabled(False)
        layout.addWidget(self.workflow_tabs)

        # Visualization section
        viz_group = QGroupBox("Workflow Visualization")
        viz_layout = QVBoxLayout()

        self.viz_text = QLabel(self._get_workflow_diagram())
        self.viz_text.setWordWrap(True)
        self.viz_text.setStyleSheet(
            "font-family: monospace; background-color: #f5f5f5; padding: 10px;"
        )
        viz_layout.addWidget(self.viz_text)

        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)

        layout.addStretch()
        self.setLayout(layout)

    def _create_workflow_tab(
        self, title: str, start_label: str, finish_label: str, start_callback, finish_callback
    ) -> QWidget:
        """Create a workflow management tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Active branches list
        list_label = QLabel(f"Active {title}:")
        layout.addWidget(list_label)

        list_widget = QListWidget()
        # Store reference based on title
        if "Feature" in title:
            self.feature_list = list_widget
        elif "Release" in title:
            self.release_list = list_widget
        elif "Hotfix" in title:
            self.hotfix_list = list_widget

        layout.addWidget(list_widget)

        # Buttons
        button_layout = QHBoxLayout()

        start_button = QPushButton(start_label)
        start_button.clicked.connect(start_callback)
        button_layout.addWidget(start_button)

        finish_button = QPushButton(finish_label)
        finish_button.clicked.connect(finish_callback)
        button_layout.addWidget(finish_button)

        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _get_workflow_diagram(self) -> str:
        """Get Git Flow workflow diagram."""
        return """Git Flow Workflow:

main     ──●────────────●────────────●──
             \\          /\\          /
              \\        /  \\        /
release        ●──────●    ●──────●
                    /        \\
develop   ──●──────●──────────●──────●──
              \\    /          /
               \\  /          /
feature         ●──────────●

• Features branch from develop
• Releases branch from develop, merge to main
• Hotfixes branch from main, merge to both"""

    def set_repository(self, repo: Optional["Repo"]) -> None:
        """Set the repository for this panel."""
        self.repo = repo

        if self.repo:
            # Initialize GitFlow with default config
            self.git_flow = GitFlow(self.repo.client)
            self._update_status()
        else:
            self.git_flow = None
            self._update_status()

    def _update_status(self) -> None:
        """Update the status display."""
        if not self.git_flow:
            self.status_label.setText("No repository")
            self.status_label.setStyleSheet("color: gray;")
            self.config_label.setText("")
            self.init_button.setEnabled(False)
            self.workflow_tabs.setEnabled(False)
            return

        is_initialized = self.git_flow.is_initialized()

        if is_initialized:
            self.status_label.setText("✓ Initialized")
            self.status_label.setStyleSheet("color: green;")

            config = self.git_flow.config
            config_text = (
                f"Master: {config.master_branch} | "
                f"Develop: {config.develop_branch}\n"
                f"Prefixes: {config.feature_prefix} | "
                f"{config.release_prefix} | {config.hotfix_prefix}"
            )
            self.config_label.setText(config_text)

            self.init_button.setText("Reinitialize Git Flow")
            self.init_button.setEnabled(True)
            self.workflow_tabs.setEnabled(True)

            # Update active branches
            self._update_active_branches()
        else:
            self.status_label.setText("✗ Not initialized")
            self.status_label.setStyleSheet("color: red;")
            self.config_label.setText("Click 'Initialize Git Flow' to set up the workflow")
            self.init_button.setText("Initialize Git Flow")
            self.init_button.setEnabled(True)
            self.workflow_tabs.setEnabled(False)

    def _update_active_branches(self) -> None:
        """Update the lists of active branches."""
        if not self.git_flow:
            return

        try:
            branches = self.git_flow.get_active_branches()

            # Update feature list
            self.feature_list.clear()
            for branch in branches.get("features", []):
                self.feature_list.addItem(branch)

            # Update release list
            self.release_list.clear()
            for branch in branches.get("releases", []):
                self.release_list.addItem(branch)

            # Update hotfix list
            self.hotfix_list.clear()
            for branch in branches.get("hotfixes", []):
                self.hotfix_list.addItem(branch)
        except Exception:
            pass

    def _initialize_git_flow(self) -> None:
        """Initialize Git Flow in the repository."""
        if not self.git_flow:
            return

        dialog = GitFlowInitDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                config = dialog.get_config()
                self.git_flow.config = config
                self.git_flow.initialize(force=self.git_flow.is_initialized())

                QMessageBox.information(self, "Success", "Git Flow initialized successfully!")
                self._update_status()

                # Notify parent to refresh
                if hasattr(self.parent(), "refresh"):
                    self.parent().refresh()
            except (BranchError, UncommittedChangesError) as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to initialize Git Flow: {e}")

    def _start_feature(self) -> None:
        """Start a new feature."""
        if not self.git_flow or not self.git_flow.is_initialized():
            return

        dialog = FeatureDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.get_name()
            if not name:
                QMessageBox.warning(self, "Error", "Feature name cannot be empty")
                return

            try:
                branch_name = self.git_flow.start_feature(name)
                QMessageBox.information(
                    self, "Success", f"Feature branch '{branch_name}' created and checked out"
                )
                self._update_status()

                # Notify parent to refresh
                if hasattr(self.parent(), "refresh"):
                    self.parent().refresh()
            except (BranchError, UncommittedChangesError) as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start feature: {e}")

    def _finish_feature(self) -> None:
        """Finish a feature."""
        if not self.git_flow or not self.git_flow.is_initialized():
            return

        branches = self.git_flow.get_active_branches().get("features", [])
        if not branches:
            QMessageBox.information(self, "Info", "No active feature branches")
            return

        dialog = FinishBranchDialog("feature", branches, self)
        if dialog.exec() == QDialog.Accepted:
            branch_name = dialog.get_branch()

            try:
                self.git_flow.finish_feature(branch_name)
                QMessageBox.information(
                    self, "Success", f"Feature '{branch_name}' merged into develop and deleted"
                )
                self._update_status()

                # Notify parent to refresh
                if hasattr(self.parent(), "refresh"):
                    self.parent().refresh()
            except (BranchError, UncommittedChangesError) as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to finish feature: {e}")

    def _start_release(self) -> None:
        """Start a new release."""
        if not self.git_flow or not self.git_flow.is_initialized():
            return

        dialog = ReleaseDialog(self)
        if dialog.exec() == QDialog.Accepted:
            version = dialog.get_version()
            if not version:
                QMessageBox.warning(self, "Error", "Version cannot be empty")
                return

            try:
                branch_name = self.git_flow.start_release(version)
                QMessageBox.information(
                    self, "Success", f"Release branch '{branch_name}' created and checked out"
                )
                self._update_status()

                # Notify parent to refresh
                if hasattr(self.parent(), "refresh"):
                    self.parent().refresh()
            except (BranchError, UncommittedChangesError) as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start release: {e}")

    def _finish_release(self) -> None:
        """Finish a release."""
        if not self.git_flow or not self.git_flow.is_initialized():
            return

        branches = self.git_flow.get_active_branches().get("releases", [])
        if not branches:
            QMessageBox.information(self, "Info", "No active release branches")
            return

        dialog = FinishBranchDialog("release", branches, self)
        if dialog.exec() == QDialog.Accepted:
            branch_name = dialog.get_branch()
            tag_message = dialog.get_tag_message()

            try:
                self.git_flow.finish_release(branch_name, tag_message=tag_message)
                QMessageBox.information(
                    self, "Success", f"Release '{branch_name}' merged, tagged, and deleted"
                )
                self._update_status()

                # Notify parent to refresh
                if hasattr(self.parent(), "refresh"):
                    self.parent().refresh()
            except (BranchError, UncommittedChangesError) as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to finish release: {e}")

    def _start_hotfix(self) -> None:
        """Start a new hotfix."""
        if not self.git_flow or not self.git_flow.is_initialized():
            return

        dialog = ReleaseDialog(self)  # Reuse ReleaseDialog since it's the same
        dialog.setWindowTitle("Start Hotfix")
        if dialog.exec() == QDialog.Accepted:
            version = dialog.get_version()
            if not version:
                QMessageBox.warning(self, "Error", "Version cannot be empty")
                return

            try:
                branch_name = self.git_flow.start_hotfix(version)
                QMessageBox.information(
                    self, "Success", f"Hotfix branch '{branch_name}' created and checked out"
                )
                self._update_status()

                # Notify parent to refresh
                if hasattr(self.parent(), "refresh"):
                    self.parent().refresh()
            except (BranchError, UncommittedChangesError) as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start hotfix: {e}")

    def _finish_hotfix(self) -> None:
        """Finish a hotfix."""
        if not self.git_flow or not self.git_flow.is_initialized():
            return

        branches = self.git_flow.get_active_branches().get("hotfixes", [])
        if not branches:
            QMessageBox.information(self, "Info", "No active hotfix branches")
            return

        dialog = FinishBranchDialog("hotfix", branches, self)
        if dialog.exec() == QDialog.Accepted:
            branch_name = dialog.get_branch()
            tag_message = dialog.get_tag_message()

            try:
                self.git_flow.finish_hotfix(branch_name, tag_message=tag_message)
                QMessageBox.information(
                    self, "Success", f"Hotfix '{branch_name}' merged, tagged, and deleted"
                )
                self._update_status()

                # Notify parent to refresh
                if hasattr(self.parent(), "refresh"):
                    self.parent().refresh()
            except (BranchError, UncommittedChangesError) as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to finish hotfix: {e}")

    def refresh(self) -> None:
        """Refresh the panel display."""
        self._update_status()
