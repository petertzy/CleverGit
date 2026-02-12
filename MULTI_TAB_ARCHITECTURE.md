# Multi-Tab/Multi-Window Architecture

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                        │
│                         (main.py)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Creates multiple instances
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MainWindow (Window 1)                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Toolbar (Shared across tabs)                            │  │
│  │  [Clone] [Open] [Refresh] [Commit] [Pull] [Push] ...    │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ QTabWidget (Tab Container)                               │  │
│  │ ┌─────────┬─────────┬─────────┐                         │  │
│  │ │ Tab 1   │ Tab 2   │ Tab 3   │                         │  │
│  │ └────┬────┴────┬────┴────┬────┘                         │  │
│  │      │         │         │                               │  │
│  │      ▼         ▼         ▼                               │  │
│  │ ┌────────┬────────┬────────┐                            │  │
│  │ │RepTab 1│RepTab 2│RepTab 3│ (RepositoryTab widgets)    │  │
│  │ └────┬───┴───┬────┴───┬────┘                            │  │
│  └──────┼───────┼────────┼──────────────────────────────────┘  │
│         │       │        │                                      │
│         │       │        └─> /path/to/repo3 (Per-tab state)   │
│         │       └─────────> /path/to/repo2 (Per-tab state)    │
│         └─────────────────> /path/to/repo1 (Per-tab state)    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       MainWindow (Window 2)                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Toolbar (Independent)                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ QTabWidget                                               │  │
│  │ ┌─────────┬─────────┐                                   │  │
│  │ │ Tab 1   │ Tab 2   │                                   │  │
│  │ └────┬────┴────┬────┘                                   │  │
│  │      ▼         ▼                                         │  │
│  │ ┌────────┬────────┐                                     │  │
│  │ │RepTab 1│RepTab 2│                                     │  │
│  │ └────────┴────────┘                                     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Settings & Persistence                     │
│  - Window geometries (position, size)                           │
│  - Session state (all windows, tabs, active tab)                │
│  - Repository branches                                           │
│  - Recent repositories                                           │
└─────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
MainWindow (Multiple instances possible)
├── Toolbar (shared, operates on current tab)
│   ├── Clone Button
│   ├── Open Button
│   ├── Refresh Button
│   ├── Commit Button
│   ├── Pull/Push Buttons
│   ├── Diff/Stash/Tag/Blame Buttons
│   └── Path Label
│
├── QTabWidget (manages repository tabs)
│   ├── Tab 1: RepositoryTab
│   │   ├── Left Panel
│   │   │   ├── RepositoryView (repo info)
│   │   │   ├── BranchView (branches list)
│   │   │   ├── StashView (stashes list)
│   │   │   └── TagView (tags list)
│   │   ├── Right Panel
│   │   │   ├── StatusView (file status)
│   │   │   └── QTabWidget (history views)
│   │   │       ├── LogView (commit list)
│   │   │       └── GraphView (commit graph)
│   │   └── State
│   │       ├── repo: Repo instance
│   │       ├── repo_path: Path
│   │       ├── _commit_cache: List[CommitInfo]
│   │       └── _selected_file: str
│   │
│   ├── Tab 2: RepositoryTab
│   │   └── (same structure)
│   │
│   └── Tab N: RepositoryTab
│       └── (same structure)
│
├── WelcomeScreen (shown when no tabs)
│   ├── Open Repository Button
│   └── Clone Repository Button
│
└── Menu Bar
    ├── File Menu
    │   ├── New Tab (Ctrl+T)
    │   ├── New Window (Ctrl+Shift+N)
    │   ├── Clone Repository (Ctrl+Shift+C)
    │   ├── Open Repository (Ctrl+O)
    │   ├── Close Tab (Ctrl+W)
    │   ├── Recent Repositories
    │   ├── Restore Session
    │   └── Exit (Ctrl+Q)
    ├── Edit Menu
    ├── Commit Menu
    ├── Remote Menu
    ├── View Menu
    └── Help Menu
```

## State Management

### Per-Tab State (RepositoryTab)
Each tab maintains:
- `repo`: Repo instance for git operations
- `repo_path`: Path to repository
- `_commit_cache`: Cached commit data
- `_selected_file`: Currently selected file
- View states: Stash/Tag visibility

### Per-Window State (MainWindow)
Each window maintains:
- `window_id`: Unique window identifier (UUID)
- `tab_widget`: QTabWidget containing repository tabs
- `_diff_dialogs`: List of open diff viewers
- `_blame_windows`: List of open blame windows
- Toolbar button states

### Global State
- `_windows`: List of all open MainWindow instances
- Settings persistence via Settings class

## Data Flow

### Opening a Repository
```
User Action
    │
    ▼
MainWindow._open_repository()
    │
    ├─> Show QFileDialog
    │
    ├─> Create RepositoryTab(repo_path)
    │   │
    │   ├─> RepositoryTab._load_repository()
    │   │   └─> Repo.open(repo_path)
    │   │
    │   └─> RepositoryTab.refresh()
    │
    ├─> tab_widget.addTab(repository_tab)
    │
    ├─> settings.add_recent_repository(path)
    │
    └─> _save_session()
```

### Switching Tabs
```
User clicks tab or uses Ctrl+Tab
    │
    ▼
tab_widget.currentChanged signal
    │
    ▼
MainWindow._on_tab_changed(index)
    │
    ├─> Get current RepositoryTab
    │
    ├─> Update toolbar button states
    │
    ├─> Update window title
    │
    ├─> Update path label
    │
    └─> _save_session()
```

### Closing a Tab
```
User clicks X or Ctrl+W
    │
    ▼
MainWindow._close_tab(index)
    │
    ├─> Get RepositoryTab at index
    │
    ├─> Save current branch to settings
    │
    ├─> tab_widget.removeTab(index)
    │
    ├─> If no tabs left, show welcome screen
    │
    └─> _save_session()
```

### Session Management
```
Application startup
    │
    ▼
MainWindow.__init__()
    │
    └─> _restore_session()
        │
        ├─> settings.get_session_windows()
        │
        ├─> For each saved window:
        │   ├─> Create MainWindow instance
        │   ├─> Restore window geometry
        │   ├─> For each saved tab:
        │   │   └─> _add_repository_tab(repo_path)
        │   └─> Set active tab
        │
        └─> Fallback to last_repository if no session

Application operation
    │
    ├─> Tab opened/closed
    ├─> Tab switched
    └─> Window closed
        │
        ▼
    _save_session()
        │
        └─> settings.set_session_windows([
                {
                    'id': window_id,
                    'tabs': [repo_paths],
                    'active_tab': index
                },
                ...
            ])
```

## Key Design Decisions

### 1. RepositoryTab as Self-Contained Widget
- **Why**: Encapsulates all repository-specific UI and state
- **Benefit**: Clean separation of concerns, easier to manage multiple repositories
- **Trade-off**: More code duplication compared to shared views

### 2. Global Window Tracking List
- **Why**: Simple way to track all open windows
- **Benefit**: Easy to implement multi-window support
- **Trade-off**: Global state, but necessary for multi-window management

### 3. UUID-based Window IDs
- **Why**: Uniquely identify windows for session persistence
- **Benefit**: Robust session management across app restarts
- **Trade-off**: Slight complexity in session state structure

### 4. Automatic Session Saving
- **Why**: Ensure no data loss if app crashes or is force-closed
- **Benefit**: Better user experience, no manual "save session" needed
- **Trade-off**: More I/O operations, but settings file is small

### 5. Welcome Screen When No Tabs
- **Why**: Avoid empty UI, provide clear call-to-action
- **Benefit**: Better onboarding, clearer UX
- **Trade-off**: Extra widget to maintain

## Performance Considerations

- **Tab Switching**: O(1) operation, instant UI updates
- **Session Save**: Async file I/O, minimal impact
- **Session Restore**: Sequential tab loading on startup
- **Memory**: Each tab holds its own Repo instance, acceptable for typical usage (5-10 tabs)

## Extension Points

Future enhancements can easily add:
- Tab drag-and-drop between windows
- Tab duplication
- Split view within tabs
- Custom tab icons/colors
- Tab groups/organization
- Workspace profiles
