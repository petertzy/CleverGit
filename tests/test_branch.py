"""
Test suite for branch operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.git.errors import BranchError


def test_delete_branch_with_refs_prefix(tmp_path):
    """Test deleting a branch with refs/heads/ prefix."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create a branch
    repo.create_branch("test-branch")
    
    # Delete using refs/heads/ prefix
    repo.delete_branch("refs/heads/test-branch")
    
    # Verify it's deleted
    branches = repo.list_branches()
    branch_names = [b.name for b in branches]
    assert "test-branch" not in branch_names


def test_delete_branch_with_slash_in_name(tmp_path):
    """Test deleting a local branch with slashes in the name."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create branches with slashes
    test_branches = ["feature/login", "bugfix/issue-123", "release/v1.0"]
    
    for branch_name in test_branches:
        repo.create_branch(branch_name)
    
    # Verify they exist
    branches = repo.list_branches()
    branch_names = [b.name for b in branches]
    for branch_name in test_branches:
        assert branch_name in branch_names
    
    # Delete them
    for branch_name in test_branches:
        repo.delete_branch(branch_name)
    
    # Verify they're deleted
    branches = repo.list_branches()
    branch_names = [b.name for b in branches]
    for branch_name in test_branches:
        assert branch_name not in branch_names


def test_delete_remote_tracking_branch_fails(tmp_path):
    """Test that deleting a remote tracking branch raises an error."""
    # Create a repo with a remote
    origin_path = tmp_path / "origin"
    origin_repo = Repo.init(str(origin_path))
    
    # Create initial commit in origin
    test_file = origin_repo.path / "test.txt"
    test_file.write_text("test content")
    origin_repo.commit_all("Initial commit", allow_empty=True)
    
    # Clone the repo
    import subprocess
    clone_path = tmp_path / "clone"
    subprocess.run(["git", "clone", str(origin_path), str(clone_path)], 
                   check=True, capture_output=True)
    
    # Open the cloned repo
    cloned_repo = Repo.open(str(clone_path))
    
    # Try to delete the remote tracking branch
    with pytest.raises(BranchError) as exc_info:
        cloned_repo.delete_branch("origin/master")
    
    assert "remote tracking branch" in str(exc_info.value).lower()


def test_list_branches_with_remote(tmp_path):
    """Test listing branches includes remote branches correctly."""
    # Create a repo with a remote
    origin_path = tmp_path / "origin"
    origin_repo = Repo.init(str(origin_path))
    
    # Create initial commit in origin
    test_file = origin_repo.path / "test.txt"
    test_file.write_text("test content")
    origin_repo.commit_all("Initial commit", allow_empty=True)
    
    # Create a branch in origin
    origin_repo.create_branch("feature-branch")
    
    # Clone the repo
    import subprocess
    clone_path = tmp_path / "clone"
    subprocess.run(["git", "clone", str(origin_path), str(clone_path)], 
                   check=True, capture_output=True)
    
    # Open the cloned repo
    cloned_repo = Repo.open(str(clone_path))
    
    # List all branches including remote
    branches = cloned_repo.list_branches(remote=True)
    
    # Should have local master and remote origin/master
    branch_names = [b.name for b in branches]
    local_branches = [b.name for b in branches if not b.is_remote]
    remote_branches = [b.name for b in branches if b.is_remote]
    
    # Check we have at least one local and one remote branch
    assert len(local_branches) > 0
    assert len(remote_branches) > 0
    
    # Remote branches should not include origin/HEAD
    for branch in remote_branches:
        assert not branch.endswith('/HEAD')


def test_delete_nonexistent_branch(tmp_path):
    """Test that deleting a non-existent branch raises an appropriate error."""
    from git.exc import GitCommandError
    
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Try to delete a branch that doesn't exist
    with pytest.raises(GitCommandError):
        repo.delete_branch("nonexistent-branch")


def test_delete_current_branch_fails(tmp_path):
    """Test that deleting the current branch raises an error."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    current_branch = repo.current_branch()
    
    # Try to delete current branch
    with pytest.raises(BranchError) as exc_info:
        repo.delete_branch(current_branch)
    
    assert "current branch" in str(exc_info.value).lower()


def test_compare_branches_basic(tmp_path):
    """Test basic branch comparison."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit on master
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit")
    
    # Create a feature branch
    repo.create_branch("feature")
    
    # Switch to feature and add a commit
    repo.checkout("feature")
    test_file.write_text("feature content")
    repo.commit_all("Feature commit")
    
    # Compare feature with master
    comparison = repo.compare_branches("master", "feature")
    
    assert comparison.base_branch == "master"
    assert comparison.compare_branch == "feature"
    assert comparison.ahead_count == 1  # feature is 1 commit ahead
    assert comparison.behind_count == 0  # feature is not behind
    assert len(comparison.ahead_commits) == 1
    assert len(comparison.behind_commits) == 0


def test_compare_branches_ahead_and_behind(tmp_path):
    """Test branch comparison when branches have diverged."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit on master
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit")
    
    # Create a feature branch
    repo.create_branch("feature")
    
    # Add commit to master
    test_file.write_text("master content")
    repo.commit_all("Master commit")
    
    # Switch to feature and add a commit
    repo.checkout("feature")
    test_file2 = repo.path / "feature.txt"
    test_file2.write_text("feature content")
    repo.commit_all("Feature commit")
    
    # Compare feature with master
    comparison = repo.compare_branches("master", "feature")
    
    assert comparison.ahead_count == 1  # feature is 1 commit ahead
    assert comparison.behind_count == 1  # feature is 1 commit behind
    assert len(comparison.ahead_commits) == 1
    assert len(comparison.behind_commits) == 1
    assert not comparison.is_up_to_date


def test_compare_branches_up_to_date(tmp_path):
    """Test branch comparison when branches are up to date."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit on master
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit")
    
    # Create a feature branch pointing to the same commit
    repo.create_branch("feature")
    
    # Compare feature with master
    comparison = repo.compare_branches("master", "feature")
    
    assert comparison.ahead_count == 0
    assert comparison.behind_count == 0
    assert comparison.is_up_to_date
    assert len(comparison.different_files) == 0


def test_compare_branches_different_files(tmp_path):
    """Test that branch comparison identifies different files."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit on master
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit")
    
    # Create a feature branch
    repo.create_branch("feature")
    repo.checkout("feature")
    
    # Modify existing file and add new file
    test_file.write_text("modified content")
    new_file = repo.path / "new.txt"
    new_file.write_text("new content")
    repo.commit_all("Feature changes")
    
    # Compare feature with master
    comparison = repo.compare_branches("master", "feature")
    
    assert len(comparison.different_files) >= 1
    assert "test.txt" in comparison.different_files or "new.txt" in comparison.different_files


def test_compare_branches_nonexistent(tmp_path):
    """Test that comparing with nonexistent branches raises an error."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit")
    
    # Try to compare with a nonexistent branch
    with pytest.raises(BranchError) as exc_info:
        repo.compare_branches("master", "nonexistent")
    
    assert "not found" in str(exc_info.value).lower()


def test_compare_branches_summary(tmp_path):
    """Test branch comparison summary generation."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit on master
    test_file = repo.path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit")
    
    # Create and switch to feature branch
    repo.create_branch("feature")
    repo.checkout("feature")
    
    # Add multiple commits to feature
    test_file.write_text("content 1")
    repo.commit_all("Feature commit 1")
    test_file.write_text("content 2")
    repo.commit_all("Feature commit 2")
    
    # Compare feature with master
    comparison = repo.compare_branches("master", "feature")
    
    summary = comparison.summary()
    assert "feature" in summary
    assert "master" in summary
    assert "2" in summary  # Should mention 2 commits
    assert "ahead" in summary

