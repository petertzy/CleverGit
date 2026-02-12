"""
Test suite for cherry-pick operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.core.cherry_pick import (
    cherry_pick,
    abort_cherry_pick,
    continue_cherry_pick,
    is_cherry_picking,
    get_cherry_pick_head,
)
from clevergit.git.errors import CherryPickError


def test_cherry_pick_simple(tmp_path):
    """Test basic cherry-pick operation."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit on main branch
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Create a feature branch and make a commit
    repo.create_branch("feature")
    repo.checkout("feature")
    
    test_file.write_text("feature content")
    repo.commit_all("Feature commit", allow_empty=False)
    
    # Get the commit SHA
    feature_commits = repo.client.log(max_count=1)
    feature_sha = feature_commits[0]["sha"]
    
    # Switch back to main
    repo.checkout("master")
    
    # Verify we're on the initial content
    assert test_file.read_text() == "initial content"
    
    # Cherry-pick the feature commit
    cherry_pick(repo.path, feature_sha)
    
    # Verify the change was applied
    assert test_file.read_text() == "feature content"
    
    # Verify no cherry-pick is in progress
    assert not is_cherry_picking(repo.path)


def test_cherry_pick_no_commit(tmp_path):
    """Test cherry-pick with no-commit option."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Create a feature branch and make a commit
    repo.create_branch("feature")
    repo.checkout("feature")
    
    test_file.write_text("feature content")
    repo.commit_all("Feature commit", allow_empty=False)
    
    feature_commits = repo.client.log(max_count=1)
    feature_sha = feature_commits[0]["sha"]
    
    # Switch back to main
    repo.checkout("master")
    
    # Cherry-pick without committing
    cherry_pick(repo.path, feature_sha, no_commit=True)
    
    # Verify the change was applied to working directory
    assert test_file.read_text() == "feature content"
    
    # Verify the changes are staged but not committed
    status = repo.status()
    assert len(status.modified) > 0 or len(status.staged) > 0


def test_cherry_pick_conflict(tmp_path):
    """Test cherry-pick with conflicts."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit on main branch
    test_file = repo.path / "test.txt"
    test_file.write_text("line 1\nline 2\nline 3")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Create a feature branch and modify
    repo.create_branch("feature")
    repo.checkout("feature")
    
    test_file.write_text("line 1\nfeature line\nline 3")
    repo.commit_all("Feature commit", allow_empty=False)
    
    feature_commits = repo.client.log(max_count=1)
    feature_sha = feature_commits[0]["sha"]
    
    # Switch back to main and make conflicting change
    repo.checkout("master")
    test_file.write_text("line 1\nmain line\nline 3")
    repo.commit_all("Main commit", allow_empty=False)
    
    # Try to cherry-pick - should fail with conflict
    with pytest.raises(CherryPickError):
        cherry_pick(repo.path, feature_sha)
    
    # Verify cherry-pick is in progress
    assert is_cherry_picking(repo.path)
    
    # Get the cherry-pick head
    cherry_pick_head = get_cherry_pick_head(repo.path)
    assert cherry_pick_head == feature_sha


def test_abort_cherry_pick(tmp_path):
    """Test aborting a cherry-pick operation."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit on main branch
    test_file = repo.path / "test.txt"
    test_file.write_text("line 1\nline 2\nline 3")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Create a feature branch and modify
    repo.create_branch("feature")
    repo.checkout("feature")
    
    test_file.write_text("line 1\nfeature line\nline 3")
    repo.commit_all("Feature commit", allow_empty=False)
    
    feature_commits = repo.client.log(max_count=1)
    feature_sha = feature_commits[0]["sha"]
    
    # Switch back to main and make conflicting change
    repo.checkout("master")
    test_file.write_text("line 1\nmain line\nline 3")
    repo.commit_all("Main commit", allow_empty=False)
    
    # Store the content before cherry-pick
    content_before = test_file.read_text()
    
    # Try to cherry-pick - should fail with conflict
    with pytest.raises(CherryPickError):
        cherry_pick(repo.path, feature_sha)
    
    # Verify cherry-pick is in progress
    assert is_cherry_picking(repo.path)
    
    # Abort the cherry-pick
    abort_cherry_pick(repo.path)
    
    # Verify cherry-pick is no longer in progress
    assert not is_cherry_picking(repo.path)
    
    # Verify we're back to the original state
    assert test_file.read_text() == content_before


def test_is_cherry_picking_false(tmp_path):
    """Test is_cherry_picking returns False when no cherry-pick is in progress."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Verify no cherry-pick is in progress
    assert not is_cherry_picking(repo.path)
    
    # Verify get_cherry_pick_head returns None
    assert get_cherry_pick_head(repo.path) is None
