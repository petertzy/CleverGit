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
