# Keyboard Shortcuts System

CleverGit includes a comprehensive keyboard shortcuts system that allows users to navigate and control the application efficiently using keyboard combinations.

## Features

- **Predefined Shortcuts**: Default keyboard shortcuts for all major actions
- **Customizable**: Users can remap shortcuts to their preferences
- **Help Dialog**: Built-in dialog to view and customize shortcuts
- **Persistence**: Custom shortcuts are saved and restored across sessions
- **Conflict Detection**: Prevents assigning the same shortcut to multiple actions

## Default Keyboard Shortcuts

### File Operations
- `Ctrl+T` - Open repository in new tab
- `Ctrl+Shift+N` - Open new window
- `Ctrl+Shift+C` - Clone repository
- `Ctrl+O` - Open repository
- `Ctrl+W` - Close current tab
- `Ctrl+Q` - Exit application

### Edit Operations
- `F5` - Refresh current view
- `Ctrl+D` - View diff
- `Ctrl+B` - Show blame for file

### Commit Operations
- `Ctrl+K` - Create new commit

### Remote Operations
- `Ctrl+Shift+P` - Pull from remote
- `Ctrl+Shift+U` - Push to remote

### Navigation
- `Ctrl+Tab` - Switch to next tab
- `Ctrl+Shift+Tab` - Switch to previous tab

### Search
- `Ctrl+P` - Open command palette

### Help
- `F1` - Show keyboard shortcuts help

## Using the Shortcuts System

### Viewing Available Shortcuts

1. Open the Help menu
2. Select "Keyboard Shortcuts" (or press `F1`)
3. The dialog will display all available shortcuts organized by category

### Customizing Shortcuts

1. Open the keyboard shortcuts dialog (`F1`)
2. Switch to the "Customize" tab
3. Click "Edit" next to the shortcut you want to change
4. Enter the new key combination
5. Click "Save"

The system will prevent you from setting conflicting shortcuts.

### Resetting Shortcuts

To reset a single shortcut to its default value:
1. Open the "Customize" tab in the shortcuts dialog
2. Click "Reset" next to the shortcut

To reset all shortcuts to defaults:
1. Open the "Customize" tab in the shortcuts dialog
2. Click "Reset All to Defaults" at the bottom

## For Developers

### Using ShortcutManager

The `ShortcutManager` class manages all keyboard shortcuts in the application:

```python
from clevergit.ui.shortcuts import ShortcutManager
from clevergit.ui.settings import Settings

# Initialize
settings = Settings()
shortcut_manager = ShortcutManager(settings)

# Get a shortcut
shortcut = shortcut_manager.get_shortcut("file.open")  # Returns "Ctrl+O"

# Set a shortcut
success = shortcut_manager.set_shortcut("file.open", "Ctrl+Shift+O")

# Register a shortcut with a callback
shortcut_manager.register_shortcut("file.open", parent_widget, callback_function)

# Register a shortcut with a QAction
shortcut_manager.register_action("file.open", action)
```

### Adding New Shortcuts

To add a new shortcut to the application:

1. Add the shortcut to `DEFAULT_SHORTCUTS` in `clevergit/ui/shortcuts.py`:
```python
DEFAULT_SHORTCUTS: Dict[str, str] = {
    # ... existing shortcuts ...
    "mynew.action": "Ctrl+Shift+A",
}
```

2. Add a description to `SHORTCUT_DESCRIPTIONS`:
```python
SHORTCUT_DESCRIPTIONS: Dict[str, str] = {
    # ... existing descriptions ...
    "mynew.action": "My new action description",
}
```

3. Add a category to `SHORTCUT_CATEGORIES`:
```python
SHORTCUT_CATEGORIES: Dict[str, str] = {
    # ... existing categories ...
    "mynew.action": "MyCategory",
}
```

4. Register the shortcut in your UI code:
```python
# For QAction
self.shortcut_manager.register_action("mynew.action", my_action)

# Or for direct callback
self.shortcut_manager.register_shortcut("mynew.action", self, self._my_callback)
```

### Shortcut Action IDs

Action IDs follow the pattern `category.action`:
- `file.*` - File operations
- `edit.*` - Edit operations
- `commit.*` - Commit operations
- `remote.*` - Remote operations
- `tab.*` - Tab navigation
- `help.*` - Help actions

## Configuration Storage

Custom shortcuts are stored in the user's configuration file at:
- Linux/macOS: `~/.config/clevergit/settings.json`
- Windows: `%USERPROFILE%\.config\clevergit\settings.json`

The shortcuts are saved in the `shortcuts` key of the settings file:
```json
{
  "shortcuts": {
    "file.open": "Ctrl+O",
    "file.new_tab": "Ctrl+T",
    ...
  }
}
```

## Implementation Details

### ShortcutManager Class

The `ShortcutManager` class provides the following functionality:

- **Loading**: Loads shortcuts from settings or uses defaults
- **Validation**: Validates keyboard sequences and prevents conflicts
- **Registration**: Registers shortcuts with Qt widgets and actions
- **Persistence**: Saves custom shortcuts to settings
- **Dynamic Updates**: Updates registered shortcuts when they are changed

### Shortcut Help Dialog

The `ShortcutHelpDialog` class provides a user-friendly interface for:
- Viewing all available shortcuts in a table
- Customizing shortcuts with validation
- Resetting individual or all shortcuts

The dialog has two tabs:
1. **View Shortcuts**: Read-only display of all shortcuts
2. **Customize**: Interactive table with edit and reset buttons

## Best Practices

1. **Use Descriptive Action IDs**: Choose clear, hierarchical action IDs
2. **Avoid Conflicts**: The system prevents conflicts, but choose unique combinations
3. **Follow Conventions**: Use standard shortcuts when possible (Ctrl+C for copy, etc.)
4. **Test Shortcuts**: Ensure shortcuts work across different platforms
5. **Document New Shortcuts**: Update documentation when adding new shortcuts

## Platform Considerations

- On macOS, `Ctrl` is typically replaced with `Cmd` automatically by Qt
- Some shortcuts may conflict with system shortcuts on different platforms
- F-keys may have special functions on laptops (brightness, volume, etc.)

## Troubleshooting

### Shortcut Not Working
1. Check if the shortcut is shown in the Help dialog
2. Verify there are no conflicts with other actions
3. Ensure the action is enabled in the current context

### Shortcut Conflicts
If you experience conflicts:
1. Open the shortcuts dialog
2. Reset the conflicting shortcut to default
3. Choose a different key combination

### Lost Customizations
If custom shortcuts are not persisting:
1. Check file permissions on the config directory
2. Verify the settings file is writable
3. Check for errors in the application log
