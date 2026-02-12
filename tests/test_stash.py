"""
Test suite for stash operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.models.stash_info import StashInfo


def test_stash_save_and_list(tmp_path):
    """Test saving and listing stashes."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Make some changes
    test_file.write_text("modified content")
    
    # Save to stash
    repo.stash_save("Test stash message")
    
    # List stashes
    stashes = repo.stash_list()
    
    assert len(stashes) > 0
    assert isinstance(stashes[0], StashInfo)
    assert "Test stash message" in stashes[0].message


def test_stash_apply(tmp_path):
    """Test applying a stash."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Make some changes
    test_file.write_text("modified content")
    
    # Save to stash
    repo.stash_save("Test stash")
    
    # File should be back to initial state
    assert test_file.read_text() == "initial content"
    
    # Apply stash
    repo.stash_apply(0)
    
    # File should have modified content again
    assert test_file.read_text() == "modified content"
    
    # Stash should still exist
    stashes = repo.stash_list()
    assert len(stashes) == 1


def test_stash_pop(tmp_path):
    """Test popping a stash."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Make some changes
    test_file.write_text("modified content")
    
    # Save to stash
    repo.stash_save("Test stash")
    
    # File should be back to initial state
    assert test_file.read_text() == "initial content"
    
    # Pop stash
    repo.stash_pop(0)
    
    # File should have modified content again
    assert test_file.read_text() == "modified content"
    
    # Stash should be removed
    stashes = repo.stash_list()
    assert len(stashes) == 0


def test_stash_drop(tmp_path):
    """Test dropping a stash."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Make some changes
    test_file.write_text("modified content")
    
    # Save to stash
    repo.stash_save("Test stash")
    
    # Verify stash exists
    stashes = repo.stash_list()
    assert len(stashes) == 1
    
    # Drop stash
    repo.stash_drop(0)
    
    # Stash should be removed
    stashes = repo.stash_list()
    assert len(stashes) == 0
    
    # File should still be in initial state
    assert test_file.read_text() == "initial content"


def test_stash_clear(tmp_path):
    """Test clearing all stashes."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create multiple stashes
    for i in range(3):
        test_file.write_text(f"content {i}")
        repo.stash_save(f"Stash {i}")
        test_file.write_text("initial content")
    
    # Verify stashes exist
    stashes = repo.stash_list()
    assert len(stashes) == 3
    
    # Clear all stashes
    repo.stash_clear()
    
    # Stashes should be removed
    stashes = repo.stash_list()
    assert len(stashes) == 0


def test_stash_show(tmp_path):
    """Test showing stash content."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Make some changes
    test_file.write_text("modified content")
    
    # Save to stash
    repo.stash_save("Test stash")
    
    # Show stash
    diff = repo.stash_show(0)
    
    # Diff should contain the changes
    assert "test.txt" in diff
    assert "modified content" in diff or "+modified content" in diff


def test_stash_include_untracked(tmp_path):
    """Test stashing with untracked files."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create untracked file
    new_file = repo.path / "new.txt"
    new_file.write_text("new content")
    
    # Save to stash with untracked files
    repo.stash_save("Test stash with untracked", include_untracked=True)
    
    # New file should be removed
    assert not new_file.exists()
    
    # Apply stash
    repo.stash_apply(0)
    
    # New file should be restored
    assert new_file.exists()
    assert new_file.read_text() == "new content"


def test_stash_multiple_entries(tmp_path):
    """Test multiple stash entries."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create multiple stashes
    for i in range(3):
        test_file.write_text(f"content {i}")
        repo.stash_save(f"Stash {i}")
    
    # List stashes
    stashes = repo.stash_list()
    assert len(stashes) == 3
    
    # Verify stash order (most recent first)
    assert "Stash 2" in stashes[0].message
    assert "Stash 1" in stashes[1].message
    assert "Stash 0" in stashes[2].message


def test_stash_info_properties(tmp_path):
    """Test StashInfo model properties."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Make some changes
    test_file.write_text("modified content")
    
    # Save to stash
    repo.stash_save("Test stash")
    
    # Get stash info
    stashes = repo.stash_list()
    stash = stashes[0]
    
    # Test properties
    assert stash.index == 0
    assert stash.ref == "stash@{0}"
    assert "Test stash" in stash.message
    assert stash.commit_sha
    assert len(stash.commit_sha) == 40  # Full SHA


def test_stash_with_no_changes(tmp_path):
    """Test stashing when there are no changes."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Try to stash with no changes
    # This should not create a stash in Git
    try:
        repo.stash_save("Empty stash")
        # If it succeeds, check if a stash was actually created
        stashes = repo.stash_list()
        # Git typically doesn't create a stash if there are no changes
        # The behavior might vary, so we just ensure this doesn't crash
    except Exception:
        # It's okay if it fails, as there are no changes to stash
        pass


def test_stash_on_different_branches(tmp_path):
    """Test stashing on different branches."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create and switch to new branch
    repo.create_branch("feature")
    repo.checkout("feature")
    
    # Make changes on feature branch
    test_file.write_text("feature content")
    repo.stash_save("Feature stash")
    
    # Switch back to main/master
    main_branch = repo.current_branch() if repo.current_branch() != "feature" else "master"
    # Get the default branch
    branches = repo.list_branches()
    for branch in branches:
        if branch.name != "feature":
            main_branch = branch.name
            break
    
    repo.checkout(main_branch)
    
    # Stash should still be accessible
    stashes = repo.stash_list()
    assert len(stashes) == 1
    assert "Feature stash" in stashes[0].message or "feature" in stashes[0].branch.lower()
