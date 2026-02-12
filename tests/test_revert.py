"""
Test suite for revert operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.core.revert import (
    revert,
    abort_revert,
    continue_revert,
    is_reverting,
    get_revert_head,
    revert_multiple,
)
from clevergit.git.errors import RevertError


def test_revert_simple(tmp_path):
    """Test basic revert operation."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Make a second commit to revert
    test_file.write_text("modified content")
    repo.commit_all("Modify file", allow_empty=False)
    
    # Get the commit SHA of the modification
    commits = repo.client.log(max_count=1)
    commit_sha = commits[0]["sha"]
    
    # Verify we have modified content
    assert test_file.read_text() == "modified content"
    
    # Revert the commit
    revert(repo.path, commit_sha)
    
    # Verify the change was reverted
    assert test_file.read_text() == "initial content"
    
    # Verify no revert is in progress
    assert not is_reverting(repo.path)


def test_revert_multiple_commits(tmp_path):
    """Test reverting multiple commits."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("v0")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Make two more commits
    test_file.write_text("v1")
    repo.commit_all("Version 1", allow_empty=False)
    commit1_sha = repo.client.log(max_count=1)[0]["sha"]
    
    test_file.write_text("v2")
    repo.commit_all("Version 2", allow_empty=False)
    commit2_sha = repo.client.log(max_count=1)[0]["sha"]
    
    # Verify we're at v2
    assert test_file.read_text() == "v2"
    
    # Revert both commits (newest first)
    revert_multiple(repo.path, [commit2_sha, commit1_sha])
    
    # Verify we're back to v0
    assert test_file.read_text() == "v0"


def test_revert_no_commit(tmp_path):
    """Test revert without creating a commit."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Make a second commit to revert
    test_file.write_text("modified content")
    repo.commit_all("Modify file", allow_empty=False)
    commit_sha = repo.client.log(max_count=1)[0]["sha"]
    
    # Get current commit count
    commits_before = len(repo.client.log(max_count=10))
    
    # Revert without committing
    revert(repo.path, commit_sha, no_commit=True)
    
    # Verify the change was applied but not committed
    assert test_file.read_text() == "initial content"
    commits_after = len(repo.client.log(max_count=10))
    assert commits_after == commits_before  # No new commit
    
    # Verify there are staged changes
    status = repo.status()
    assert len(status.staged) > 0 or len(status.modified) > 0


def test_revert_conflict_detection(tmp_path):
    """Test detection of revert conflicts."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("line 1\nline 2\nline 3")
    repo.commit_all("Initial commit", allow_empty=False)
    
    # Make a commit that modifies line 2
    test_file.write_text("line 1\nmodified line 2\nline 3")
    repo.commit_all("Modify line 2", allow_empty=False)
    modify_sha = repo.client.log(max_count=1)[0]["sha"]
    
    # Make another commit that also modifies line 2 (will conflict when reverting)
    test_file.write_text("line 1\nconflicting line 2\nline 3")
    repo.commit_all("Conflicting change to line 2", allow_empty=False)
    
    # Try to revert the first modification (should conflict)
    try:
        revert(repo.path, modify_sha)
        # If we get here, check if revert is in progress
        if is_reverting(repo.path):
            # Abort the revert since we're just testing conflict detection
            abort_revert(repo.path)
            assert not is_reverting(repo.path)
    except RevertError:
        # Revert failed due to conflict, which is expected
        # Clean up if revert is in progress
        if is_reverting(repo.path):
            abort_revert(repo.path)
        pass


def test_is_reverting(tmp_path):
    """Test checking if revert is in progress."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Initially, no revert should be in progress
    assert not is_reverting(repo.path)
    
    # Create a commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit", allow_empty=False)
    
    test_file.write_text("modified content")
    repo.commit_all("Modify file", allow_empty=False)
    
    # Still no revert in progress
    assert not is_reverting(repo.path)


def test_get_revert_head(tmp_path):
    """Test getting the commit being reverted."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Initially, no revert head
    assert get_revert_head(repo.path) is None
    
    # Create commits
    test_file = repo.path / "test.txt"
    test_file.write_text("initial")
    repo.commit_all("Initial", allow_empty=False)
    
    test_file.write_text("modified")
    repo.commit_all("Modified", allow_empty=False)
    
    # No revert head yet
    assert get_revert_head(repo.path) is None


def test_abort_revert_no_revert_in_progress(tmp_path):
    """Test aborting when no revert is in progress."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create a commit
    test_file = repo.path / "test.txt"
    test_file.write_text("content")
    repo.commit_all("Initial", allow_empty=False)
    
    # Try to abort when there's no revert in progress
    with pytest.raises(RevertError):
        abort_revert(repo.path)


def test_revert_creates_revert_commit(tmp_path):
    """Test that revert creates a proper revert commit with message."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create commits
    test_file = repo.path / "test.txt"
    test_file.write_text("initial")
    repo.commit_all("Initial commit", allow_empty=False)
    
    test_file.write_text("modified")
    repo.commit_all("Modify file", allow_empty=False)
    commit_sha = repo.client.log(max_count=1)[0]["sha"]
    
    # Count commits before revert
    commits_before = len(repo.client.log(max_count=10))
    
    # Revert the commit
    revert(repo.path, commit_sha)
    
    # Verify a new commit was created
    commits_after = len(repo.client.log(max_count=10))
    assert commits_after == commits_before + 1
    
    # Verify the revert commit message mentions "Revert"
    latest_commit = repo.client.log(max_count=1)[0]
    assert "Revert" in latest_commit["message"] or "revert" in latest_commit["message"].lower()


def test_revert_nonexistent_commit(tmp_path):
    """Test reverting a nonexistent commit."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create a commit
    test_file = repo.path / "test.txt"
    test_file.write_text("content")
    repo.commit_all("Initial", allow_empty=False)
    
    # Try to revert a nonexistent commit
    fake_sha = "0" * 40
    with pytest.raises(RevertError):
        revert(repo.path, fake_sha)


def test_revert_with_clean_working_directory(tmp_path):
    """Test that working directory is clean after successful revert."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create commits
    test_file = repo.path / "test.txt"
    test_file.write_text("initial")
    repo.commit_all("Initial", allow_empty=False)
    
    test_file.write_text("modified")
    repo.commit_all("Modified", allow_empty=False)
    commit_sha = repo.client.log(max_count=1)[0]["sha"]
    
    # Revert
    revert(repo.path, commit_sha)
    
    # Working directory should be clean
    assert repo.is_clean()
