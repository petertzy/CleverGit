#!/usr/bin/env python3
"""
Example demonstrating the improved diff viewer.
This example shows how to use the enhanced diff viewer with the new features.
"""

from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from clevergit.core.diff import get_working_tree_diff
from clevergit.ui.widgets.diff_viewer import DiffViewer

class DiffExampleWindow(QMainWindow):
    """Example window demonstrating the improved diff viewer."""
    
    def __init__(self, repo_path: Path):
        super().__init__()
        self.repo_path = repo_path
        
        self.setWindowTitle("CleverGit Diff Viewer - Improved Presentation")
        self.resize(1400, 900)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Add info button
        info_btn = QPushButton("ℹ️  About the Improvements")
        info_btn.clicked.connect(self.show_info)
        layout.addWidget(info_btn)
        
        # Create diff viewer
        self.viewer = DiffViewer()
        layout.addWidget(self.viewer)
        
        # Load diff
        self.load_diff()
    
    def load_diff(self):
        """Load the diff from the repository."""
        try:
            diff_result = get_working_tree_diff(self.repo_path)
            
            self.viewer.set_diff(
                diff_result.diff_text,
                stats={
                    'files_changed': diff_result.stats.files_changed,
                    'insertions': diff_result.stats.insertions,
                    'deletions': diff_result.stats.deletions
                }
            )
        except Exception as e:
            print(f"Error loading diff: {e}")
    
    def show_info(self):
        """Show information about the improvements."""
        from PySide6.QtWidgets import QMessageBox
        
        info_text = """
<h3>Diff Viewer Improvements</h3>

<p><b>SmartGit-inspired enhancements for better code review experience:</b></p>

<ul>
<li><b>Enhanced Color Scheme:</b> Softer, professional colors that reduce eye strain
    <ul>
    <li>Added lines: Light green background (#d4f8d4)</li>
    <li>Deleted lines: Light red background (#ffd7d7)</li>
    <li>Better visual hierarchy with colored backgrounds</li>
    </ul>
</li>

<li><b>Word-Level Highlighting:</b> Changed words within lines are emphasized with darker, bolder colors</li>

<li><b>Improved Visual Spacing:</b>
    <ul>
    <li>8px padding for better readability</li>
    <li>Visual separators between files</li>
    <li>Better line height (1.4)</li>
    <li>Rounded corners and modern borders</li>
    </ul>
</li>

<li><b>Enhanced Stats Display:</b> More descriptive labels with color coding
    <ul>
    <li>Before: "Files changed: 2 | +15 | -8"</li>
    <li>After: "2 files changed | +15 additions | -8 deletions"</li>
    </ul>
</li>

<li><b>Better Side-by-Side View:</b> 
    <ul>
    <li>Left panel: Subtle red tint (for deletions)</li>
    <li>Right panel: Subtle green tint (for additions)</li>
    </ul>
</li>
</ul>

<p><b>Try it out:</b></p>
<ul>
<li>Switch between Unified and Side-by-Side views</li>
<li>Use Previous/Next buttons to navigate between changes</li>
<li>Toggle "Collapse Unchanged" to focus on modifications</li>
<li>Look for the bold, darker highlights on changed words!</li>
</ul>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About the Improvements")
        msg.setTextFormat(1)  # RichText
        msg.setText(info_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python example_improved_diff_viewer.py <path-to-repo>")
        print("\nExample:")
        print("  python example_improved_diff_viewer.py /path/to/your/repo")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    if not (repo_path / ".git").exists():
        print(f"Error: Not a git repository: {repo_path}")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    window = DiffExampleWindow(repo_path)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
