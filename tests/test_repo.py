"""
Test suite for repository operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.git.errors import RepoNotFoundError


def test_repo_init(tmp_path):
    """Test repository initialization."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    assert repo is not None
    assert repo.path.exists()
    assert (repo.path / ".git").exists()


def test_repo_open(tmp_path):
    """Test opening an existing repository."""
    # Create a repo first
    repo_path = tmp_path / "test_repo"
    Repo.init(str(repo_path))
    
    # Open it
    repo = Repo.open(str(repo_path))
    assert repo is not None
    assert repo.path == repo_path


def test_repo_open_nonexistent():
    """Test opening a non-existent repository."""
    with pytest.raises(RepoNotFoundError):
        Repo.open("/path/that/does/not/exist")


def test_repo_is_clean(tmp_path):
    """Test checking if repository is clean."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # New repo should be clean
    assert repo.is_clean()


def test_repo_current_branch(tmp_path):
    """Test getting current branch."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Default branch should be 'main' or 'master'
    branch = repo.current_branch()
    assert branch is not None
    # Note: actual branch name depends on Git configuration


def test_repo_create_and_delete_branch(tmp_path):
    """Test creating and deleting a branch."""
    from clevergit.git.errors import BranchError
    
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit so we have something to branch from
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create a new branch
    branch_info = repo.create_branch("feature/test")
    assert branch_info is not None
    assert branch_info.name == "feature/test"
    
    # List branches and verify it exists
    branches = repo.list_branches()
    branch_names = [b.name for b in branches]
    assert "feature/test" in branch_names
    
    # Delete the branch
    repo.delete_branch("feature/test")
    
    # Verify it's deleted
    branches = repo.list_branches()
    branch_names = [b.name for b in branches]
    assert "feature/test" not in branch_names
    
    # Try to delete the current branch - should raise error
    current = repo.current_branch()
    if current:
        with pytest.raises(BranchError):
            repo.delete_branch(current)


def test_repo_commit_files(tmp_path):
    """Test committing specific files."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create multiple files
    file1 = repo.path / "file1.txt"
    file2 = repo.path / "file2.txt"
    file3 = repo.path / "file3.txt"
    
    file1.write_text("content 1")
    file2.write_text("content 2")
    file3.write_text("content 3")
    
    # Commit only file1 and file2
    commit_sha = repo.commit_files(["file1.txt", "file2.txt"], "Add file1 and file2")
    assert commit_sha is not None
    
    # Check status - file3 should still be untracked
    status = repo.status()
    untracked_paths = [f.path for f in status.untracked]
    # Untracked files remain untracked until explicitly added
    assert "file3.txt" in untracked_paths
    
    # Commit the remaining file
    commit_sha2 = repo.commit_files(["file3.txt"], "Add file3")
    assert commit_sha2 is not None
    
    # Now the repo should be clean
    assert repo.is_clean()
