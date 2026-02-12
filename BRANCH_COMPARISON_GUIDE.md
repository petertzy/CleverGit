# Branch Comparison Feature

## Overview
The branch comparison feature allows users to compare two branches and view their differences, including:
- Commits that are ahead/behind
- List of different files
- Detailed commit information
- Statistics and summary

## Usage

### Command Line (Python API)
```python
from clevergit.core.repo import Repo

# Open a repository
repo = Repo.open("/path/to/repo")

# Compare two branches
comparison = repo.compare_branches("base_branch", "compare_branch")

# View statistics
print(f"Ahead: {comparison.ahead_count} commits")
print(f"Behind: {comparison.behind_count} commits")
print(f"Different files: {len(comparison.different_files)}")
print(f"Summary: {comparison.summary()}")

# Access detailed information
for commit_sha in comparison.ahead_commits:
    print(f"  {commit_sha}")

for file_path in comparison.different_files:
    print(f"  {file_path}")
```

### GUI Interface
1. Open the CleverGit GUI
2. Navigate to the "Branches" tab
3. Click the "Compare" button
4. The dialog shows your current branch and allows you to select another branch to compare with
5. Select a branch from the dropdown menu
6. Click "Compare" to see the results

The comparison dialog displays:
- **Current Branch**: Your active branch (displayed as read-only)
- **Compare Branch**: Select a branch to compare against the current branch
- **Summary**: Human-readable summary of the comparison
- **Statistics**: Number of commits ahead/behind and different files
- **Ahead Commits**: List of commits in the compare branch but not in current branch
- **Behind Commits**: List of commits in the current branch but not in compare branch
- **Different Files**: List of files that differ between branches
  - **Double-click a file** to view the code differences for that specific file
- **Commit Details**: Double-click any commit to view its details and changes

## Implementation Details

### Core Components

#### 1. BranchComparison Model (`clevergit/models/branch_comparison.py`)
Data model representing comparison results:
- `base_branch`: The base branch name
- `compare_branch`: The branch being compared
- `ahead_commits`: List of commit SHAs ahead
- `behind_commits`: List of commit SHAs behind
- `different_files`: List of differing file paths
- Properties: `ahead_count`, `behind_count`, `is_up_to_date`
- Methods: `summary()` for human-readable output

#### 2. Core Functions (`clevergit/core/branch.py`)
- `compare_branches(client, base_branch, compare_branch)`: Main comparison function
  - Validates both branches exist
  - Gets commit differences
  - Gets file differences
  - Returns BranchComparison object

#### 3. GitClient Methods (`clevergit/git/client.py`)
- `compare_branches(base, compare)`: Gets ahead/behind commit SHAs using `git rev-list`
- `get_different_files(base, compare)`: Lists files that differ using `git diff --name-only`

#### 4. UI Dialog (`clevergit/ui/widgets/branch_compare_dialog.py`)
- Branch selection dropdowns
- Compare button to trigger comparison
- Statistics display (ahead/behind/files)
- Commit lists (ahead/behind) with double-click for details
- File list showing all different files
- Commit details viewer with diff display

### Git Commands Used
- `git rev-list base..compare`: Get commits ahead
- `git rev-list compare..base`: Get commits behind
- `git diff --name-only base compare`: Get different files
- `git show -s <sha>`: Get commit details
- `git diff <sha>^ <sha>`: Get commit changes

## Testing

### Unit Tests (`tests/test_branch.py`)
Comprehensive test suite covering:
- Basic branch comparison
- Diverged branches (ahead and behind)
- Up-to-date branches
- File difference detection
- Error handling (nonexistent branches)
- Summary generation

Run tests:
```bash
pytest tests/test_branch.py -v
```

### Integration Testing
Manual integration testing can be done using the provided test script:
```bash
python /tmp/test_integration.py
```

## Error Handling
- **BranchError**: Raised when a specified branch doesn't exist
- **GitCommandError**: Raised when Git commands fail
- UI displays user-friendly error messages via message boxes

## Future Enhancements
Possible improvements for future versions:
- Support for comparing with remote branches
- Ability to merge directly from comparison dialog
- Export comparison results to file
- Visual diff viewer for files
- Commit graph visualization
- Filter/search commits and files
