#!/usr/bin/env python3
"""
Demo script for testing the MergeToolWidget.
Creates a sample conflicted file and launches the merge tool.
"""

import sys
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from clevergit.ui.widgets.merge_tool import MergeToolWidget


def create_sample_conflict_file() -> Path:
    """Create a temporary file with sample conflicts."""
    content = """# Sample Configuration File
# This file contains configuration settings

server:
  host: localhost
<<<<<<< HEAD
  port: 8080
  ssl: true
=======
  port: 3000
  ssl: false
>>>>>>> feature-branch

database:
<<<<<<< HEAD
  name: production_db
  user: admin
||||||| base-commit
  name: test_db
  user: testuser
=======
  name: development_db
  user: developer
>>>>>>> feature-branch

# End of configuration
"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.conf',
        delete=False,
        encoding='utf-8'
    )
    temp_file.write(content)
    temp_file.close()
    
    return Path(temp_file.name)


def main():
    """Run the merge tool demo."""
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("CleverGit - Merge Tool Demo")
    window.resize(1400, 900)
    
    # Create central widget with merge tool
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    merge_tool = MergeToolWidget()
    layout.addWidget(merge_tool)
    
    window.setCentralWidget(central_widget)
    
    # Create and load sample conflict file
    conflict_file = create_sample_conflict_file()
    print(f"Created sample conflict file: {conflict_file}")
    
    merge_tool.load_file(conflict_file)
    
    # Connect signals for demo
    def on_conflict_resolved(index):
        print(f"Conflict {index + 1} resolved!")
    
    def on_all_resolved():
        print("All conflicts resolved!")
        print(f"Resolved content saved to: {conflict_file}")
    
    merge_tool.conflict_resolved.connect(on_conflict_resolved)
    merge_tool.all_conflicts_resolved.connect(on_all_resolved)
    
    # Show window
    window.show()
    
    # Run application
    exit_code = app.exec()
    
    # Cleanup
    try:
        conflict_file.unlink()
        print(f"Cleaned up temporary file: {conflict_file}")
    except (FileNotFoundError, OSError) as e:
        print(f"Warning: Could not clean up temporary file: {e}")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
