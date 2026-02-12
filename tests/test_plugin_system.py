"""
Test suite for plugin system.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from clevergit.plugins.interface import Plugin, PluginMetadata, PluginState
from clevergit.plugins.loader import PluginLoader
from clevergit.plugins.config import PluginConfig
from clevergit.plugins.manager import PluginManager


# Sample test plugin
class SamplePlugin(Plugin):
    """A test plugin for unit testing."""
    
    def __init__(self):
        super().__init__()
        self.load_called = False
        self.enable_called = False
        self.disable_called = False
        self.unload_called = False
    
    def get_metadata(self):
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin",
            dependencies=[]
        )
    
    def on_load(self):
        self.load_called = True
    
    def on_enable(self):
        self.enable_called = True
    
    def on_disable(self):
        self.disable_called = True
    
    def on_unload(self):
        self.unload_called = True


class TestPluginInterface:
    """Test plugin interface and base class."""
    
    def test_plugin_metadata_creation(self):
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            author="Author",
            description="Description"
        )
        assert metadata.name == "test"
        assert metadata.version == "1.0.0"
        assert metadata.dependencies == []
    
    def test_plugin_state_initialization(self):
        """Test plugin initial state."""
        plugin = SamplePlugin()
        assert plugin.get_state() == PluginState.UNLOADED
    
    def test_plugin_lifecycle_methods(self):
        """Test plugin lifecycle methods are called."""
        plugin = SamplePlugin()
        
        plugin.on_load()
        assert plugin.load_called
        
        plugin.on_enable()
        assert plugin.enable_called
        
        plugin.on_disable()
        assert plugin.disable_called
        
        plugin.on_unload()
        assert plugin.unload_called
    
    def test_plugin_configuration(self):
        """Test plugin configuration."""
        plugin = SamplePlugin()
        config = {"key": "value"}
        plugin.configure(config)
        assert plugin.get_config() == config


class TestPluginConfig:
    """Test plugin configuration management."""
    
    def test_config_initialization(self, tmp_path):
        """Test config file initialization."""
        config_file = tmp_path / "plugins.json"
        config = PluginConfig(config_file)
        assert config_file.exists()
    
    def test_set_and_get_plugin_config(self, tmp_path):
        """Test setting and getting plugin configuration."""
        config_file = tmp_path / "plugins.json"
        config = PluginConfig(config_file)
        
        plugin_config = {"setting1": "value1", "setting2": 42}
        config.set_plugin_config("test_plugin", plugin_config)
        
        retrieved = config.get_plugin_config("test_plugin")
        assert retrieved == plugin_config
    
    def test_remove_plugin_config(self, tmp_path):
        """Test removing plugin configuration."""
        config_file = tmp_path / "plugins.json"
        config = PluginConfig(config_file)
        
        config.set_plugin_config("test_plugin", {"key": "value"})
        config.remove_plugin_config("test_plugin")
        
        retrieved = config.get_plugin_config("test_plugin")
        assert retrieved == {}
    
    def test_get_all_configs(self, tmp_path):
        """Test getting all configurations."""
        config_file = tmp_path / "plugins.json"
        config = PluginConfig(config_file)
        
        config.set_plugin_config("plugin1", {"a": 1})
        config.set_plugin_config("plugin2", {"b": 2})
        
        all_configs = config.get_all_configs()
        assert len(all_configs) == 2
        assert "plugin1" in all_configs
        assert "plugin2" in all_configs


class TestPluginLoader:
    """Test plugin loading mechanism."""
    
    def test_add_plugin_path(self, tmp_path):
        """Test adding plugin search path."""
        loader = PluginLoader()
        loader.add_plugin_path(tmp_path)
        assert tmp_path in loader._plugin_paths
    
    def test_discover_plugins(self, tmp_path):
        """Test plugin discovery."""
        loader = PluginLoader()
        loader.add_plugin_path(tmp_path)
        
        # Create a dummy plugin file
        plugin_file = tmp_path / "dummy_plugin.py"
        plugin_file.write_text("# Dummy plugin")
        
        discovered = loader.discover_plugins()
        assert "dummy_plugin" in discovered
    
    def test_load_plugin(self, tmp_path):
        """Test loading a plugin."""
        loader = PluginLoader()
        loader.add_plugin_path(tmp_path)
        
        # Create a valid plugin file
        plugin_code = '''
from clevergit.plugins.interface import Plugin, PluginMetadata

class DummyPlugin(Plugin):
    def get_metadata(self):
        return PluginMetadata("dummy", "1.0.0", "Author", "Description")
    
    def on_load(self):
        pass
    
    def on_enable(self):
        pass
    
    def on_disable(self):
        pass
    
    def on_unload(self):
        pass
'''
        plugin_file = tmp_path / "dummy_plugin.py"
        plugin_file.write_text(plugin_code)
        
        plugin_class = loader.load_plugin("dummy_plugin")
        assert plugin_class is not None
        assert issubclass(plugin_class, Plugin)


class TestPluginManager:
    """Test plugin manager."""
    
    def test_manager_initialization(self, tmp_path):
        """Test plugin manager initialization."""
        config_file = tmp_path / "plugins.json"
        manager = PluginManager(config_file)
        assert manager is not None
    
    def test_discover_plugins_from_builtin(self, tmp_path):
        """Test discovering built-in plugins."""
        manager = PluginManager(tmp_path / "plugins.json")
        plugins = manager.discover_plugins()
        assert isinstance(plugins, list)
    
    def test_plugin_lifecycle(self, tmp_path):
        """Test complete plugin lifecycle."""
        # Create a test plugin file
        plugin_dir = tmp_path / "test_plugins"
        plugin_dir.mkdir()
        
        plugin_code = '''
from clevergit.plugins.interface import Plugin, PluginMetadata

class LifecycleTestPlugin(Plugin):
    def get_metadata(self):
        return PluginMetadata("lifecycle_test", "1.0.0", "Author", "Test")
    
    def on_load(self):
        pass
    
    def on_enable(self):
        pass
    
    def on_disable(self):
        pass
    
    def on_unload(self):
        pass
'''
        (plugin_dir / "lifecycle_test.py").write_text(plugin_code)
        
        # Initialize manager
        config_file = tmp_path / "plugins.json"
        manager = PluginManager(config_file)
        manager.add_plugin_path(plugin_dir)
        
        # Test lifecycle
        assert manager.load_plugin("lifecycle_test")
        assert manager.get_plugin_state("lifecycle_test") == PluginState.LOADED
        
        assert manager.enable_plugin("lifecycle_test")
        assert manager.get_plugin_state("lifecycle_test") == PluginState.ENABLED
        
        assert manager.disable_plugin("lifecycle_test")
        assert manager.get_plugin_state("lifecycle_test") == PluginState.DISABLED
        
        assert manager.unload_plugin("lifecycle_test")
        assert manager.get_plugin_state("lifecycle_test") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
