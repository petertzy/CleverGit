# Merge Tool Documentation

## Overview

The CleverGit Merge Tool provides a visual interface for resolving Git merge conflicts. It features a three-way merge view that displays the Base (common ancestor), Ours (current branch), and Theirs (incoming branch) versions side-by-side, making it easy to understand and resolve conflicts.

## Features

### Core Features
- **Three-Way Merge View**: Display Base, Ours, and Theirs versions simultaneously
- **Quick Resolution Actions**: 
  - Take Ours - Accept current branch changes
  - Take Theirs - Accept incoming branch changes
  - Take Both - Combine both versions
- **Manual Editing**: Full text editor for custom conflict resolution
- **Conflict Navigation**: Navigate between multiple conflicts in a file
- **Visual Conflict Tracking**: See which conflicts are resolved
- **Auto-Save Protection**: Prevents saving until all conflicts are resolved

### Conflict Marker Support
- Standard two-way conflicts (<<<<<<< / ======= / >>>>>>>)
- Diff3-style conflicts with base (<<<<<<< / ||||||| / ======= / >>>>>>>)
- Multiple conflicts per file

## Usage

### Python API

#### Basic Usage

```python
from pathlib import Path
from clevergit.core.conflict import (
    parse_conflicted_file,
    resolve_conflict_take_ours,
    resolve_all_conflicts
)

# Parse a file with conflicts
file_path = Path("conflicted_file.txt")
conflicted_file = parse_conflicted_file(file_path)

# Check if file has conflicts
if conflicted_file.has_conflicts():
    print(f"Found {conflicted_file.get_conflict_count()} conflicts")
    
    # Resolve first conflict by taking "ours"
    conflict = conflicted_file.conflicts[0]
    resolution = resolve_conflict_take_ours(conflict)
    
    # Apply resolution to all conflicts
    resolutions = [resolution]  # One resolution per conflict
    resolved_content = resolve_all_conflicts(conflicted_file, resolutions)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(resolved_content)
```

#### Resolution Functions

```python
from clevergit.core.conflict import (
    resolve_conflict_take_ours,
    resolve_conflict_take_theirs,
    resolve_conflict_take_both
)

# Take our version
ours_resolution = resolve_conflict_take_ours(conflict)

# Take their version
theirs_resolution = resolve_conflict_take_theirs(conflict)

# Take both (ours first, then theirs)
both_resolution = resolve_conflict_take_both(conflict, ours_first=True)

# Take both (theirs first, then ours)
both_reversed = resolve_conflict_take_both(conflict, ours_first=False)
```

### GUI Usage

#### Standalone Merge Tool

```python
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from clevergit.ui.widgets.merge_tool import MergeToolWidget

app = QApplication(sys.argv)

# Create main window
window = QMainWindow()
window.setWindowTitle("Merge Tool")
window.resize(1400, 900)

# Add merge tool widget
merge_tool = MergeToolWidget()
window.setCentralWidget(merge_tool)

# Load conflicted file
merge_tool.load_file(Path("path/to/conflicted_file.txt"))

# Connect signals
merge_tool.conflict_resolved.connect(
    lambda idx: print(f"Conflict {idx + 1} resolved")
)
merge_tool.all_conflicts_resolved.connect(
    lambda: print("All conflicts resolved!")
)

window.show()
sys.exit(app.exec())
```

#### Integration with Main Application

```python
from clevergit.ui.widgets.merge_tool import MergeToolWidget

# In your main window
merge_tool = MergeToolWidget()
layout.addWidget(merge_tool)

# Load file when needed
merge_tool.load_file(conflict_file_path)

# Check resolution status
if merge_tool.is_all_resolved():
    resolved_content = merge_tool.get_resolved_content()
```

## Workflow

### Typical Merge Conflict Resolution Workflow

1. **Detect Conflicts**: After a merge or rebase operation fails
   ```python
   from clevergit.core.merge import get_conflict_files
   
   conflicts = get_conflict_files(repo_path)
   if conflicts:
       print(f"Conflicts in: {conflicts}")
   ```

2. **Load File in Merge Tool**: Open the file in the merge tool widget
   ```python
   merge_tool.load_file(Path(conflicts[0]))
   ```

3. **Review Conflicts**: View the three-way merge display:
   - **Base**: Original version before changes
   - **Ours**: Your current branch version
   - **Theirs**: Incoming branch version

4. **Resolve Each Conflict**:
   - Click "Take Ours" to keep your version
   - Click "Take Theirs" to accept their version
   - Click "Take Both" to combine both versions
   - Or manually edit in the Result editor

5. **Mark as Resolved**: Click "Mark as Resolved" to save the resolution

6. **Navigate**: Use Previous/Next buttons to move between conflicts

7. **Save All**: Once all conflicts are resolved, click "Save All Resolutions"

8. **Stage and Commit**: Stage the resolved file and commit
   ```python
   from clevergit.core.repo import Repo
   
   repo = Repo(repo_path)
   repo.stage_files([resolved_file])
   repo.commit("Resolved merge conflicts")
   ```

## API Reference

### Core Module (`clevergit.core.conflict`)

#### Classes

**ConflictBlock**
- `start_line: int` - Line number where conflict starts
- `end_line: int` - Line number where conflict ends
- `ours_label: str` - Label from <<<<<<< line
- `theirs_label: str` - Label from >>>>>>> line
- `ours_content: List[str]` - Lines in "ours" section
- `theirs_content: List[str]` - Lines in "theirs" section
- `base_content: Optional[List[str]]` - Lines in base section (if present)
- `has_base() -> bool` - Check if base is available
- `get_ours_text() -> str` - Get ours content as string
- `get_theirs_text() -> str` - Get theirs content as string
- `get_base_text() -> str` - Get base content as string

**ConflictedFile**
- `file_path: str` - Path to the file
- `conflicts: List[ConflictBlock]` - List of conflicts in file
- `original_content: List[str]` - Original file lines
- `get_conflict_count() -> int` - Number of conflicts
- `has_conflicts() -> bool` - Whether file has conflicts

#### Functions

**parse_conflict_markers(content: str) -> List[ConflictBlock]**
- Parse conflict markers from file content
- Returns list of ConflictBlock objects

**parse_conflicted_file(file_path: Path) -> ConflictedFile**
- Parse a file and extract all conflicts
- Returns ConflictedFile object

**has_conflict_markers(content: str) -> bool**
- Check if content contains conflict markers

**resolve_conflict_take_ours(conflict: ConflictBlock) -> List[str]**
- Resolve by taking "ours" version

**resolve_conflict_take_theirs(conflict: ConflictBlock) -> List[str]**
- Resolve by taking "theirs" version

**resolve_conflict_take_both(conflict: ConflictBlock, ours_first: bool = True) -> List[str]**
- Resolve by taking both versions

**apply_resolution(conflicted_file: ConflictedFile, conflict_index: int, resolved_content: List[str]) -> str**
- Apply resolution to specific conflict

**resolve_all_conflicts(conflicted_file: ConflictedFile, resolutions: List[List[str]]) -> str**
- Apply resolutions to all conflicts and return final content

### UI Widget (`clevergit.ui.widgets.merge_tool`)

#### MergeToolWidget

**Signals**
- `conflict_resolved(int)` - Emitted when a conflict is resolved (index)
- `all_conflicts_resolved()` - Emitted when all conflicts are resolved

**Methods**
- `load_file(file_path: Path)` - Load a conflicted file
- `get_resolved_content() -> Optional[str]` - Get fully resolved content
- `is_all_resolved() -> bool` - Check if all conflicts are resolved

## Examples

### Example 1: Command-Line Conflict Resolution

```python
#!/usr/bin/env python3
from pathlib import Path
from clevergit.core.conflict import (
    parse_conflicted_file,
    resolve_conflict_take_ours,
    resolve_conflict_take_theirs,
    resolve_all_conflicts
)

def resolve_conflicts_cli(file_path: Path):
    """Resolve conflicts from command line."""
    conflicted = parse_conflicted_file(file_path)
    
    if not conflicted.has_conflicts():
        print("No conflicts found!")
        return
    
    resolutions = []
    
    for i, conflict in enumerate(conflicted.conflicts, 1):
        print(f"\nConflict {i}/{conflicted.get_conflict_count()}")
        print(f"Ours ({conflict.ours_label}):")
        print(conflict.get_ours_text())
        print(f"\nTheirs ({conflict.theirs_label}):")
        print(conflict.get_theirs_text())
        
        choice = input("\nResolve with (o)urs, (t)heirs, (b)oth? ").lower()
        
        if choice == 'o':
            resolutions.append(resolve_conflict_take_ours(conflict))
        elif choice == 't':
            resolutions.append(resolve_conflict_take_theirs(conflict))
        elif choice == 'b':
            resolutions.append(resolve_conflict_take_both(conflict))
        else:
            print("Invalid choice, taking ours by default")
            resolutions.append(resolve_conflict_take_ours(conflict))
    
    # Apply all resolutions
    resolved = resolve_all_conflicts(conflicted, resolutions)
    
    # Save to file
    with open(file_path, 'w') as f:
        f.write(resolved)
    
    print(f"\n✓ All conflicts resolved and saved to {file_path}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python resolve_cli.py <file_path>")
        sys.exit(1)
    
    resolve_conflicts_cli(Path(sys.argv[1]))
```

### Example 2: Automatic Resolution Strategy

```python
from pathlib import Path
from clevergit.core.conflict import (
    parse_conflicted_file,
    resolve_conflict_take_ours,
    resolve_conflict_take_theirs,
    resolve_all_conflicts
)

def auto_resolve_prefer_ours(file_path: Path):
    """Automatically resolve all conflicts by preferring 'ours'."""
    conflicted = parse_conflicted_file(file_path)
    
    resolutions = [
        resolve_conflict_take_ours(conflict)
        for conflict in conflicted.conflicts
    ]
    
    resolved = resolve_all_conflicts(conflicted, resolutions)
    
    with open(file_path, 'w') as f:
        f.write(resolved)
    
    print(f"Resolved {len(resolutions)} conflicts in {file_path}")

def auto_resolve_prefer_theirs(file_path: Path):
    """Automatically resolve all conflicts by preferring 'theirs'."""
    conflicted = parse_conflicted_file(file_path)
    
    resolutions = [
        resolve_conflict_take_theirs(conflict)
        for conflict in conflicted.conflicts
    ]
    
    resolved = resolve_all_conflicts(conflicted, resolutions)
    
    with open(file_path, 'w') as f:
        f.write(resolved)
    
    print(f"Resolved {len(resolutions)} conflicts in {file_path}")
```

## Testing

Run the conflict resolution tests:

```bash
pytest tests/test_conflict.py -v
```

All 20 tests should pass, covering:
- Simple and diff3 conflict parsing
- Multiple conflicts per file
- Resolution functions (take_ours, take_theirs, take_both)
- File parsing and writing
- Error handling

## Notes

- The merge tool preserves the original line structure when possible
- Empty resolutions are not allowed (must provide content)
- All conflicts must be resolved before saving
- The tool supports both standard and diff3-style conflict markers
- Syntax highlighting helps distinguish between sections
- `example_conflict_resolution.py` demonstrates CLI usage without GUI dependencies
- `test_merge_tool_ui.py` provides a GUI demo using PySide6/Qt (requires display libraries)
