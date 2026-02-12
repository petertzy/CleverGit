# CleverGit Plugin Development Guide

## Overview

CleverGit provides an extensible plugin architecture that allows developers to extend its functionality with custom features. This guide will help you create, test, and deploy plugins for CleverGit.

## Plugin Architecture

### Plugin Lifecycle

Plugins in CleverGit follow a well-defined lifecycle:

1. **Unloaded** - Plugin is discovered but not loaded
2. **Loaded** - Plugin is instantiated and initialized
3. **Enabled** - Plugin is active and performing operations
4. **Disabled** - Plugin is loaded but not active
5. **Error** - Plugin encountered an error during lifecycle transition

### Plugin States

```
UNLOADED → LOADED → ENABLED
                 ↓       ↓
            DISABLED ← ←
                 ↓
            UNLOADED
```

## Creating a Plugin

### Basic Plugin Structure

Every plugin must inherit from the `Plugin` base class and implement the required methods:

```python
from clevergit.plugins.interface import Plugin, PluginMetadata
from typing import Dict, Any


class MyPlugin(Plugin):
    """My custom CleverGit plugin."""
    
    def __init__(self) -> None:
        """Initialize your plugin."""
        super().__init__()
        # Initialize your plugin-specific variables here
        self.my_data = {}
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            author="Your Name",
            description="Description of what your plugin does",
            dependencies=[]  # List of required plugin names
        )
    
    def on_load(self) -> None:
        """Called when the plugin is loaded."""
        # Initialize resources, connect to services, etc.
        print("MyPlugin loaded")
    
    def on_enable(self) -> None:
        """Called when the plugin is enabled."""
        # Start operations, register event handlers, etc.
        print("MyPlugin enabled")
    
    def on_disable(self) -> None:
        """Called when the plugin is disabled."""
        # Stop operations, unregister handlers, etc.
        print("MyPlugin disabled")
    
    def on_unload(self) -> None:
        """Called when the plugin is unloaded."""
        # Clean up resources, close connections, etc.
        print("MyPlugin unloaded")
```

### Plugin Metadata

The `PluginMetadata` class contains information about your plugin:

- **name**: Unique identifier for your plugin (use lowercase with underscores)
- **version**: Semantic version (e.g., "1.0.0")
- **author**: Your name or organization
- **description**: Brief description of what the plugin does
- **dependencies**: List of other plugin names that must be loaded first

## Plugin Configuration

### Using Configuration

Plugins can be configured using a dictionary of settings:

```python
def on_load(self) -> None:
    """Called when the plugin is loaded."""
    config = self.get_config()
    self.my_setting = config.get("my_setting", "default_value")
    self.enabled_feature = config.get("enabled_feature", True)
```

### Configuration Persistence

Plugin configurations are automatically persisted to `~/.clevergit/plugins.json`. You can modify them programmatically:

```python
from clevergit.plugins.manager import PluginManager

manager = PluginManager()
manager.configure_plugin("my_plugin", {
    "my_setting": "custom_value",
    "enabled_feature": False
})
```

## Installing Plugins

### User Plugin Directory

Place your plugin file in the user plugins directory:

```
~/.clevergit/plugins/my_plugin.py
```

### Custom Plugin Paths

You can also add custom plugin search paths:

```python
from pathlib import Path
from clevergit.plugins.manager import PluginManager

manager = PluginManager()
manager.add_plugin_path(Path("/custom/plugin/directory"))
```

## Using the Plugin System

### Basic Usage

```python
from clevergit.plugins.manager import PluginManager

# Initialize the plugin manager
manager = PluginManager()

# Discover available plugins
available_plugins = manager.discover_plugins()
print(f"Available plugins: {available_plugins}")

# Load and enable a plugin
manager.load_plugin("my_plugin")
manager.enable_plugin("my_plugin")

# Get plugin instance to call custom methods
plugin = manager.get_plugin("my_plugin")
if plugin:
    # Call plugin-specific methods
    result = plugin.some_custom_method()

# Disable and unload when done
manager.disable_plugin("my_plugin")
manager.unload_plugin("my_plugin")
```

### Managing Multiple Plugins

```python
# Load multiple plugins
for plugin_name in ["plugin1", "plugin2", "plugin3"]:
    if manager.load_plugin(plugin_name):
        manager.enable_plugin(plugin_name)

# List all loaded plugins
loaded_plugins = manager.list_plugins()
for metadata in loaded_plugins:
    print(f"{metadata.name} v{metadata.version} - {metadata.description}")

# Check plugin state
state = manager.get_plugin_state("my_plugin")
print(f"Plugin state: {state}")
```

## Example Plugin: Commit Statistics

Here's a complete example plugin that tracks commit statistics:

```python
from clevergit.plugins.interface import Plugin, PluginMetadata
from typing import Dict, Any


class CommitStatsPlugin(Plugin):
    """Tracks commit statistics in the repository."""
    
    def __init__(self) -> None:
        super().__init__()
        self._commit_count = 0
        self._active = False
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="commit_stats",
            version="1.0.0",
            author="CleverGit Team",
            description="Tracks and displays commit statistics",
            dependencies=[]
        )
    
    def on_load(self) -> None:
        print("[CommitStats] Plugin loaded")
        self._commit_count = 0
    
    def on_enable(self) -> None:
        print("[CommitStats] Plugin enabled - tracking commits")
        self._active = True
    
    def on_disable(self) -> None:
        print("[CommitStats] Plugin disabled - stopped tracking")
        self._active = False
    
    def on_unload(self) -> None:
        print(f"[CommitStats] Plugin unloaded - Total: {self._commit_count}")
    
    # Custom plugin methods
    def track_commit(self) -> None:
        """Track a new commit."""
        if self._active:
            self._commit_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        return {
            "total_commits": self._commit_count,
            "active": self._active
        }
```

## Best Practices

### Error Handling

Always handle errors gracefully in your plugin methods:

```python
def on_enable(self) -> None:
    try:
        # Your initialization code
        self.initialize_resources()
    except Exception as e:
        print(f"Error enabling plugin: {e}")
        raise  # Re-raise to let the manager handle it
```

### Resource Cleanup

Always clean up resources in `on_unload()`:

```python
def on_unload(self) -> None:
    if self.connection:
        self.connection.close()
    if self.temp_files:
        for file in self.temp_files:
            file.unlink()
```

### State Management

Use the plugin state to control behavior:

```python
def some_operation(self) -> None:
    if self.get_state() != PluginState.ENABLED:
        print("Plugin is not enabled")
        return
    # Perform operation
```

### Thread Safety

If your plugin uses threads, ensure proper synchronization:

```python
import threading

class MyThreadedPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self._data = {}
    
    def update_data(self, key, value):
        with self._lock:
            self._data[key] = value
```

## Testing Plugins

### Unit Testing

Create tests for your plugin using pytest:

```python
import pytest
from my_plugin import MyPlugin
from clevergit.plugins.interface import PluginState


def test_plugin_lifecycle():
    plugin = MyPlugin()
    
    # Test initial state
    assert plugin.get_state() == PluginState.UNLOADED
    
    # Test lifecycle
    plugin.on_load()
    plugin._set_state(PluginState.LOADED)
    assert plugin.get_state() == PluginState.LOADED
    
    plugin.on_enable()
    plugin._set_state(PluginState.ENABLED)
    assert plugin.get_state() == PluginState.ENABLED
    
    plugin.on_disable()
    plugin._set_state(PluginState.DISABLED)
    
    plugin.on_unload()
```

### Integration Testing

Test your plugin with the plugin manager:

```python
def test_plugin_with_manager(tmp_path):
    from clevergit.plugins.manager import PluginManager
    
    # Create manager with temporary config
    manager = PluginManager(tmp_path / "plugins.json")
    
    # Test loading
    assert manager.load_plugin("my_plugin")
    assert manager.enable_plugin("my_plugin")
    
    # Test functionality
    plugin = manager.get_plugin("my_plugin")
    result = plugin.some_method()
    assert result is not None
```

## Advanced Topics

### Plugin Dependencies

If your plugin depends on other plugins:

```python
def get_metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="advanced_plugin",
        version="1.0.0",
        author="Your Name",
        description="Advanced plugin with dependencies",
        dependencies=["base_plugin", "utils_plugin"]
    )
```

### Accessing Repository

To access the Git repository from your plugin:

```python
from clevergit.core.repo import Repo

class RepoAwarePlugin(Plugin):
    def __init__(self, repo_path: str = ".") -> None:
        super().__init__()
        self.repo = Repo.open(repo_path)
    
    def on_enable(self) -> None:
        # Use repository operations
        status = self.repo.status()
        branches = self.repo.list_branches()
```

### Event Hooks

While not built into the base system, you can implement event hooks:

```python
from typing import Callable, List

class EventPlugin(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self._on_commit_hooks: List[Callable] = []
    
    def register_commit_hook(self, callback: Callable) -> None:
        """Register a callback for commit events."""
        self._on_commit_hooks.append(callback)
    
    def trigger_commit_event(self, commit_info) -> None:
        """Trigger all registered commit hooks."""
        for hook in self._on_commit_hooks:
            try:
                hook(commit_info)
            except Exception as e:
                print(f"Error in commit hook: {e}")
```

## Troubleshooting

### Plugin Not Loading

- Check that the plugin file is in a valid plugin directory
- Ensure the plugin class inherits from `Plugin`
- Verify there are no syntax errors in the plugin file
- Check console output for error messages

### Configuration Not Persisting

- Ensure `~/.clevergit/` directory exists and is writable
- Check file permissions on `plugins.json`
- Verify you're using `manager.configure_plugin()` to save settings

### Plugin State Issues

- Always use lifecycle methods (`on_load`, `on_enable`, etc.)
- Don't modify `_state` directly (use `_set_state()`)
- Handle exceptions in lifecycle methods

## API Reference

### Plugin Class

```python
class Plugin(ABC):
    def get_metadata(self) -> PluginMetadata
    def on_load(self) -> None
    def on_enable(self) -> None
    def on_disable(self) -> None
    def on_unload(self) -> None
    def configure(self, config: Dict[str, Any]) -> None
    def get_config(self) -> Dict[str, Any]
    def get_state(self) -> PluginState
```

### PluginManager Class

```python
class PluginManager:
    def __init__(self, config_path: Optional[Path] = None)
    def add_plugin_path(self, path: Path) -> None
    def discover_plugins(self) -> List[str]
    def load_plugin(self, plugin_name: str) -> bool
    def enable_plugin(self, plugin_name: str) -> bool
    def disable_plugin(self, plugin_name: str) -> bool
    def unload_plugin(self, plugin_name: str) -> bool
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]
    def list_plugins(self) -> List[PluginMetadata]
    def get_plugin_state(self, plugin_name: str) -> Optional[PluginState]
    def configure_plugin(self, plugin_name: str, config: Dict) -> bool
```

## Contributing Plugins

To contribute your plugin to CleverGit:

1. Ensure your plugin follows this guide
2. Add comprehensive tests
3. Document your plugin's functionality
4. Submit a pull request with your plugin in `clevergit/plugins/builtin/`

## Support

For questions or issues with plugin development:

- Check the [GitHub Issues](https://github.com/petertzy/CleverGit/issues)
- Review existing plugin examples in `clevergit/plugins/builtin/`
- Consult the main CleverGit documentation

## License

Plugins you create are your own intellectual property, but to be included in CleverGit's built-in plugins, they must be compatible with CleverGit's license.
