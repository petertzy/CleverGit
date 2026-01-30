# CleverGit GUI Usage Guide

## Starting the GUI Application

After installing the project, you can launch the CleverGit GUI in two ways:

### Method 1: Using Command Line

```bash
sgg
```

or

```bash
python -m clevergit.ui.main
```

### Method 2: From Python

```python
from clevergit.ui.main import main
main()
```

## GUI Features

### 1. **Main Window**

The main window provides:

- **Top Toolbar**: Quick access buttons for common operations
  - 📁 **Open Repository** - Select a Git repository to work with
  - 🔄 **Refresh** - Update all views with latest repository data
  - ✅ **Commit** - Create a new commit
  - Path display showing current repository

### 2. **Left Panel - Repository Info & Branches**

- **Repository Info**: Shows current path, branch, and status
- **Branches**: 
  - View all local and remote branches
  - Double-click to switch branches
  - Create new branches
  - Delete branches

### 3. **Right Panel - Status & History**

- **File Status**: 
  - Modified files (yellow)
  - Untracked files (red)
  - Staged files (green)
  - Conflicted files (red)
  
- **Commit History**: 
  - View recent commits (default: last 20)
  - Shows hash, author, date, and message

### 4. **Commit Dialog**

When creating a commit:

- View all files that will be committed
- Enter commit message
- Option to "Commit all changes"
- Option to "Allow empty commit"

## Menu Bar

### File Menu

- **Open Repository** (Ctrl+O) - Open a repository directory
- **Exit** (Ctrl+Q) - Close the application

### Edit Menu

- **Refresh** (F5) - Refresh all views

### Commit Menu

- **New Commit** (Ctrl+K) - Open commit dialog

### Help Menu

- **About** - Show application information

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open Repository |
| Ctrl+Q | Exit Application |
| F5 | Refresh |
| Ctrl+K | New Commit |

## Common Workflows

### Opening a Repository

1. Click "📁 Open Repository" button
2. Select the repository directory
3. The GUI will load all repository information

### Viewing Changes

1. After opening a repository, the "File Status" panel shows all changes
2. Different colors indicate different statuses:
   - Yellow: Modified files
   - Red: Untracked or conflicted files
   - Green: Staged files

### Creating a Commit

1. Click "✅ Commit" button or press Ctrl+K
2. Review the files that will be committed
3. Enter a meaningful commit message
4. Click "Commit" to create the commit

### Switching Branches

1. Double-click on a branch in the "Branches" panel
2. The GUI will switch to that branch and refresh automatically

### Creating a New Branch

1. Click the "New Branch" button in the "Branches" panel
2. Enter the branch name
3. Click OK to create the branch

## System Requirements

- **Python**: 3.9 or higher
- **OS**: macOS, Linux, or Windows
- **Dependencies**: Automatically installed via pip

## Troubleshooting

### GUI doesn't start

```bash
# Check if PySide6 is installed
pip list | grep PySide6

# If missing, install it
pip install PySide6>=6.6.0
```

### Repository operations fail

1. Ensure you have the correct repository selected
2. Check that you have proper Git permissions
3. Try clicking "Refresh" to reload repository state

### Slow performance with large repositories

- The GUI loads commit history for better performance
- Large repositories may take a few seconds to load
- Try limiting operations or use the CLI version for batch operations

## Features in Development

The following features are planned for future releases:

- [ ] Stashing changes
- [ ] Rebasing branches
- [ ] Merging branches visually
- [ ] Conflict resolution wizard
- [ ] Remote repository management
- [ ] Tag management
- [ ] Settings/Preferences dialog
- [ ] Dark mode theme

## Getting Help

For more information:

- Check [README.MD](README.MD) for project overview
- Review [README_zh.md](README_zh.md) for quick start guide
- See [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) for implementation details
