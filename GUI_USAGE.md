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
  - ⬇️ **Clone** - Clone a repository from a URL
  - 📁 **Open Repository** - Select a Git repository to work with
  - 🔄 **Refresh** - Update all views with latest repository data
  - ✅ **Commit** - Create a new commit
  - ⬇️ **Pull** - Pull changes from remote repository
  - ⬆️ **Push** - Push commits to remote repository
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
- Select specific files to commit (multi-select with Ctrl/Cmd+Click)
- Enter commit message
- Option to "Commit all changes" - commits all modified and untracked files
- Option to commit only selected files - uncheck "Commit all changes" and select specific files
- Option to "Allow empty commit"

## Menu Bar

### File Menu

- **Clone Repository** (Ctrl+Shift+C) - Clone a repository from a URL
- **Open Repository** (Ctrl+O) - Open a repository directory
- **Exit** (Ctrl+Q) - Close the application

### Edit Menu

- **Refresh** (F5) - Refresh all views

### Commit Menu

- **New Commit** (Ctrl+K) - Open commit dialog

### Remote Menu

- **Pull** (Ctrl+Shift+P) - Pull changes from remote repository
- **Push** (Ctrl+Shift+U) - Push commits to remote repository

### View Menu

- **Command Palette** (Ctrl+P) - Quick search and command execution
  - Search files with fuzzy matching
  - Search commits by message or SHA
  - Search and checkout branches
  - Execute commands quickly
- **Theme** - Choose visual theme for the application
  - **Light** - GitHub-inspired light theme with bright backgrounds
  - **Dark** - VS Code-inspired dark theme for reduced eye strain
  - **Follow System** - Automatically match your operating system's theme preference

### Help Menu

- **About** - Show application information

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift+C | Clone Repository |
| Ctrl+O | Open Repository |
| Ctrl+Q | Exit Application |
| F5 | Refresh |
| Ctrl+K | New Commit |
| Ctrl+Shift+P | Pull from Remote |
| Ctrl+Shift+U | Push to Remote |

## Common Workflows

### Cloning a Repository

CleverGit supports cloning repositories from both HTTPS and SSH URLs with advanced options.

**Basic Clone:**

1. Click "⬇️ Clone" button or press Ctrl+Shift+C
2. Enter the repository URL (e.g., `https://github.com/user/repo.git` or `git@github.com:user/repo.git`)
3. Select or enter the destination directory path
4. Click "Clone" to start the cloning process
5. The GUI will show real-time progress updates
6. Once complete, the cloned repository will automatically open in CleverGit

**Advanced Clone Options:**

The clone dialog provides several advanced options:

- **Clone specific branch:**
  - Check "Clone specific branch" checkbox
  - Enter the branch name (e.g., `main`, `develop`, `feature/xyz`)
  - Only the specified branch will be cloned

- **Shallow clone:**
  - Check "Shallow clone (depth)" checkbox
  - Set the depth (default: 1)
  - Only the specified number of recent commits will be cloned
  - Useful for large repositories when you don't need full history

- **Clone submodules recursively:**
  - Check "Clone submodules recursively"
  - All submodules will be cloned along with the main repository

**Clone Progress:**

- The clone dialog shows real-time progress messages
- A progress bar indicates the operation is ongoing
- The dialog cannot be canceled during an active clone operation (to ensure repository integrity)
- Once complete, a success message is displayed

**Supported Protocols:**

- **HTTPS**: `https://github.com/user/repo.git`
- **SSH**: `git@github.com:user/repo.git`

**Authentication:**

- HTTPS: Git credential manager or SSH agent handles authentication automatically
- SSH: Ensure your SSH keys are properly configured

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

**Option 1: Commit All Changes**

1. Click "✅ Commit" button or press Ctrl+K
2. Review the files that will be committed
3. Keep "Commit all changes" checked
4. Enter a meaningful commit message
5. Click "Commit" to create the commit

**Option 2: Commit Selected Files**

1. Click "✅ Commit" button or press Ctrl+K
2. Uncheck "Commit all changes"
3. Select specific files to commit (use Ctrl/Cmd+Click for multiple files)
4. Enter a meaningful commit message
5. Click "Commit" to create the commit with only the selected files

### Switching Branches

1. Double-click on a branch in the "Branches" panel
2. The GUI will switch to that branch and refresh automatically

### Creating a New Branch

1. Click the "New Branch" button in the "Branches" panel
2. Enter the branch name
3. Click OK to create the branch

### Deleting a Branch

1. Select a branch in the "Branches" panel
2. Click the "Delete" button
3. Confirm the deletion in the dialog
4. Note: You cannot delete the current branch or remote branches

### Pulling from Remote

1. Ensure you have a repository open
2. Click "⬇️ Pull" button or press Ctrl+Shift+P
3. If you have uncommitted changes, you'll be prompted to confirm
4. The GUI will pull updates from the remote repository
5. The view will refresh automatically to show the changes

### Pushing to Remote

1. Ensure you have a repository open with commits to push
2. Click "⬆️ Push" button or press Ctrl+Shift+U
3. The GUI will push your commits to the remote repository
4. A success message will be displayed when complete

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
- [x] Repository cloning with advanced options
- [x] Push/Pull from remote repositories
- [ ] Tag management
- [ ] Settings/Preferences dialog
- [x] Theme system (Light/Dark/System themes)

## Customization

### Themes

CleverGit supports multiple visual themes to suit your preferences:

#### Available Themes

1. **Light Theme** (Default)
   - GitHub-inspired color scheme
   - Bright backgrounds with dark text
   - Green highlights for additions, red for deletions
   - Ideal for well-lit environments

2. **Dark Theme**
   - VS Code-inspired color scheme
   - Dark backgrounds with light text
   - Reduced blue light for comfortable night-time use
   - Muted colors to reduce eye strain

3. **System Theme**
   - Automatically follows your operating system's theme preference
   - Dynamically switches between light and dark based on system settings
   - Seamless integration with your desktop environment

#### Switching Themes

To change the theme:

1. Open the **View** menu in the menu bar
2. Select **Theme** → Choose your preferred theme
3. The theme will be applied immediately
4. Your selection is automatically saved for future sessions

#### Custom Themes

Advanced users can create custom themes by:

1. Adding theme data to the settings file (`~/.config/clevergit/settings.json`)
2. Using the theme manager API to register custom color schemes programmatically

Example custom theme structure:
```json
{
  "custom_themes": {
    "my_theme": {
      "background": "#ffffff",
      "text": "#000000",
      "button_primary": "#0066cc",
      ...
    }
  }
}
```

## Getting Help

For more information:

- Check [README.MD](README.MD) for project overview
- Review [README_zh.md](README_zh.md) for quick start guide
- See [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) for implementation details
