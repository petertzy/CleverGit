"""
Test suite for Git Flow operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.core.git_flow import GitFlow, GitFlowConfig
from clevergit.git.errors import BranchError, UncommittedChangesError


@pytest.fixture
def test_repo(tmp_path):
    """Create a test repository with initial commits."""
    repo = Repo.init(str(tmp_path / "test_repo"))

    # Configure git user for tests
    repo.client._run_command(["git", "config", "user.email", "test@example.com"])
    repo.client._run_command(["git", "config", "user.name", "Test User"])

    # Create initial commit (this creates the 'master' branch by default)
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)

    # Rename master to main for consistency with the default config
    try:
        repo.client.rename_branch("master", "main")
    except Exception:
        # Branch might already be named 'main' in newer Git versions
        pass

    return repo


@pytest.fixture
def initialized_git_flow(test_repo):
    """Create a Git Flow instance initialized with a test repository."""
    git_flow = GitFlow(test_repo.client)
    git_flow.initialize()
    return git_flow, test_repo


def test_git_flow_config_defaults():
    """Test Git Flow configuration defaults."""
    config = GitFlowConfig()

    assert config.master_branch == "main"
    assert config.develop_branch == "develop"
    assert config.feature_prefix == "feature/"
    assert config.release_prefix == "release/"
    assert config.hotfix_prefix == "hotfix/"
    assert config.version_tag_prefix == "v"


def test_git_flow_config_custom():
    """Test Git Flow configuration with custom values."""
    config = GitFlowConfig(
        master_branch="master",
        develop_branch="dev",
        feature_prefix="feat/",
        release_prefix="rel/",
        hotfix_prefix="fix/",
        version_tag_prefix="version-",
    )

    assert config.master_branch == "master"
    assert config.develop_branch == "dev"
    assert config.feature_prefix == "feat/"
    assert config.release_prefix == "rel/"
    assert config.hotfix_prefix == "fix/"
    assert config.version_tag_prefix == "version-"


def test_git_flow_is_not_initialized(test_repo):
    """Test that Git Flow is not initialized by default."""
    git_flow = GitFlow(test_repo.client)
    assert not git_flow.is_initialized()


def test_git_flow_initialize(test_repo):
    """Test Git Flow initialization."""
    git_flow = GitFlow(test_repo.client)

    # Should not be initialized
    assert not git_flow.is_initialized()

    # Initialize
    git_flow.initialize()

    # Should be initialized
    assert git_flow.is_initialized()

    # Develop branch should exist
    branches = test_repo.client.list_branches()
    assert "develop" in branches


def test_git_flow_initialize_twice_fails(test_repo):
    """Test that initializing Git Flow twice raises an error."""
    git_flow = GitFlow(test_repo.client)

    # First initialization should succeed
    git_flow.initialize()

    # Second initialization should fail
    with pytest.raises(BranchError) as exc_info:
        git_flow.initialize()

    assert "already initialized" in str(exc_info.value).lower()


def test_git_flow_initialize_force(test_repo):
    """Test that force initialization works."""
    git_flow = GitFlow(test_repo.client)

    # First initialization
    git_flow.initialize()

    # Force initialization should succeed
    git_flow.initialize(force=True)

    assert git_flow.is_initialized()


def test_start_feature(initialized_git_flow):
    """Test starting a feature branch."""
    git_flow, repo = initialized_git_flow

    # Start a feature
    branch_name = git_flow.start_feature("user-auth")

    assert branch_name == "feature/user-auth"
    assert "feature/user-auth" in repo.client.list_branches()
    assert repo.client.current_branch() == "feature/user-auth"


def test_start_feature_without_initialization(test_repo):
    """Test that starting a feature without initialization fails."""
    git_flow = GitFlow(test_repo.client)

    with pytest.raises(BranchError) as exc_info:
        git_flow.start_feature("test-feature")

    assert "not initialized" in str(exc_info.value).lower()


def test_start_feature_duplicate_fails(initialized_git_flow):
    """Test that starting a duplicate feature fails."""
    git_flow, repo = initialized_git_flow

    # Start first feature
    git_flow.start_feature("duplicate")

    # Switch back to develop
    repo.client.checkout("develop")

    # Try to start same feature again
    with pytest.raises(BranchError) as exc_info:
        git_flow.start_feature("duplicate")

    assert "already exists" in str(exc_info.value).lower()


def test_finish_feature(initialized_git_flow):
    """Test finishing a feature branch."""
    git_flow, repo = initialized_git_flow

    # Start a feature
    git_flow.start_feature("test-feature")

    # Make a change
    test_file = repo.path / "feature.txt"
    test_file.write_text("feature content")
    repo.commit_all("Add feature", allow_empty=True)

    # Finish the feature
    git_flow.finish_feature("test-feature")

    # Should be on develop
    assert repo.client.current_branch() == "develop"

    # Feature branch should be deleted
    assert "feature/test-feature" not in repo.client.list_branches()

    # File should exist on develop
    assert test_file.exists()


def test_finish_feature_full_name(initialized_git_flow):
    """Test finishing a feature with full branch name."""
    git_flow, repo = initialized_git_flow

    # Start a feature
    git_flow.start_feature("test-feature")

    # Make a change
    repo.commit_all("Feature change", allow_empty=True)

    # Finish using full branch name
    git_flow.finish_feature("feature/test-feature")

    # Should be on develop
    assert repo.client.current_branch() == "develop"
    assert "feature/test-feature" not in repo.client.list_branches()


def test_finish_feature_nonexistent_fails(initialized_git_flow):
    """Test that finishing a nonexistent feature fails."""
    git_flow, repo = initialized_git_flow

    with pytest.raises(BranchError) as exc_info:
        git_flow.finish_feature("nonexistent")

    assert "does not exist" in str(exc_info.value).lower()


def test_start_release(initialized_git_flow):
    """Test starting a release branch."""
    git_flow, repo = initialized_git_flow

    # Start a release
    branch_name = git_flow.start_release("1.0.0")

    assert branch_name == "release/1.0.0"
    assert "release/1.0.0" in repo.client.list_branches()
    assert repo.client.current_branch() == "release/1.0.0"


def test_finish_release(initialized_git_flow):
    """Test finishing a release branch."""
    git_flow, repo = initialized_git_flow

    # Start a release
    git_flow.start_release("1.0.0")

    # Make a change
    test_file = repo.path / "release.txt"
    test_file.write_text("release content")
    repo.commit_all("Release changes", allow_empty=True)

    # Finish the release
    git_flow.finish_release("1.0.0", tag_message="Release 1.0.0")

    # Should be on develop
    assert repo.client.current_branch() == "develop"

    # Release branch should be deleted
    assert "release/1.0.0" not in repo.client.list_branches()

    # Tag should exist
    tags = repo.list_tags()
    tag_names = [t.name for t in tags]
    assert "v1.0.0" in tag_names


def test_finish_release_full_name(initialized_git_flow):
    """Test finishing a release with full branch name."""
    git_flow, repo = initialized_git_flow

    # Start a release
    git_flow.start_release("1.0.0")

    # Make a change
    repo.commit_all("Release changes", allow_empty=True)

    # Finish using full branch name
    git_flow.finish_release("release/1.0.0")

    # Should be on develop
    assert repo.client.current_branch() == "develop"
    assert "release/1.0.0" not in repo.client.list_branches()


def test_start_hotfix(initialized_git_flow):
    """Test starting a hotfix branch."""
    git_flow, repo = initialized_git_flow

    # Start a hotfix
    branch_name = git_flow.start_hotfix("1.0.1")

    assert branch_name == "hotfix/1.0.1"
    assert "hotfix/1.0.1" in repo.client.list_branches()
    assert repo.client.current_branch() == "hotfix/1.0.1"


def test_finish_hotfix(initialized_git_flow):
    """Test finishing a hotfix branch."""
    git_flow, repo = initialized_git_flow

    # Start a hotfix
    git_flow.start_hotfix("1.0.1")

    # Make a change
    test_file = repo.path / "hotfix.txt"
    test_file.write_text("hotfix content")
    repo.commit_all("Hotfix changes", allow_empty=True)

    # Finish the hotfix
    git_flow.finish_hotfix("1.0.1", tag_message="Hotfix 1.0.1")

    # Should be on develop
    assert repo.client.current_branch() == "develop"

    # Hotfix branch should be deleted
    assert "hotfix/1.0.1" not in repo.client.list_branches()

    # Tag should exist
    tags = repo.list_tags()
    tag_names = [t.name for t in tags]
    assert "v1.0.1" in tag_names


def test_get_active_branches(initialized_git_flow):
    """Test getting active Git Flow branches."""
    git_flow, repo = initialized_git_flow

    # Start various branches
    git_flow.start_feature("feature1")
    repo.client.checkout("develop")

    git_flow.start_feature("feature2")
    repo.client.checkout("develop")

    git_flow.start_release("1.0.0")
    repo.client.checkout("develop")

    git_flow.start_hotfix("1.0.1")
    repo.client.checkout("develop")

    # Get active branches
    active = git_flow.get_active_branches()

    assert len(active["features"]) == 2
    assert "feature/feature1" in active["features"]
    assert "feature/feature2" in active["features"]

    assert len(active["releases"]) == 1
    assert "release/1.0.0" in active["releases"]

    assert len(active["hotfixes"]) == 1
    assert "hotfix/1.0.1" in active["hotfixes"]


def test_get_status_not_initialized(test_repo):
    """Test getting status when not initialized."""
    git_flow = GitFlow(test_repo.client)

    status = git_flow.get_status()

    assert status["initialized"] is False
    assert "config" in status
    assert "active_branches" not in status


def test_get_status_initialized(initialized_git_flow):
    """Test getting status when initialized."""
    git_flow, repo = initialized_git_flow

    # Start a feature
    git_flow.start_feature("test")

    status = git_flow.get_status()

    assert status["initialized"] is True
    assert status["config"]["master_branch"] == "main"
    assert status["config"]["develop_branch"] == "develop"
    assert "active_branches" in status
    assert "current_branch" in status


def test_start_feature_with_uncommitted_changes_fails(initialized_git_flow):
    """Test that starting a feature with uncommitted changes fails."""
    git_flow, repo = initialized_git_flow

    # Create uncommitted changes
    test_file = repo.path / "uncommitted.txt"
    test_file.write_text("uncommitted")

    with pytest.raises(UncommittedChangesError):
        git_flow.start_feature("test")


def test_finish_feature_with_uncommitted_changes_fails(initialized_git_flow):
    """Test that finishing a feature with uncommitted changes fails."""
    git_flow, repo = initialized_git_flow

    # Start a feature
    git_flow.start_feature("test")

    # Create uncommitted changes
    test_file = repo.path / "uncommitted.txt"
    test_file.write_text("uncommitted")

    with pytest.raises(UncommittedChangesError):
        git_flow.finish_feature("test")


def test_custom_config(test_repo):
    """Test Git Flow with custom configuration."""
    config = GitFlowConfig(
        master_branch="master",
        develop_branch="dev",
        feature_prefix="feat/",
        release_prefix="rel/",
        hotfix_prefix="fix/",
    )

    # Rename main to master for this test
    test_repo.client.rename_branch("main", "master")

    git_flow = GitFlow(test_repo.client, config)
    git_flow.initialize()

    assert git_flow.is_initialized()
    assert "dev" in test_repo.client.list_branches()

    # Start a feature with custom prefix
    branch_name = git_flow.start_feature("test")
    assert branch_name == "feat/test"
    assert "feat/test" in test_repo.client.list_branches()
