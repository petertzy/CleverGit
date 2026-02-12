# Multi-Tab and Multi-Window Support

CleverGit now supports opening multiple repositories in tabs within a single window, and running multiple windows simultaneously.

## Features

### Tab Management

#### Opening Repositories in Tabs
- **File → Open Repository** (Ctrl+O) - Opens a repository in a new tab
- **File → Clone Repository** (Ctrl+Shift+C) - Clones and opens a repository in a new tab
- **File → Recent Repositories** - Opens a recent repository in a new tab

#### Tab Navigation
- **Ctrl+Tab** - Switch to next tab
- **Ctrl+Shift+Tab** - Switch to previous tab
- **Ctrl+W** - Close current tab
- Click on tab to switch to it
- Drag tabs to reorder them

#### Tab Context Menu
Right-click on a tab to access:
- **Close** - Close the selected tab
- **Close Others** - Close all tabs except the selected one
- **Close All** - Close all open tabs

### Multi-Window Support

#### Creating New Windows
- **File → New Window** (Ctrl+Shift+N) - Opens a new CleverGit window
- Each window can have its own set of tabs
- Windows operate independently

### Session Management

#### Automatic Session Saving
CleverGit automatically saves your session when:
- A tab is opened or closed
- The active tab changes
- A window is closed

The session includes:
- Open tabs in each window
- Active tab in each window
- Window position and size

#### Session Restoration
- **Automatic on startup** - CleverGit restores your previous session when launched
- **File → Restore Session** - Manually restore the last saved session

### Welcome Screen

When no tabs are open, CleverGit displays a welcome screen with quick actions:
- **Open Repository** - Browse for a repository
- **Clone Repository** - Clone a new repository

## Per-Tab State

Each tab maintains its own:
- Repository path
- Current branch
- File selection
- Stash/Tag view visibility
- Commit cache
- View states (log, graph, status)

## Toolbar Behavior

The toolbar buttons (Commit, Pull, Push, etc.) operate on the currently active tab:
- Buttons are enabled/disabled based on current tab state
- Window title shows current repository and branch
- Path label shows current repository path

## Keyboard Shortcuts

### Tab Management
- **Ctrl+T** - New tab (opens repository dialog)
- **Ctrl+W** - Close current tab
- **Ctrl+Tab** - Next tab
- **Ctrl+Shift+Tab** - Previous tab

### Window Management
- **Ctrl+Shift+N** - New window
- **Ctrl+Q** - Close window (and exit if last window)

### Repository Operations (operate on current tab)
- **Ctrl+O** - Open repository
- **Ctrl+Shift+C** - Clone repository
- **F5** - Refresh current tab
- **Ctrl+K** - Commit
- **Ctrl+Shift+P** - Pull
- **Ctrl+Shift+U** - Push
- **Ctrl+D** - View diff
- **Ctrl+B** - Blame file

## Settings Storage

Session data is stored in `~/.config/clevergit/settings.json`:

```json
{
  "session_windows": [
    {
      "window_id": "uuid",
      "tabs": ["/path/to/repo1", "/path/to/repo2"],
      "active_tab": 0
    }
  ],
  "window_geometries": {
    "uuid": {"x": 100, "y": 100, "width": 1200, "height": 800}
  }
}
```

## Tips

1. **Quick Switching** - Use Ctrl+Tab to quickly switch between repositories
2. **Multiple Repos** - Open related repositories in tabs to switch between them easily
3. **Separate Windows** - Use multiple windows when working on unrelated projects
4. **Session Restore** - Your work session persists across restarts automatically
5. **Close Others** - Right-click a tab and select "Close Others" to focus on one repository

## Technical Details

### Architecture
- **RepositoryTab** - Widget encapsulating all repository-specific UI and state
- **MainWindow** - Container managing tabs and global UI
- **Settings** - Persistent storage for session state
- **WelcomeScreen** - Displayed when no tabs are open

### Window Tracking
- All windows are tracked in a global list
- Each window has a unique ID (UUID)
- Last window closing exits the application

### State Management
- Each tab maintains independent state
- Toolbar updates when switching tabs
- Window title reflects current tab
- Session saved on tab/window changes
