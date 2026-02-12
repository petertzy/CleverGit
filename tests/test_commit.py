"""
Test suite for commit operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.core.commit import commit_all, validate_commit_message
from clevergit.git.errors import NothingToCommitError


def test_commit_validation():
    """Test commit message validation."""
    # Valid message
    assert validate_commit_message("fix: resolve bug")
    
    # Empty message
    with pytest.raises(ValueError):
        validate_commit_message("")
    
    # Too short
    with pytest.raises(ValueError):
        validate_commit_message("ab")


def test_commit_nothing_to_commit(tmp_path):
    """Test committing with no changes."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    with pytest.raises(NothingToCommitError):
        repo.commit_all("test commit")


def test_commit_with_file(tmp_path):
    """Test committing a file."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("test content")
    
    commit_info = repo.commit_all("feat: add test file")
    
    assert commit_info is not None
    assert len(commit_info.sha) > 0
    assert repo.is_clean()


def test_commit_specific_files(tmp_path):
    """Test committing specific files."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create multiple files
    file1 = repo_path / "file1.txt"
    file2 = repo_path / "file2.txt"
    file1.write_text("content 1")
    file2.write_text("content 2")
    
    # Commit only one file
    commit_info = repo.commit_files(["file1.txt"], "feat: add file1")
    
    assert commit_info is not None
    assert len(commit_info.sha) > 0
    
    # file2.txt should still be untracked
    status = repo.status()
    assert len(status.untracked) == 1
    assert status.untracked[0].path == "file2.txt"
