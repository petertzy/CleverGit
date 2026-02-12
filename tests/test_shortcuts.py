"""
Test suite for keyboard shortcuts module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys

# Mock PySide6 modules before importing shortcuts module
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtGui'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()

from clevergit.ui.shortcuts import (
    ShortcutManager,
    DEFAULT_SHORTCUTS,
    SHORTCUT_DESCRIPTIONS,
    SHORTCUT_CATEGORIES,
)
from clevergit.ui.settings import Settings


class MockQKeySequence:
    """Mock QKeySequence for testing."""
    
    def __init__(self, shortcut):
        self.shortcut = shortcut
        self._empty = not shortcut or shortcut == "InvalidKey123"
    
    def isEmpty(self):
        return self._empty


# Patch QKeySequence in the shortcuts module
import clevergit.ui.shortcuts
clevergit.ui.shortcuts.QKeySequence = MockQKeySequence


class MockSettings:
    """Mock settings for testing."""
    
    def __init__(self):
        self._shortcuts = None
    
    def get_shortcuts(self):
        """Get saved shortcuts."""
        return self._shortcuts
    
    def set_shortcuts(self, shortcuts):
        """Save shortcuts."""
        self._shortcuts = shortcuts


def test_shortcut_manager_initialization():
    """Test ShortcutManager initialization with default shortcuts."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    # Should have loaded default shortcuts
    assert manager.get_shortcut("file.open") == "Ctrl+O"
    assert manager.get_shortcut("file.new_tab") == "Ctrl+T"
    assert manager.get_shortcut("edit.refresh") == "F5"


def test_shortcut_manager_load_custom_shortcuts():
    """Test loading custom shortcuts from settings."""
    mock_settings = MockSettings()
    custom_shortcuts = {
        "file.open": "Ctrl+Shift+O",
        "file.new_tab": "Ctrl+N",
    }
    mock_settings._shortcuts = custom_shortcuts
    
    manager = ShortcutManager(mock_settings)
    
    # Should have loaded custom shortcuts
    assert manager.get_shortcut("file.open") == "Ctrl+Shift+O"
    assert manager.get_shortcut("file.new_tab") == "Ctrl+N"


def test_get_all_shortcuts():
    """Test getting all shortcuts."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    all_shortcuts = manager.get_all_shortcuts()
    
    # Should return a copy of all shortcuts
    assert isinstance(all_shortcuts, dict)
    assert len(all_shortcuts) > 0
    assert "file.open" in all_shortcuts
    
    # Should be a copy, not the original
    all_shortcuts["file.open"] = "Test"
    assert manager.get_shortcut("file.open") != "Test"


def test_set_shortcut():
    """Test setting a keyboard shortcut."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    # Set a new shortcut
    result = manager.set_shortcut("file.open", "Ctrl+Shift+O")
    
    assert result is True
    assert manager.get_shortcut("file.open") == "Ctrl+Shift+O"
    assert mock_settings._shortcuts["file.open"] == "Ctrl+Shift+O"


def test_set_invalid_shortcut():
    """Test setting an invalid shortcut."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    # Try to set an invalid shortcut
    result = manager.set_shortcut("file.open", "InvalidKey123")
    
    assert result is False
    # Should keep the original value
    assert manager.get_shortcut("file.open") == "Ctrl+O"


def test_set_conflicting_shortcut():
    """Test setting a shortcut that conflicts with another action."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    # Try to set a shortcut that's already used by another action
    result = manager.set_shortcut("file.new_tab", "Ctrl+O")  # Already used by file.open
    
    assert result is False
    # Should keep the original value
    assert manager.get_shortcut("file.new_tab") == "Ctrl+T"


def test_set_empty_shortcut():
    """Test setting an empty shortcut (disable shortcut)."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    # Set empty shortcut to disable it
    result = manager.set_shortcut("file.open", "")
    
    assert result is True
    assert manager.get_shortcut("file.open") == ""


def test_reset_shortcut():
    """Test resetting a shortcut to default."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    # Change a shortcut
    manager.set_shortcut("file.open", "Ctrl+Shift+O")
    assert manager.get_shortcut("file.open") == "Ctrl+Shift+O"
    
    # Reset it
    result = manager.reset_shortcut("file.open")
    
    assert result is True
    assert manager.get_shortcut("file.open") == DEFAULT_SHORTCUTS["file.open"]


def test_reset_nonexistent_shortcut():
    """Test resetting a shortcut that doesn't exist in defaults."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    # Try to reset a non-existent shortcut
    result = manager.reset_shortcut("nonexistent.action")
    
    assert result is False


def test_reset_all_shortcuts():
    """Test resetting all shortcuts to defaults."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    # Change some shortcuts
    manager.set_shortcut("file.open", "Ctrl+Shift+O")
    manager.set_shortcut("file.new_tab", "Ctrl+N")
    
    # Reset all
    manager.reset_all_shortcuts()
    
    # Should be back to defaults
    assert manager.get_shortcut("file.open") == DEFAULT_SHORTCUTS["file.open"]
    assert manager.get_shortcut("file.new_tab") == DEFAULT_SHORTCUTS["file.new_tab"]


def test_get_shortcuts_by_category():
    """Test getting shortcuts organized by category."""
    mock_settings = MockSettings()
    manager = ShortcutManager(mock_settings)
    
    shortcuts_by_category = manager.get_shortcuts_by_category()
    
    # Should return a dict with categories
    assert isinstance(shortcuts_by_category, dict)
    assert "File" in shortcuts_by_category
    assert "Edit" in shortcuts_by_category
    
    # Each category should have shortcuts with descriptions
    file_shortcuts = shortcuts_by_category["File"]
    assert "file.open" in file_shortcuts
    assert "shortcut" in file_shortcuts["file.open"]
    assert "description" in file_shortcuts["file.open"]


def test_default_shortcuts_completeness():
    """Test that all default shortcuts have descriptions and categories."""
    for action_id in DEFAULT_SHORTCUTS:
        assert action_id in SHORTCUT_DESCRIPTIONS, f"Missing description for {action_id}"
        assert action_id in SHORTCUT_CATEGORIES, f"Missing category for {action_id}"


def test_shortcut_manager_with_real_settings(tmp_path):
    """Test ShortcutManager with real Settings instance."""
    # Create a temporary config directory
    config_dir = tmp_path / ".config" / "clevergit"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Settings with custom config path
    settings = Settings()
    settings.config_dir = config_dir
    settings.config_file = config_dir / "settings.json"
    
    # Create ShortcutManager
    manager = ShortcutManager(settings)
    
    # Change a shortcut
    manager.set_shortcut("file.open", "Ctrl+Shift+O")
    
    # Verify the settings file was created and contains the shortcut
    assert settings.config_file.exists(), "Settings file should be created"
    
    import json
    with open(settings.config_file, 'r') as f:
        saved_data = json.load(f)
    
    assert "shortcuts" in saved_data, "Settings should contain shortcuts key"
    assert saved_data["shortcuts"]["file.open"] == "Ctrl+Shift+O", "Shortcut should be saved"
    
    # Create a new manager with the same settings
    manager2 = ShortcutManager(settings)
    
    # Should have loaded the saved shortcut
    assert manager2.get_shortcut("file.open") == "Ctrl+Shift+O"
