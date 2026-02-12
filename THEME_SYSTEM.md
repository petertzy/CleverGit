# Theme System Documentation

## Overview

The CleverGit theme system provides a centralized, extensible way to manage the application's visual appearance. It supports built-in themes (Light and Dark), system theme detection, and custom theme creation.

## Architecture

### Core Components

1. **Theme** (`clevergit/ui/themes/base.py`)
   - Base dataclass defining all color properties
   - Provides `to_dict()` for serialization
   - Generates QSS stylesheets via `get_stylesheet()`

2. **ThemeManager** (`clevergit/ui/themes/manager.py`)
   - Singleton pattern for global access
   - Manages theme registration and switching
   - Handles system theme detection
   - Applies themes to the QApplication

3. **LightTheme** (`clevergit/ui/themes/light.py`)
   - GitHub-inspired color palette
   - Bright backgrounds with high contrast

4. **DarkTheme** (`clevergit/ui/themes/dark.py`)
   - VS Code-inspired color palette
   - Dark backgrounds optimized for low-light environments

### Integration Points

- **Settings** (`clevergit/ui/settings.py`): Persists theme selection
- **Main** (`clevergit/ui/main.py`): Initializes and applies themes on startup
- **MainWindow** (`clevergit/ui/windows/main_window.py`): Provides theme switching UI
- **Widgets**: Use theme colors for syntax highlighting and visual elements

## Usage

### Basic Usage

```python
from clevergit.ui.themes import get_theme_manager

# Get the singleton instance
theme_manager = get_theme_manager()

# List available themes
themes = theme_manager.get_available_themes()
# Returns: ['light', 'dark']

# Switch to a theme
theme_manager.set_theme('dark')

# Get current theme
current = theme_manager.get_current_theme()
if current:
    print(f"Current theme: {current.name}")
    print(f"Background color: {current.background}")
    print(f"Text color: {current.text}")
```

### Custom Themes

#### Programmatic Registration

```python
from clevergit.ui.themes import get_theme_manager

theme_manager = get_theme_manager()

custom_data = {
    "background": "#1a1a2e",
    "background_secondary": "#16213e",
    "text": "#eaeaea",
    "button_primary": "#0f3460",
    # ... other color properties
}

theme_manager.register_custom_theme("midnight", custom_data)
theme_manager.set_theme("midnight")
```

#### Settings File Configuration

Add to `~/.config/clevergit/settings.json`:

```json
{
  "theme": "my_custom",
  "custom_themes": {
    "my_custom": {
      "background": "#ffffff",
      "background_secondary": "#f0f0f0",
      "text": "#333333",
      "button_primary": "#007acc",
      "button_success": "#28a745",
      "diff_added": "#e6ffed",
      "diff_removed": "#ffeef0",
      "graph_colors": [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
        "#9b59b6", "#1abc9c", "#e67e22", "#95a5a6"
      ]
    }
  }
}
```

### Widget Integration

Widgets can access the current theme to apply appropriate colors:

```python
from clevergit.ui.themes import get_theme_manager
from PySide6.QtGui import QColor

theme_manager = get_theme_manager()
theme = theme_manager.get_current_theme()

if theme:
    # Use theme colors for highlighting
    added_color = QColor(theme.diff_added)
    removed_color = QColor(theme.diff_removed)
    
    # Use theme colors for UI elements
    background_color = QColor(theme.background)
    text_color = QColor(theme.text)
```

## Theme Properties

### Color Properties

| Property | Purpose | Example (Light) | Example (Dark) |
|----------|---------|-----------------|----------------|
| `background` | Main background | `#ffffff` | `#1e1e1e` |
| `background_secondary` | Secondary areas | `#f6f8fa` | `#252526` |
| `background_hover` | Hover states | `#e1e4e8` | `#2a2d2e` |
| `text` | Primary text | `#24292e` | `#d4d4d4` |
| `text_secondary` | Secondary text | `#586069` | `#a0a0a0` |
| `text_disabled` | Disabled text | `#959da5` | `#6e6e6e` |
| `button_primary` | Primary buttons | `#0366d6` | `#0e639c` |
| `button_success` | Success buttons | `#28a745` | `#107c10` |
| `button_warning` | Warning buttons | `#ff9800` | `#ca5010` |
| `button_danger` | Danger buttons | `#d73a49` | `#c42b1c` |
| `diff_added` | Added lines | `#e6ffed` | `#1a3d2e` |
| `diff_removed` | Removed lines | `#ffeef0` | `#4b1818` |
| `diff_modified` | Modified lines | `#fff8c5` | `#3d3721` |
| `graph_colors` | Branch colors | 8 colors | 8 colors |
| `selection_background` | Selected items | `#0366d6` | `#094771` |

### System Theme Detection

The theme manager can detect the system's color scheme:

```python
theme_manager = get_theme_manager()

# Detect and apply system theme
detected_theme = theme_manager.detect_system_theme()
print(f"System prefers: {detected_theme}")

# Apply system theme
theme_manager.apply_system_theme()
```

Detection algorithm:
1. Get system palette via Qt's `QApplication.palette()`
2. Calculate luminance of window background color
3. Return "dark" if luminance < 128, else "light"

## Testing

The theme system includes comprehensive unit tests in `tests/test_themes.py`:

- Theme initialization and properties
- Theme manager registration and switching
- Custom theme creation
- Settings persistence
- System theme detection

Run tests:
```bash
pytest tests/test_themes.py -v
```

## Future Enhancements

Possible future improvements:

1. **Theme Preview**: Visual preview before applying
2. **Theme Editor**: GUI for creating custom themes
3. **More Built-in Themes**: High contrast, colorblind-friendly, etc.
4. **Per-Widget Customization**: Fine-grained control over widget styling
5. **Import/Export**: Share themes with other users
6. **Live Theme Switching**: Update all windows without restart

## Implementation Notes

### Design Decisions

1. **Singleton Pattern**: Ensures consistent theme across the application
2. **Dataclass**: Simple, clear definition of theme properties
3. **Lazy Qt Imports**: Allows testing without Qt runtime
4. **Fallback Colors**: Graceful degradation if theme is None
5. **QSS Generation**: Centralized stylesheet creation from theme data

### Limitations

1. Some widgets may require restart for full theme application
2. Third-party widgets may not respect theme colors
3. System theme detection requires Qt runtime
4. Custom themes require manual color specification

### Migration from Hardcoded Colors

The implementation replaced hardcoded colors in:
- `diff_viewer.py`: Syntax highlighting colors
- `merge_tool.py`: Conflict section colors
- `graph_view.py`: Branch visualization colors
- `reset_dialog.py`: Removed color from inline styles

Fallback colors are preserved for compatibility when theme is not available.
