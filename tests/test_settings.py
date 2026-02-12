"""
Tests for Settings management.
"""

from clevergit.ui.settings import Settings


class TestSettings:
    """Test Settings class."""

    def test_settings_initialization(self, tmp_path):
        """Test that settings can be initialized."""
        # Override config path to use temp directory
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"
        settings._load()

        assert settings._settings == {}

    def test_get_last_repository_empty(self, tmp_path):
        """Test getting last repository when none is set."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"
        settings._load()

        assert settings.get_last_repository() is None

    def test_set_and_get_last_repository(self, tmp_path):
        """Test setting and getting last repository."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        test_path = "/home/user/test-repo"
        settings.set_last_repository(test_path)

        assert settings.get_last_repository() == test_path

    def test_settings_persistence(self, tmp_path):
        """Test that settings are saved and loaded correctly."""
        # Create first settings instance and set a value
        settings1 = Settings()
        settings1.config_dir = tmp_path / ".config" / "clevergit"
        settings1.config_file = settings1.config_dir / "settings.json"

        test_path = "/home/user/test-repo"
        settings1.set_last_repository(test_path)

        # Create second settings instance and verify it loads the saved value
        settings2 = Settings()
        settings2.config_dir = tmp_path / ".config" / "clevergit"
        settings2.config_file = settings2.config_dir / "settings.json"
        settings2._load()

        assert settings2.get_last_repository() == test_path

    def test_corrupted_settings_file(self, tmp_path):
        """Test that corrupted settings file is handled gracefully."""
        config_dir = tmp_path / ".config" / "clevergit"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "settings.json"

        # Write corrupted JSON
        with open(config_file, "w") as f:
            f.write("{ corrupted json }")

        # Settings should initialize with empty dict
        settings = Settings()
        settings.config_dir = config_dir
        settings.config_file = config_file
        settings._load()

        assert settings._settings == {}
        assert settings.get_last_repository() is None

    def test_config_directory_creation(self, tmp_path):
        """Test that config directory is created if it doesn't exist."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Config dir shouldn't exist yet
        assert not settings.config_dir.exists()

        # Setting a value should create the directory
        settings.set_last_repository("/home/user/test-repo")

        assert settings.config_dir.exists()
        assert settings.config_file.exists()

    def test_get_repository_branch_empty(self, tmp_path):
        """Test getting repository branch when none is set."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"
        settings._load()

        repo_path = "/home/user/test-repo"
        assert settings.get_repository_branch(repo_path) is None

    def test_set_and_get_repository_branch(self, tmp_path):
        """Test setting and getting repository branch."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        repo_path = "/home/user/test-repo"
        branch_name = "feature/new-feature"
        settings.set_repository_branch(repo_path, branch_name)

        assert settings.get_repository_branch(repo_path) == branch_name

    def test_multiple_repository_branches(self, tmp_path):
        """Test storing branches for multiple repositories."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Set branches for multiple repos
        settings.set_repository_branch("/home/user/repo1", "main")
        settings.set_repository_branch("/home/user/repo2", "develop")
        settings.set_repository_branch("/home/user/repo3", "feature/auth")

        # Verify all are stored correctly
        assert settings.get_repository_branch("/home/user/repo1") == "main"
        assert settings.get_repository_branch("/home/user/repo2") == "develop"
        assert settings.get_repository_branch("/home/user/repo3") == "feature/auth"

    def test_update_repository_branch(self, tmp_path):
        """Test updating branch for a repository."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        repo_path = "/home/user/test-repo"

        # Set initial branch
        settings.set_repository_branch(repo_path, "main")
        assert settings.get_repository_branch(repo_path) == "main"

        # Update to new branch
        settings.set_repository_branch(repo_path, "feature/new-feature")
        assert settings.get_repository_branch(repo_path) == "feature/new-feature"

    def test_repository_branches_persistence(self, tmp_path):
        """Test that repository branches are saved and loaded correctly."""
        # Create first settings instance and set values
        settings1 = Settings()
        settings1.config_dir = tmp_path / ".config" / "clevergit"
        settings1.config_file = settings1.config_dir / "settings.json"

        settings1.set_repository_branch("/home/user/repo1", "main")
        settings1.set_repository_branch("/home/user/repo2", "develop")

        # Create second settings instance and verify it loads the saved values
        settings2 = Settings()
        settings2.config_dir = tmp_path / ".config" / "clevergit"
        settings2.config_file = settings2.config_dir / "settings.json"
        settings2._load()

        assert settings2.get_repository_branch("/home/user/repo1") == "main"
        assert settings2.get_repository_branch("/home/user/repo2") == "develop"

    def test_window_geometry(self, tmp_path):
        """Test setting and getting window geometry."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Set geometry
        settings.set_window_geometry(100, 200, 1024, 768, "main")

        # Get geometry
        geometry = settings.get_window_geometry("main")
        assert geometry == {"x": 100, "y": 200, "width": 1024, "height": 768}

    def test_open_tabs(self, tmp_path):
        """Test setting and getting open tabs."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Set tabs
        tabs = ["/repo1", "/repo2", "/repo3"]
        settings.set_open_tabs(tabs, "main")

        # Get tabs
        retrieved_tabs = settings.get_open_tabs("main")
        assert retrieved_tabs == tabs

    def test_active_tab(self, tmp_path):
        """Test setting and getting active tab index."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Set active tab
        settings.set_active_tab(2, "main")

        # Get active tab
        active_tab = settings.get_active_tab("main")
        assert active_tab == 2

    def test_session_windows(self, tmp_path):
        """Test setting and getting session windows."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Set session windows
        windows = [
            {"window_id": "1", "tabs": ["/repo1", "/repo2"], "active_tab": 0},
            {"window_id": "2", "tabs": ["/repo3"], "active_tab": 0},
        ]
        settings.set_session_windows(windows)

        # Get session windows
        retrieved_windows = settings.get_session_windows()
        assert retrieved_windows == windows

    def test_recent_repositories_deduplication(self, tmp_path):
        """Test that recent repositories are deduplicated."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Add the same repository multiple times with different path representations
        base_path = tmp_path / "test-repo"
        base_path.mkdir()

        # Add the path as-is
        settings.add_recent_repository(str(base_path))
        recent = settings.get_recent_repositories()
        assert len(recent) == 1

        # Add with trailing slash (should not duplicate on Unix)
        settings.add_recent_repository(str(base_path) + "/")
        recent = settings.get_recent_repositories()
        assert len(recent) == 1

        # Add again - should still be only one entry
        settings.add_recent_repository(str(base_path))
        recent = settings.get_recent_repositories()
        assert len(recent) == 1

    def test_recent_repositories_order(self, tmp_path):
        """Test that recent repositories maintain MRU order."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Add repositories in order
        for i in range(5):
            repo_path = tmp_path / f"repo{i}"
            repo_path.mkdir()
            settings.add_recent_repository(str(repo_path))

        recent = settings.get_recent_repositories()
        # Most recent should be first
        assert str(tmp_path / "repo4") in recent[0]
        assert len(recent) == 5

        # Add an older repo again - should move to front
        settings.add_recent_repository(str(tmp_path / "repo0"))
        recent = settings.get_recent_repositories()
        assert str(tmp_path / "repo0") in recent[0]
        assert len(recent) == 5

    def test_recent_repositories_limit(self, tmp_path):
        """Test that recent repositories are limited to 10."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Add 15 repositories
        for i in range(15):
            repo_path = tmp_path / f"repo{i}"
            repo_path.mkdir()
            settings.add_recent_repository(str(repo_path))

        recent = settings.get_recent_repositories()
        # Should only keep the 10 most recent
        assert len(recent) == 10
        # Most recent should be repo14
        assert str(tmp_path / "repo14") in recent[0]

    def test_remove_recent_repository(self, tmp_path):
        """Test removing a repository from the recent list."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Add several repositories
        repo1 = tmp_path / "repo1"
        repo2 = tmp_path / "repo2"
        repo3 = tmp_path / "repo3"
        repo1.mkdir()
        repo2.mkdir()
        repo3.mkdir()

        settings.add_recent_repository(str(repo1))
        settings.add_recent_repository(str(repo2))
        settings.add_recent_repository(str(repo3))

        recent = settings.get_recent_repositories()
        assert len(recent) == 3

        # Remove repo2
        settings.remove_recent_repository(str(repo2))
        recent = settings.get_recent_repositories()
        assert len(recent) == 2
        assert str(repo2) not in recent
        assert str(repo1) in recent
        assert str(repo3) in recent

    def test_remove_recent_repository_with_trailing_slash(self, tmp_path):
        """Test removing a repository with different path format."""
        settings = Settings()
        settings.config_dir = tmp_path / ".config" / "clevergit"
        settings.config_file = settings.config_dir / "settings.json"

        # Add repository
        repo1 = tmp_path / "repo1"
        repo1.mkdir()
        settings.add_recent_repository(str(repo1))

        recent = settings.get_recent_repositories()
        assert len(recent) == 1

        # Remove with trailing slash (should still work due to normalization)
        settings.remove_recent_repository(str(repo1) + "/")
        recent = settings.get_recent_repositories()
        assert len(recent) == 0
