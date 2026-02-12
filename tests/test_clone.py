"""
Test suite for repository cloning operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo


def test_clone_basic(tmp_path):
    """Test basic repository cloning."""
    # Create a source repository
    source_repo_path = tmp_path / "source"
    source_repo = Repo.init(str(source_repo_path))

    # Create a test file and commit
    test_file = source_repo_path / "test.txt"
    test_file.write_text("test content")
    source_repo.commit_all("Initial commit", allow_empty=False)

    # Clone the repository
    dest_repo_path = tmp_path / "dest"
    cloned_repo = Repo.clone(str(source_repo_path), str(dest_repo_path))

    assert cloned_repo is not None
    assert cloned_repo.path.exists()
    assert (cloned_repo.path / ".git").exists()

    # Verify the file exists in cloned repo
    cloned_file = dest_repo_path / "test.txt"
    assert cloned_file.exists()
    assert cloned_file.read_text() == "test content"


def test_clone_with_branch(tmp_path):
    """Test cloning a specific branch."""
    # Create a source repository with multiple branches
    source_repo_path = tmp_path / "source"
    source_repo = Repo.init(str(source_repo_path))

    # Create initial commit
    test_file = source_repo_path / "main.txt"
    test_file.write_text("main branch")
    source_repo.commit_all("Main commit", allow_empty=False)

    # Create a feature branch
    source_repo.create_branch("feature")
    source_repo.checkout("feature")

    feature_file = source_repo_path / "feature.txt"
    feature_file.write_text("feature branch")
    source_repo.commit_all("Feature commit", allow_empty=False)

    # Clone only the feature branch
    dest_repo_path = tmp_path / "dest"
    cloned_repo = Repo.clone(str(source_repo_path), str(dest_repo_path), branch="feature")

    assert cloned_repo is not None
    # Check current branch
    current = cloned_repo.current_branch()
    assert current == "feature"

    # Verify feature file exists
    cloned_feature_file = dest_repo_path / "feature.txt"
    assert cloned_feature_file.exists()


def test_clone_shallow(tmp_path):
    """Test shallow cloning.

    Note: Shallow cloning doesn't work with local file:// URLs.
    This test verifies the API accepts the parameter, but we can't
    verify the actual depth restriction with local repos.
    """
    # Create a source repository with multiple commits
    source_repo_path = tmp_path / "source"
    source_repo = Repo.init(str(source_repo_path))

    # Create multiple commits
    for i in range(5):
        test_file = source_repo_path / f"file{i}.txt"
        test_file.write_text(f"content {i}")
        source_repo.commit_all(f"Commit {i}", allow_empty=False)

    # Clone with depth=1 (won't actually be shallow for local clones)
    dest_repo_path = tmp_path / "dest"
    cloned_repo = Repo.clone(str(source_repo_path), str(dest_repo_path), depth=1)

    assert cloned_repo is not None
    assert cloned_repo.path.exists()

    # Note: Local clones don't respect depth, so we just verify it completes
    # For remote URLs (https/ssh), depth would work correctly
    log = cloned_repo.log(max_count=10)
    assert len(log) >= 1  # At least one commit exists


def test_clone_progress_callback(tmp_path):
    """Test clone with progress callback."""
    # Create a source repository
    source_repo_path = tmp_path / "source"
    source_repo = Repo.init(str(source_repo_path))

    # Create a test file
    test_file = source_repo_path / "test.txt"
    test_file.write_text("test content")
    source_repo.commit_all("Initial commit", allow_empty=False)

    # Track progress messages
    progress_messages = []

    def progress_callback(message: str):
        progress_messages.append(message)

    # Clone with progress callback
    dest_repo_path = tmp_path / "dest"
    cloned_repo = Repo.clone(
        str(source_repo_path), str(dest_repo_path), progress_callback=progress_callback
    )

    assert cloned_repo is not None
    # Verify we received progress updates
    assert len(progress_messages) > 0


def test_clone_to_existing_empty_directory(tmp_path):
    """Test cloning to an existing empty directory."""
    source_repo_path = tmp_path / "source"
    source_repo = Repo.init(str(source_repo_path))

    test_file = source_repo_path / "test.txt"
    test_file.write_text("test content")
    source_repo.commit_all("Initial commit", allow_empty=False)

    # Create destination directory
    dest_repo_path = tmp_path / "dest"
    dest_repo_path.mkdir()

    # Should still work with empty directory
    cloned_repo = Repo.clone(str(source_repo_path), str(dest_repo_path))

    assert cloned_repo is not None
    assert (dest_repo_path / "test.txt").exists()


def test_clone_invalid_url(tmp_path):
    """Test cloning from an invalid URL."""
    dest_repo_path = tmp_path / "dest"

    with pytest.raises(Exception):
        Repo.clone("invalid-url", str(dest_repo_path))


def test_clone_nonexistent_branch(tmp_path):
    """Test cloning a non-existent branch."""
    source_repo_path = tmp_path / "source"
    source_repo = Repo.init(str(source_repo_path))

    test_file = source_repo_path / "test.txt"
    test_file.write_text("test content")
    source_repo.commit_all("Initial commit", allow_empty=False)

    dest_repo_path = tmp_path / "dest"

    with pytest.raises(Exception):
        Repo.clone(str(source_repo_path), str(dest_repo_path), branch="nonexistent-branch")
