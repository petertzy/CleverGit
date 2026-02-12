# CleverGit Quick Start Guide

CleverGit provides **three ways** to manage your Git repositories:

## 🖥️ Graphical User Interface (GUI)

Launch the GUI application for an intuitive, visual Git experience:

```bash
sgg
# or
python -m clevergit.ui.main
```

**GUI Features:**
- Click-based repository management
- Visual file status display
- Branch management and switching
- Commit history viewer
- Dialog-based operations

📚 **For detailed documentation, see [GUI_USAGE.md](GUI_USAGE.md)**

## 💻 Command Line Interface (CLI)

Use powerful command-line tools for Git operations:

```bash
# View repository status
sg status

# Commit all changes
sg commit all -m "feat: add new feature"

# View commit history
sg log --oneline

# Branch management
sg branch list           # List all branches
sg branch new feature/x  # Create new branch
sg branch switch main    # Switch branch
```

**CLI Features:**
- Fast and efficient command-line workflow
- Scriptable operations
- Batch processing support
- Integration with other tools

## 🐍 Python API

Use CleverGit programmatically in Python scripts:

```python
from clevergit import Repo

# Open repository
repo = Repo.open(".")

# Check status
status = repo.status()
print(f"Modified files: {len(status.modified)}")

# Create commit
repo.commit_all("fix: resolve issue")

# Branch operations
repo.create_branch("feature/new")
repo.checkout("feature/new")
```

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/petertzy/CleverGit.git
cd CleverGit

# Install with all features
pip install -e .

# Verify installation
sgg --version  # Check GUI
sg --version   # Check CLI
```

## Common Workflows

### Opening a Repository

**GUI Method:**
1. Click the "📁 Open Repository" button
2. Select the repository directory
3. Repository information loads automatically

**CLI Method:**
```bash
cd /path/to/your/repo
sg status
```

### Viewing File Changes

**GUI Method:**
- View changes in the "File Status" panel on the right
- Different colors indicate different statuses:
  - Yellow: Modified files
  - Red: Untracked or conflicted files
  - Green: Staged files

**CLI Method:**
```bash
sg status
```

### Creating a Commit

**GUI Method:**
1. Click the "✅ Commit" button or press Ctrl+K
2. Review the files to be committed
3. Enter your commit message
4. Click "Commit"

**CLI Method:**
```bash
sg commit all -m "Your commit message"
```

### Switching Branches

**GUI Method:**
- Double-click a branch name in the "Branches" panel on the left

**CLI Method:**
```bash
sg branch switch branch-name
```

### Creating a New Branch

**GUI Method:**
1. Click the "New Branch" button in the "Branches" panel
2. Enter the branch name
3. Click OK

**CLI Method:**
```bash
sg branch new branch-name
```

## Keyboard Shortcuts (GUI)

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open Repository |
| Ctrl+Q | Close Application |
| F5 | Refresh |
| Ctrl+K | Create Commit |

## System Requirements

- **Python**: 3.9 or higher
- **Operating System**: macOS, Linux, or Windows
- **Dependencies**: Automatically installed via pip

## Troubleshooting

### GUI fails to start

```bash
# Check if PySide6 is installed
pip list | grep PySide6

# If missing, install manually
pip install PySide6>=6.6.0
```

### Repository operations fail

1. Ensure you have selected the correct repository
2. Check your Git permissions
3. Try clicking "Refresh" to reload the status

### Poor performance with large repositories

- Use the CLI version for batch operations
- Reduce the number of loaded commits
- Consider using shallow clone (`git clone --depth=1`)

## Additional Resources

- 📖 [Project Documentation](README.MD) - Project overview and design
- 📖 [GUI Usage Guide](GUI_USAGE.md) - Detailed GUI documentation
- 📖 [Project Completion Summary](PROJECT_COMPLETION.md) - Implementation details

## Getting Help

If you have questions:
- Review the project documentation
- Check GitHub Issues
- Submit a Pull Request
