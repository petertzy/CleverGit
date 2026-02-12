"""
Tests for Theme system.
"""

import pytest
from clevergit.ui.themes import Theme, ThemeManager, get_theme_manager, LightTheme, DarkTheme


class TestTheme:
    """Test Theme class."""

    def test_light_theme_initialization(self):
        """Test that light theme can be initialized with correct values."""
        theme = LightTheme()

        assert theme.name == "light"
        assert theme.background == "#ffffff"
        assert theme.text == "#24292e"
        assert theme.button_success == "#28a745"
        assert len(theme.graph_colors) == 8

    def test_dark_theme_initialization(self):
        """Test that dark theme can be initialized with correct values."""
        theme = DarkTheme()

        assert theme.name == "dark"
        assert theme.background == "#1e1e1e"
        assert theme.text == "#d4d4d4"
        assert theme.button_success == "#107c10"
        assert len(theme.graph_colors) == 8

    def test_theme_to_dict(self):
        """Test converting theme to dictionary."""
        theme = LightTheme()
        theme_dict = theme.to_dict()

        assert isinstance(theme_dict, dict)
        assert theme_dict["name"] == "light"
        assert theme_dict["background"] == "#ffffff"
        assert theme_dict["text"] == "#24292e"
        assert "graph_colors" in theme_dict
        assert isinstance(theme_dict["graph_colors"], list)

    def test_theme_stylesheet_generation(self):
        """Test that theme generates valid stylesheet."""
        theme = LightTheme()
        stylesheet = theme.get_stylesheet()

        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0
        assert "QWidget" in stylesheet
        assert theme.background in stylesheet
        assert theme.text in stylesheet


class TestThemeManager:
    """Test ThemeManager class."""

    def test_theme_manager_initialization(self):
        """Test that theme manager initializes with built-in themes."""
        manager = ThemeManager()

        themes = manager.get_available_themes()
        assert "light" in themes
        assert "dark" in themes

    def test_get_theme(self):
        """Test getting a theme by name."""
        manager = ThemeManager()

        light = manager.get_theme("light")
        assert light is not None
        assert light.name == "light"

        dark = manager.get_theme("dark")
        assert dark is not None
        assert dark.name == "dark"

    def test_get_nonexistent_theme(self):
        """Test getting a theme that doesn't exist."""
        manager = ThemeManager()

        theme = manager.get_theme("nonexistent")
        assert theme is None

    def test_set_theme(self):
        """Test setting current theme."""
        manager = ThemeManager()

        result = manager.set_theme("light")
        assert result is True

        current = manager.get_current_theme()
        assert current is not None
        assert current.name == "light"

    def test_set_nonexistent_theme(self):
        """Test setting a theme that doesn't exist."""
        manager = ThemeManager()

        result = manager.set_theme("nonexistent")
        assert result is False

    def test_register_custom_theme(self):
        """Test registering a custom theme."""
        manager = ThemeManager()

        custom_data = {
            "background": "#123456",
            "text": "#abcdef",
            "button_primary": "#ff0000",
        }

        manager.register_custom_theme("custom", custom_data)

        # Verify theme is registered
        themes = manager.get_available_themes()
        assert "custom" in themes

        # Verify theme can be retrieved
        custom = manager.get_theme("custom")
        assert custom is not None
        assert custom.name == "custom"
        assert custom.background == "#123456"
        assert custom.text == "#abcdef"

    def test_export_theme(self):
        """Test exporting a theme to dictionary."""
        manager = ThemeManager()

        theme_data = manager.export_theme("light")
        assert theme_data is not None
        assert isinstance(theme_data, dict)
        assert theme_data["name"] == "light"

    def test_export_nonexistent_theme(self):
        """Test exporting a theme that doesn't exist."""
        manager = ThemeManager()

        theme_data = manager.export_theme("nonexistent")
        assert theme_data is None

    def test_singleton_instance(self):
        """Test that get_theme_manager returns singleton instance."""
        manager1 = get_theme_manager()
        manager2 = get_theme_manager()

        assert manager1 is manager2


class TestThemeSettings:
    """Test theme-related settings."""

    def test_theme_persistence(self, tmp_path):
        """Test that theme selection is persisted."""
        from clevergit.ui.settings import Settings

        # Create settings instance
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Set theme
        settings.set_theme("dark")

        # Verify it was saved
        assert settings.get_theme() == "dark"

        # Create new instance and verify persistence
        settings2 = Settings()
        settings2.config_dir = tmp_path / ".config" / "clevergit"
        settings2.config_file = settings2.config_dir / "settings.json"
        settings2._load()

        assert settings2.get_theme() == "dark"

    def test_custom_theme_persistence(self, tmp_path):
        """Test that custom themes are persisted."""
        from clevergit.ui.settings import Settings

        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        custom_data = {
            "background": "#123456",
            "text": "#abcdef",
        }

        settings.add_custom_theme("my_theme", custom_data)

        # Verify custom themes are saved
        custom_themes = settings.get_custom_themes()
        assert "my_theme" in custom_themes
        assert custom_themes["my_theme"]["background"] == "#123456"

    def test_use_system_theme_default(self, tmp_path):
        """Test that system theme is used by default."""
        from clevergit.ui.settings import Settings

        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"
        settings._load()

        assert settings.use_system_theme() is True
