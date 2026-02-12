#!/usr/bin/env python3
"""
Example script demonstrating the CleverGit plugin system.

This script shows how to use the plugin manager to load, enable, and interact
with plugins.
"""

from pathlib import Path
from clevergit.plugins import PluginManager


def main():
    """Demonstrate plugin system usage."""
    print("=" * 60)
    print("CleverGit Plugin System Example")
    print("=" * 60)
    print()
    
    # Initialize the plugin manager
    print("Initializing plugin manager...")
    manager = PluginManager()
    print("✓ Plugin manager initialized")
    print()
    
    # Discover available plugins
    print("Discovering plugins...")
    available_plugins = manager.discover_plugins()
    print(f"✓ Found {len(available_plugins)} plugin(s): {', '.join(available_plugins)}")
    print()
    
    # Try to load the example plugin
    if "example_plugin" in available_plugins:
        print("Loading 'example_plugin'...")
        if manager.load_plugin("example_plugin"):
            print("✓ Plugin loaded successfully")
            print()
            
            # Enable the plugin
            print("Enabling plugin...")
            if manager.enable_plugin("example_plugin"):
                print("✓ Plugin enabled")
                print()
                
                # Get the plugin instance and use it
                plugin = manager.get_plugin("example_plugin")
                if plugin:
                    metadata = plugin.get_metadata()
                    print(f"Plugin Info:")
                    print(f"  Name: {metadata.name}")
                    print(f"  Version: {metadata.version}")
                    print(f"  Author: {metadata.author}")
                    print(f"  Description: {metadata.description}")
                    print()
                    
                    # Demonstrate plugin-specific functionality
                    print("Testing plugin functionality...")
                    if hasattr(plugin, 'track_commit'):
                        plugin.track_commit()
                        plugin.track_commit()
                        plugin.track_commit()
                        stats = plugin.get_stats()
                        print(f"✓ Stats: {stats}")
                    print()
                
                # List all loaded plugins
                print("Loaded plugins:")
                for plugin_name in available_plugins:
                    plugin = manager.get_plugin(plugin_name)
                    if plugin:
                        metadata = plugin.get_metadata()
                        state = manager.get_plugin_state(plugin_name)
                        state_str = state.value if state else "unknown"
                        print(f"  - {metadata.name} v{metadata.version} [{state_str}]")
                print()
                
                # Disable the plugin
                print("Disabling plugin...")
                if manager.disable_plugin("example_plugin"):
                    print("✓ Plugin disabled")
                print()
                
                # Unload the plugin
                print("Unloading plugin...")
                if manager.unload_plugin("example_plugin"):
                    print("✓ Plugin unloaded")
                print()
        else:
            print("✗ Failed to load plugin")
    else:
        print("⚠ Example plugin not found")
        print("Available plugins:", available_plugins)
    
    print("=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
