"""
Test suite for reset operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.core.commit import (
    soft_reset, mixed_reset, hard_reset, get_reflog
)
from clevergit.git.errors import ResetError


def test_soft_reset(tmp_path):
    """Test soft reset functionality."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create first commit
    file1 = repo_path / "file1.txt"
    file1.write_text("content 1")
    commit_info1 = repo.commit_all("feat: add file1")
    sha1 = commit_info1.sha
    
    # Create second commit
    file2 = repo_path / "file2.txt"
    file2.write_text("content 2")
    commit_info2 = repo.commit_all("feat: add file2")
    
    # Soft reset to first commit
    soft_reset(repo.client, sha1)
    
    # Verify: HEAD should be at sha1, but file2.txt should be staged
    commits = repo.client.log(max_count=1)
    assert commits[0]['sha'] == sha1
    
    # file2.txt should still exist
    assert file2.exists()


def test_mixed_reset(tmp_path):
    """Test mixed reset functionality."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create first commit
    file1 = repo_path / "file1.txt"
    file1.write_text("content 1")
    commit_info1 = repo.commit_all("feat: add file1")
    sha1 = commit_info1.sha
    
    # Create second commit
    file2 = repo_path / "file2.txt"
    file2.write_text("content 2")
    commit_info2 = repo.commit_all("feat: add file2")
    
    # Mixed reset to first commit
    mixed_reset(repo.client, sha1)
    
    # Verify: HEAD should be at sha1
    commits = repo.client.log(max_count=1)
    assert commits[0]['sha'] == sha1
    
    # file2.txt should still exist as untracked
    assert file2.exists()
    
    # Check status - file2 should be untracked
    status = repo.status()
    assert len(status.untracked) > 0


def test_hard_reset(tmp_path):
    """Test hard reset functionality."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create first commit
    file1 = repo_path / "file1.txt"
    file1.write_text("content 1")
    commit_info1 = repo.commit_all("feat: add file1")
    sha1 = commit_info1.sha
    
    # Create second commit
    file2 = repo_path / "file2.txt"
    file2.write_text("content 2")
    commit_info2 = repo.commit_all("feat: add file2")
    
    # Hard reset to first commit
    hard_reset(repo.client, sha1)
    
    # Verify: HEAD should be at sha1
    commits = repo.client.log(max_count=1)
    assert commits[0]['sha'] == sha1
    
    # file2.txt should be deleted
    assert not file2.exists()
    
    # Working directory should be clean
    assert repo.is_clean()


def test_reset_to_head(tmp_path):
    """Test reset to HEAD (should be no-op)."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create a commit
    file1 = repo_path / "file1.txt"
    file1.write_text("content 1")
    commit_info1 = repo.commit_all("feat: add file1")
    
    # Modify file without committing
    file1.write_text("modified content")
    
    # Soft reset to HEAD (no-op for HEAD position)
    soft_reset(repo.client, "HEAD")
    
    # File should still be modified
    assert file1.read_text() == "modified content"


def test_reset_with_invalid_target(tmp_path):
    """Test reset with invalid target."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create a commit
    file1 = repo_path / "file1.txt"
    file1.write_text("content 1")
    repo.commit_all("feat: add file1")
    
    # Try to reset to non-existent commit
    with pytest.raises(ResetError):
        soft_reset(repo.client, "invalid_sha")


def test_reflog(tmp_path):
    """Test reflog functionality."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create commits
    file1 = repo_path / "file1.txt"
    file1.write_text("content 1")
    commit_info1 = repo.commit_all("feat: add file1")
    
    file2 = repo_path / "file2.txt"
    file2.write_text("content 2")
    commit_info2 = repo.commit_all("feat: add file2")
    
    # Get reflog
    reflog_entries = get_reflog(repo.client, max_count=10)
    
    # Should have reflog entries
    assert len(reflog_entries) > 0
    
    # Each entry should have required fields
    for entry in reflog_entries:
        assert 'sha' in entry
        assert 'message' in entry
        assert 'selector' in entry
        assert len(entry['sha']) == 40  # Full SHA


def test_reset_preserves_untracked_files(tmp_path):
    """Test that reset preserves untracked files."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create first commit
    file1 = repo_path / "file1.txt"
    file1.write_text("content 1")
    commit_info1 = repo.commit_all("feat: add file1")
    sha1 = commit_info1.sha
    
    # Create second commit
    file2 = repo_path / "file2.txt"
    file2.write_text("content 2")
    commit_info2 = repo.commit_all("feat: add file2")
    
    # Create untracked file
    untracked_file = repo_path / "untracked.txt"
    untracked_file.write_text("untracked content")
    
    # Soft reset to first commit
    soft_reset(repo.client, sha1)
    
    # Untracked file should still exist
    assert untracked_file.exists()
    assert untracked_file.read_text() == "untracked content"


def test_reset_multiple_commits_back(tmp_path):
    """Test resetting multiple commits back."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create multiple commits
    file1 = repo_path / "file1.txt"
    file1.write_text("content 1")
    commit_info1 = repo.commit_all("commit 1")
    sha1 = commit_info1.sha
    
    file2 = repo_path / "file2.txt"
    file2.write_text("content 2")
    commit_info2 = repo.commit_all("commit 2")
    
    file3 = repo_path / "file3.txt"
    file3.write_text("content 3")
    commit_info3 = repo.commit_all("commit 3")
    
    # Reset back to first commit
    mixed_reset(repo.client, sha1)
    
    # Verify we're at sha1
    commits = repo.client.log(max_count=1)
    assert commits[0]['sha'] == sha1


def test_reflog_max_count(tmp_path):
    """Test reflog with max_count parameter."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create several commits
    for i in range(5):
        file = repo_path / f"file{i}.txt"
        file.write_text(f"content {i}")
        repo.commit_all(f"commit {i}")
    
    # Get limited reflog entries
    reflog_entries = get_reflog(repo.client, max_count=3)
    
    # Should have at most 3 entries
    assert len(reflog_entries) <= 3
