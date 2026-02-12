# Diff Viewer Module

This module provides an advanced file difference viewer for CleverGit.

## Components

### Core Module: `clevergit/core/diff.py`

The core diff module provides functions for computing and analyzing file differences:

#### Functions

- **`get_working_tree_diff(repo_path, file_path=None)`**
  - Compares working tree changes against HEAD
  - Returns `DiffResult` with diff text, stats, and file information

- **`get_staged_diff(repo_path, file_path=None)`**
  - Compares staged changes against HEAD
  - Returns `DiffResult` with diff text, stats, and file information

- **`get_commit_diff(repo_path, commit_sha, file_path=None)`**
  - Shows changes introduced by a specific commit
  - Returns `DiffResult` with diff text, stats, and file information

- **`get_commit_range_diff(repo_path, commit_sha1, commit_sha2, file_path=None)`**
  - Compares two commits
  - Returns `DiffResult` with diff text, stats, and file information

#### Data Models

- **`DiffMode`** - Enum for diff types (WORKING_TREE, STAGED, COMMIT, COMMIT_RANGE)
- **`DiffStats`** - Statistics about a diff (files changed, insertions, deletions)
- **`FileDiff`** - Per-file diff information
- **`DiffResult`** - Complete diff result with all information

#### Helper Functions

- **`find_next_diff(diff_text, current_line)`** - Find next diff hunk
- **`find_previous_diff(diff_text, current_line)`** - Find previous diff hunk

### UI Widget: `clevergit/ui/widgets/diff_viewer.py`

The diff viewer widget provides a rich UI for displaying and navigating diffs:

#### Features

1. **Multiple View Modes**
   - Unified diff view (traditional diff format)
   - Side-by-side comparison view

2. **Syntax Highlighting**
   - Color-coded added/deleted/context lines
   - Highlighted file headers and hunk markers

3. **Navigation**
   - Next/Previous buttons to jump between changes
   - Automatic scrolling to focused change

4. **Statistics Display**
   - Shows files changed, insertions, and deletions
   - Real-time updates when diff changes

5. **Display Options**
   - Toggle line numbers on/off
   - Collapse/expand unchanged sections
   - Switch between view modes

#### Usage Example

```python
from PySide6.QtWidgets import QApplication
from clevergit.ui.widgets.diff_viewer import DiffViewer

app = QApplication([])

# Create diff viewer
viewer = DiffViewer()

# Load a diff
diff_text = "..."  # Your diff content
stats = {
    'files_changed': 2,
    'insertions': 15,
    'deletions': 8
}
viewer.set_diff(diff_text, stats)

# Show the viewer
viewer.show()
app.exec()
```

## Integration Example

```python
from pathlib import Path
from clevergit.core.diff import get_working_tree_diff
from clevergit.ui.widgets.diff_viewer import DiffViewer

# Get diff from repository
repo_path = Path("/path/to/repo")
diff_result = get_working_tree_diff(repo_path)

# Display in viewer
viewer = DiffViewer()
viewer.set_diff(
    diff_result.diff_text,
    stats={
        'files_changed': diff_result.stats.files_changed,
        'insertions': diff_result.stats.insertions,
        'deletions': diff_result.stats.deletions
    }
)
viewer.show()
```

## Testing

Comprehensive tests are available in `tests/test_diff.py`:

```bash
# Run diff module tests
pytest tests/test_diff.py -v

# Run with coverage
pytest tests/test_diff.py --cov=clevergit.core.diff
```

## API Reference

### DiffResult

```python
@dataclass
class DiffResult:
    mode: DiffMode              # Type of diff
    diff_text: str              # Raw unified diff
    stats: DiffStats            # Statistics
    files: List[FileDiff]       # Per-file information
    commit_sha: Optional[str]   # First commit (if applicable)
    commit_sha2: Optional[str]  # Second commit (if applicable)
```

### DiffStats

```python
@dataclass
class DiffStats:
    files_changed: int          # Number of files modified
    insertions: int             # Number of lines added
    deletions: int              # Number of lines deleted
    
    @property
    def total_changes(self) -> int:
        """Total number of line changes."""
        return self.insertions + self.deletions
```

### FileDiff

```python
@dataclass
class FileDiff:
    old_path: str              # Path in old version
    new_path: str              # Path in new version
    status: str                # 'added', 'deleted', 'modified', 'renamed'
    diff_text: str             # Diff for this file
    insertions: int            # Lines added in this file
    deletions: int             # Lines deleted in this file
```

## Implementation Details

### Diff Computation

The diff module uses the Git command-line interface through `GitClient` to compute diffs:
- Working tree diffs: `git diff HEAD`
- Staged diffs: `git diff --cached`
- Commit diffs: `git show <commit>`
- Commit range diffs: `git diff <commit1> <commit2>`

### Syntax Highlighting

The `DiffSyntaxHighlighter` class uses Qt's syntax highlighting framework to color-code:
- Green background for added lines
- Red background for deleted lines
- Blue text for hunk headers
- Gray text for file headers
- Black text for context lines

### Side-by-Side View

The side-by-side view parses unified diff format and splits it into:
- Left pane: Original content (shows deleted lines)
- Right pane: Modified content (shows added lines)
- Context lines shown on both sides
- Synchronized scrolling between panes

## Future Enhancements

Possible improvements for future versions:
- Word-level diff highlighting
- Inline editing capabilities
- Export diff to various formats (HTML, PDF)
- Custom color schemes
- Line-by-line comparison mode
- Integration with merge conflict resolution
- Diff search functionality
- Bookmark specific diff locations
