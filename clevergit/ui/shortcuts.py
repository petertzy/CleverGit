"""
Keyboard shortcuts management for CleverGit GUI.
"""

from typing import Dict, Optional, Callable, Any
from PySide6.QtGui import QKeySequence, QShortcut, QAction
from PySide6.QtWidgets import QWidget


# Default keyboard shortcuts mapping
DEFAULT_SHORTCUTS: Dict[str, str] = {
    # File operations
    "file.new_tab": "Ctrl+T",
    "file.new_window": "Ctrl+Shift+N",
    "file.clone": "Ctrl+Shift+C",
    "file.open": "Ctrl+O",
    "file.close_tab": "Ctrl+W",
    "file.exit": "Ctrl+Q",
    
    # Edit operations
    "edit.refresh": "F5",
    "edit.view_diff": "Ctrl+D",
    "edit.blame": "Ctrl+B",
    
    # Commit operations
    "commit.new": "Ctrl+K",
    
    # Remote operations
    "remote.pull": "Ctrl+Shift+P",
    "remote.push": "Ctrl+Shift+U",
    
    # Tab navigation
    "tab.next": "Ctrl+Tab",
    "tab.previous": "Ctrl+Shift+Tab",
    
    # Search
    "search.command_palette": "Ctrl+P",
    
    # Help
    "help.shortcuts": "F1",
}

# Human-readable descriptions for shortcuts
SHORTCUT_DESCRIPTIONS: Dict[str, str] = {
    "file.new_tab": "Open repository in new tab",
    "file.new_window": "Open new window",
    "file.clone": "Clone repository",
    "file.open": "Open repository",
    "file.close_tab": "Close current tab",
    "file.exit": "Exit application",
    "edit.refresh": "Refresh current view",
    "edit.view_diff": "View diff",
    "edit.blame": "Show blame for file",
    "commit.new": "Create new commit",
    "remote.pull": "Pull from remote",
    "remote.push": "Push to remote",
    "tab.next": "Switch to next tab",
    "tab.previous": "Switch to previous tab",
    "search.command_palette": "Open command palette",
    "help.shortcuts": "Show keyboard shortcuts help",
}

# Categories for organizing shortcuts
SHORTCUT_CATEGORIES: Dict[str, str] = {
    "file.new_tab": "File",
    "file.new_window": "File",
    "file.clone": "File",
    "file.open": "File",
    "file.close_tab": "File",
    "file.exit": "File",
    "edit.refresh": "Edit",
    "edit.view_diff": "Edit",
    "edit.blame": "Edit",
    "commit.new": "Commit",
    "remote.pull": "Remote",
    "remote.push": "Remote",
    "tab.next": "Navigation",
    "tab.previous": "Navigation",
    "search.command_palette": "Search",
    "help.shortcuts": "Help",
}


class ShortcutManager:
    """Manage keyboard shortcuts for the application."""
    
    def __init__(self, settings: Any) -> None:
        """
        Initialize shortcut manager.
        
        Args:
            settings: Settings instance for persisting shortcuts
        """
        self.settings = settings
        self._shortcuts: Dict[str, str] = {}
        self._registered_shortcuts: Dict[str, QShortcut] = {}
        self._registered_actions: Dict[str, QAction] = {}
        self._load_shortcuts()
    
    def _load_shortcuts(self) -> None:
        """Load shortcuts from settings or use defaults."""
        saved_shortcuts = self.settings.get_shortcuts()
        if saved_shortcuts:
            self._shortcuts = saved_shortcuts.copy()
        else:
            self._shortcuts = DEFAULT_SHORTCUTS.copy()
    
    def get_shortcut(self, action_id: str) -> Optional[str]:
        """
        Get the keyboard shortcut for an action.
        
        Args:
            action_id: Action identifier (e.g., 'file.open')
            
        Returns:
            Keyboard shortcut string or None if not found
        """
        return self._shortcuts.get(action_id)
    
    def get_all_shortcuts(self) -> Dict[str, str]:
        """
        Get all keyboard shortcuts.
        
        Returns:
            Dictionary mapping action IDs to shortcut strings
        """
        return self._shortcuts.copy()
    
    def set_shortcut(self, action_id: str, shortcut: str) -> bool:
        """
        Set a keyboard shortcut for an action.
        
        Args:
            action_id: Action identifier (e.g., 'file.open')
            shortcut: Keyboard shortcut string (e.g., 'Ctrl+O')
            
        Returns:
            True if shortcut was set successfully, False otherwise
        """
        # Validate the shortcut string
        key_sequence = QKeySequence(shortcut)
        if key_sequence.isEmpty() and shortcut:
            return False
        
        # Check for conflicts
        if shortcut and self._is_conflicting(action_id, shortcut):
            return False
        
        # Update shortcut
        self._shortcuts[action_id] = shortcut
        self._save_shortcuts()
        
        # Update registered shortcuts/actions
        self._update_registered_shortcut(action_id, shortcut)
        
        return True
    
    def _is_conflicting(self, action_id: str, shortcut: str) -> bool:
        """
        Check if a shortcut conflicts with existing shortcuts.
        
        Args:
            action_id: Action identifier to check
            shortcut: Keyboard shortcut string
            
        Returns:
            True if there's a conflict, False otherwise
        """
        for existing_id, existing_shortcut in self._shortcuts.items():
            if existing_id != action_id and existing_shortcut == shortcut:
                return True
        return False
    
    def reset_shortcut(self, action_id: str) -> bool:
        """
        Reset a shortcut to its default value.
        
        Args:
            action_id: Action identifier
            
        Returns:
            True if reset was successful, False otherwise
        """
        if action_id in DEFAULT_SHORTCUTS:
            return self.set_shortcut(action_id, DEFAULT_SHORTCUTS[action_id])
        return False
    
    def reset_all_shortcuts(self) -> None:
        """Reset all shortcuts to their default values."""
        self._shortcuts = DEFAULT_SHORTCUTS.copy()
        self._save_shortcuts()
        
        # Update all registered shortcuts/actions
        for action_id in self._shortcuts:
            self._update_registered_shortcut(action_id, self._shortcuts[action_id])
    
    def _save_shortcuts(self) -> None:
        """Save shortcuts to settings."""
        self.settings.set_shortcuts(self._shortcuts)
    
    def register_shortcut(
        self,
        action_id: str,
        parent: QWidget,
        callback: Callable[[], None]
    ) -> Optional[QShortcut]:
        """
        Register a keyboard shortcut with a callback.
        
        Args:
            action_id: Action identifier
            parent: Parent widget for the shortcut
            callback: Function to call when shortcut is activated
            
        Returns:
            QShortcut instance or None if action_id not found
        """
        shortcut_str = self.get_shortcut(action_id)
        if not shortcut_str:
            return None
        
        shortcut = QShortcut(QKeySequence(shortcut_str), parent)
        shortcut.activated.connect(callback)
        
        # Store reference to update later if needed
        self._registered_shortcuts[action_id] = shortcut
        
        return shortcut
    
    def register_action(self, action_id: str, action: QAction) -> None:
        """
        Register a QAction with a shortcut.
        
        Args:
            action_id: Action identifier
            action: QAction to associate with the shortcut
        """
        shortcut_str = self.get_shortcut(action_id)
        if shortcut_str:
            action.setShortcut(shortcut_str)
        
        # Store reference to update later if needed
        self._registered_actions[action_id] = action
    
    def _update_registered_shortcut(self, action_id: str, shortcut: str) -> None:
        """
        Update a registered shortcut or action.
        
        Args:
            action_id: Action identifier
            shortcut: New keyboard shortcut string
        """
        # Update registered QShortcut
        if action_id in self._registered_shortcuts:
            qshortcut = self._registered_shortcuts[action_id]
            qshortcut.setKey(QKeySequence(shortcut))
        
        # Update registered QAction
        if action_id in self._registered_actions:
            action = self._registered_actions[action_id]
            action.setShortcut(shortcut)
    
    def get_shortcuts_by_category(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Get shortcuts organized by category.
        
        Returns:
            Dictionary mapping categories to their shortcuts with descriptions
        """
        result: Dict[str, Dict[str, Dict[str, str]]] = {}
        
        for action_id, shortcut in self._shortcuts.items():
            category = SHORTCUT_CATEGORIES.get(action_id, "Other")
            description = SHORTCUT_DESCRIPTIONS.get(action_id, action_id)
            
            if category not in result:
                result[category] = {}
            
            result[category][action_id] = {
                "shortcut": shortcut,
                "description": description
            }
        
        return result
