# Hunk-Based Staging Documentation

## Overview

CleverGit now supports staging specific parts (diff hunks) of a file, allowing you to commit only selected changes while keeping other modifications in your working directory. This is similar to `git add -p` (patch mode) but with a graphical interface.

## Features

### 1. Hunk Parsing
- Automatically parses unified diff output into individual hunks
- Each hunk represents a contiguous block of changes
- Supports multiple hunks per file

### 2. GUI Integration
The diff viewer provides several ways to stage/unstage hunks:

#### Context Menu (Right-Click)
- Select lines in the diff viewer
- Right-click to open context menu
- Choose "Stage Selected Lines" or "Unstage Selected Lines"

#### Control Bar Buttons
- Place cursor within a hunk
- Click "Stage Hunk" or "Unstage Hunk" button
- The entire hunk at cursor position will be staged/unstaged

### 3. Command-Line Interface
For programmatic access, use the core API:

```python
from clevergit.core.diff import (
    get_working_tree_diff,
    parse_diff_hunks,
    create_patch_from_file_hunk
)
from clevergit.git.client import GitClient

# Get working tree diff
diff_result = get_working_tree_diff(repo_path)
file_diff = diff_result.files[0]

# Parse hunks
hunks = parse_diff_hunks(file_diff.diff_text)

# Create patch for first hunk
patch = create_patch_from_file_hunk(file_diff, hunks[0])

# Stage the hunk
client = GitClient(repo_path)
client.stage_hunk(patch)
```

## API Reference

### Core Classes

#### `DiffHunk`
Represents a single diff hunk.

**Attributes:**
- `old_start: int` - Starting line number in old file
- `old_count: int` - Number of lines in old file
- `new_start: int` - Starting line number in new file
- `new_count: int` - Number of lines in new file
- `header: str` - The @@ header line
- `lines: List[str]` - The actual diff lines

**Properties:**
- `text: str` - Full text of the hunk including header

### Core Functions

#### `parse_diff_hunks(diff_text: str) -> List[DiffHunk]`
Parse diff text to extract individual hunks.

**Parameters:**
- `diff_text` - Raw unified diff output

**Returns:**
- List of DiffHunk objects

#### `create_patch_from_hunk(file_path: str, hunk: DiffHunk, is_new_file: bool = False, index_line: str = None) -> str`
Create a complete patch from a single hunk.

**Parameters:**
- `file_path` - Path to the file
- `hunk` - The DiffHunk object
- `is_new_file` - Whether this is for a new file
- `index_line` - Optional index line from original diff

**Returns:**
- Complete patch string including file headers

#### `create_patch_from_file_hunk(file_diff: FileDiff, hunk: DiffHunk) -> str`
Create a patch from a FileDiff and a hunk, including proper index.

**Parameters:**
- `file_diff` - The FileDiff object containing the original diff
- `hunk` - The hunk to create a patch from

**Returns:**
- Complete patch string

### Git Operations

#### `GitClient.apply_patch(patch: str, cached: bool = False, reverse: bool = False) -> None`
Apply a patch to the working directory or index.

**Parameters:**
- `patch` - The patch content to apply
- `cached` - If True, apply to index (stage changes)
- `reverse` - If True, reverse the patch (unstage changes)

#### `GitClient.stage_hunk(hunk_patch: str) -> None`
Stage a specific hunk.

**Parameters:**
- `hunk_patch` - The complete patch including file headers and hunk

#### `GitClient.unstage_hunk(hunk_patch: str) -> None`
Unstage a specific hunk.

**Parameters:**
- `hunk_patch` - The complete patch including file headers and hunk

### GUI Components

#### `DiffViewer`
Enhanced diff viewer widget with hunk staging support.

**New Signals:**
- `stage_hunk_requested(str)` - Emitted when a hunk should be staged
- `unstage_hunk_requested(str)` - Emitted when a hunk should be unstaged

**New Methods:**
- `set_file_path(file_path: str)` - Set the current file path being viewed
- `stage_hunk_at_cursor()` - Stage the hunk at cursor position
- `unstage_hunk_at_cursor()` - Unstage the hunk at cursor position

## Usage Examples

### Example 1: Stage First Hunk of a File

```python
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.core.diff import get_working_tree_diff, parse_diff_hunks, create_patch_from_file_hunk
from clevergit.git.client import GitClient

repo_path = Path("/path/to/repo")
client = GitClient(repo_path)

# Get diff
diff_result = get_working_tree_diff(repo_path)

if diff_result.files:
    file_diff = diff_result.files[0]
    hunks = parse_diff_hunks(file_diff.diff_text)
    
    if hunks:
        # Stage first hunk
        patch = create_patch_from_file_hunk(file_diff, hunks[0])
        client.stage_hunk(patch)
        print(f"Staged hunk: {hunks[0].header}")
```

### Example 2: Selective Staging in Multiple Files

```python
# Get all changed files
diff_result = get_working_tree_diff(repo_path)

for file_diff in diff_result.files:
    print(f"\nFile: {file_diff.new_path}")
    hunks = parse_diff_hunks(file_diff.diff_text)
    
    for i, hunk in enumerate(hunks):
        print(f"  Hunk {i+1}: {hunk.header}")
        # Stage only hunks that modify specific patterns
        if "TODO" in hunk.text or "FIXME" in hunk.text:
            patch = create_patch_from_file_hunk(file_diff, hunk)
            client.stage_hunk(patch)
            print(f"    ✓ Staged")
```

### Example 3: GUI Integration

```python
from PySide6.QtWidgets import QApplication
from clevergit.ui.widgets.diff_viewer import DiffViewer

app = QApplication([])

# Create diff viewer
viewer = DiffViewer(repo_path=repo_path)

# Connect signals
def on_stage_hunk(patch):
    try:
        client = GitClient(repo_path)
        client.stage_hunk(patch)
        print("Hunk staged successfully!")
    except Exception as e:
        print(f"Error: {e}")

viewer.stage_hunk_requested.connect(on_stage_hunk)

# Display diff
diff_result = get_working_tree_diff(repo_path)
viewer.set_file_path("example.txt")
viewer.set_diff(diff_result.diff_text)

app.exec()
```

## Technical Details

### Patch Format
The implementation generates patches in the unified diff format that can be applied with `git apply`. The patches include:

1. File header: `diff --git a/path b/path`
2. Index line: `index <old_blob>..<new_blob> <mode>` (extracted from original diff)
3. Old file reference: `--- a/path`
4. New file reference: `+++ b/path`
5. Hunk header: `@@ -old_start,old_count +new_start,new_count @@`
6. Hunk content: Lines prefixed with `-`, `+`, or ` ` (context)

### Git Apply Options
The implementation uses `git apply --cached --unidiff-zero` for staging:
- `--cached`: Apply to index (staging area) instead of working directory
- `--unidiff-zero`: Allow context-free patches
- `--reverse`: For unstaging operations

### Limitations
- The implementation focuses on unified diff format (not side-by-side patches)
- Context lines from the original diff are preserved
- Binary files are not supported for hunk staging
- Very large files may have performance implications

## Testing

Run the test suite:

```bash
# Test hunk parsing
pytest tests/test_diff.py -v

# Test hunk staging operations
pytest tests/test_hunk_staging.py -v

# Run example
python example_hunk_staging.py
```

## Future Enhancements

Potential improvements for future versions:
1. Interactive hunk editing (modify lines before staging)
2. Split hunk functionality (divide a large hunk into smaller ones)
3. Merge hunks (combine adjacent hunks)
4. Stage individual lines (not just complete hunks)
5. Preview staged changes before committing
6. Undo staging of specific hunks

## Troubleshooting

### "Failed to apply patch" Error
If you encounter this error:
1. Ensure the file hasn't changed since the diff was generated
2. Check that the index line contains valid blob hashes
3. Verify the patch format matches git's expectations

### Hunks Not Detected
If hunks aren't being parsed:
1. Ensure the diff contains `@@` headers
2. Check that the diff is in unified format (not side-by-side)
3. Verify the diff text is complete and not truncated

### Selection Not Working in GUI
If right-click menu doesn't appear:
1. Ensure you've selected text that includes diff content (lines with +/-)
2. Check that the selection includes a complete hunk with `@@` header
3. Verify the file path has been set with `set_file_path()`
