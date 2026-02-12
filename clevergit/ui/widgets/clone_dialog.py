"""
Clone repository dialog widget.
"""

from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QMessageBox,
    QFileDialog,
    QTextEdit,
    QGroupBox,
    QSpinBox,
    QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal


class CloneWorker(QThread):
    """Worker thread for cloning repository to avoid blocking UI."""

    progress = Signal(str)
    finished = Signal(bool, str)  # success, message

    def __init__(
        self,
        url: str,
        path: str,
        branch: Optional[str],
        depth: Optional[int],
        recurse_submodules: bool,
    ):
        super().__init__()
        self.url = url
        self.path = path
        self.branch = branch
        self.depth = depth
        self.recurse_submodules = recurse_submodules

    def run(self):
        """Execute the clone operation."""
        try:
            from clevergit.core.repo import Repo

            def progress_callback(message: str):
                self.progress.emit(message)

            Repo.clone(
                url=self.url,
                path=self.path,
                branch=self.branch if self.branch else None,
                depth=self.depth if self.depth else None,
                recurse_submodules=self.recurse_submodules,
                progress_callback=progress_callback,
            )

            self.finished.emit(True, f"Successfully cloned repository to {self.path}")

        except Exception as e:
            self.finished.emit(False, f"Clone failed: {str(e)}")


class CloneDialog(QDialog):
    """Dialog for cloning a Git repository."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.worker: Optional[CloneWorker] = None
        self.cloned_path: Optional[str] = None

        self.setWindowTitle("Clone Repository")
        self.setGeometry(100, 100, 600, 500)

        layout = QVBoxLayout()

        # Repository URL
        layout.addWidget(QLabel("Repository URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "https://github.com/user/repo.git or git@github.com:user/repo.git"
        )
        layout.addWidget(self.url_input)

        # Destination path
        layout.addWidget(QLabel("Destination Path:"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select or enter destination path")
        path_layout.addWidget(self.path_input)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_button)

        layout.addLayout(path_layout)

        # Clone options group
        options_group = QGroupBox("Clone Options")
        options_layout = QVBoxLayout()

        # Branch selection
        branch_layout = QHBoxLayout()
        self.branch_checkbox = QCheckBox("Clone specific branch:")
        self.branch_checkbox.stateChanged.connect(self._toggle_branch_input)
        branch_layout.addWidget(self.branch_checkbox)

        self.branch_input = QLineEdit()
        self.branch_input.setPlaceholderText("e.g., main, develop")
        self.branch_input.setEnabled(False)
        branch_layout.addWidget(self.branch_input)

        options_layout.addLayout(branch_layout)

        # Shallow clone option
        depth_layout = QHBoxLayout()
        self.shallow_checkbox = QCheckBox("Shallow clone (depth):")
        self.shallow_checkbox.stateChanged.connect(self._toggle_depth_input)
        depth_layout.addWidget(self.shallow_checkbox)

        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setMinimum(1)
        self.depth_spinbox.setMaximum(10000)
        self.depth_spinbox.setValue(1)
        self.depth_spinbox.setEnabled(False)
        depth_layout.addWidget(self.depth_spinbox)
        depth_layout.addStretch()

        options_layout.addLayout(depth_layout)

        # Recursive submodules option
        self.recurse_submodules_checkbox = QCheckBox("Clone submodules recursively")
        options_layout.addWidget(self.recurse_submodules_checkbox)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress display
        layout.addWidget(QLabel("Progress:"))
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMaximumHeight(150)
        layout.addWidget(self.progress_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()

        self.clone_button = QPushButton("Clone")
        self.clone_button.clicked.connect(self._on_clone)
        button_layout.addWidget(self.clone_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _browse_path(self) -> None:
        """Open file dialog to select destination path."""
        path = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory", str(Path.home())
        )

        if path:
            self.path_input.setText(path)

    def _toggle_branch_input(self, state: int) -> None:
        """Enable/disable branch input based on checkbox."""
        self.branch_input.setEnabled(state == Qt.Checked)

    def _toggle_depth_input(self, state: int) -> None:
        """Enable/disable depth input based on checkbox."""
        self.depth_spinbox.setEnabled(state == Qt.Checked)

    def _validate_inputs(self) -> bool:
        """Validate user inputs."""
        url = self.url_input.text().strip()
        path = self.path_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Invalid Input", "Please enter a repository URL")
            return False

        if not path:
            QMessageBox.warning(self, "Invalid Input", "Please enter a destination path")
            return False

        # Check if destination already exists and is not empty
        dest_path = Path(path)
        if dest_path.exists():
            if any(dest_path.iterdir()):
                reply = QMessageBox.question(
                    self,
                    "Directory Not Empty",
                    f"The directory '{path}' already exists and is not empty.\n\n"
                    "Do you want to continue? This may cause conflicts.",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return False

        return True

    def _on_clone(self) -> None:
        """Handle clone button click."""
        if not self._validate_inputs():
            return

        url = self.url_input.text().strip()
        path = self.path_input.text().strip()

        # Get options
        branch = self.branch_input.text().strip() if self.branch_checkbox.isChecked() else None
        depth = self.depth_spinbox.value() if self.shallow_checkbox.isChecked() else None
        recurse_submodules = self.recurse_submodules_checkbox.isChecked()

        # Disable inputs during clone
        self._set_inputs_enabled(False)
        self.clone_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Clear previous progress
        self.progress_text.clear()

        # Create and start worker thread
        self.worker = CloneWorker(url, path, branch, depth, recurse_submodules)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_progress(self, message: str) -> None:
        """Handle progress updates."""
        self.progress_text.append(message)

    def _on_finished(self, success: bool, message: str) -> None:
        """Handle clone completion."""
        self.progress_bar.setVisible(False)
        self._set_inputs_enabled(True)
        self.clone_button.setEnabled(True)

        if success:
            self.progress_text.append(f"\n✓ {message}")
            self.cloned_path = self.path_input.text().strip()
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            self.progress_text.append(f"\n✗ {message}")
            QMessageBox.critical(self, "Error", message)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        if self.worker and self.worker.isRunning():
            # Don't allow canceling during active clone operation
            # as it cannot be safely interrupted
            QMessageBox.warning(
                self,
                "Cannot Cancel",
                "Clone operation is in progress and cannot be safely interrupted.\n\n"
                "Please wait for the operation to complete.",
            )
        else:
            self.reject()

    def _set_inputs_enabled(self, enabled: bool) -> None:
        """Enable/disable all input fields."""
        self.url_input.setEnabled(enabled)
        self.path_input.setEnabled(enabled)
        self.branch_checkbox.setEnabled(enabled)
        self.branch_input.setEnabled(enabled and self.branch_checkbox.isChecked())
        self.shallow_checkbox.setEnabled(enabled)
        self.depth_spinbox.setEnabled(enabled and self.shallow_checkbox.isChecked())
        self.recurse_submodules_checkbox.setEnabled(enabled)

    def get_cloned_path(self) -> Optional[str]:
        """Get the path of the cloned repository."""
        return self.cloned_path
