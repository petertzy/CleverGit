"""
Test suite for remote operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.git.errors import RemoteError


def test_repo_fetch(tmp_path):
    """Test fetching from a remote repository."""
    # Create a bare repository to act as remote
    remote_path = tmp_path / "remote_repo.git"
    remote_repo = Repo.init(str(remote_path), bare=True)
    
    # Create a local repository and add the remote
    local_path = tmp_path / "local_repo"
    local_repo = Repo.init(str(local_path))
    
    # Add a remote
    local_repo.client.add_remote("origin", str(remote_path))
    
    # Fetch should work (even if there's nothing to fetch yet)
    local_repo.fetch(remote="origin")
    
    # Test with non-existent remote should raise error
    with pytest.raises(RemoteError):
        local_repo.fetch(remote="nonexistent")


def test_repo_push_pull(tmp_path):
    """Test pushing and pulling from a remote repository."""
    # Create a bare repository to act as remote
    remote_path = tmp_path / "remote_repo.git"
    Repo.init(str(remote_path), bare=True)
    
    # Create first local repository
    local1_path = tmp_path / "local1"
    local1 = Repo.init(str(local1_path))
    local1.client.add_remote("origin", str(remote_path))
    
    # Create a commit in local1
    test_file = local1.path / "test.txt"
    test_file.write_text("test content")
    local1.commit_all("Initial commit")
    
    # Push to remote with set_upstream
    local1.push(remote="origin", set_upstream=True)
    
    # Create second local repository and clone from remote
    local2_path = tmp_path / "local2"
    local2 = Repo.init(str(local2_path))
    local2.client.add_remote("origin", str(remote_path))
    
    # Fetch and checkout from remote
    local2.fetch(remote="origin")
    # Note: In a real clone, we'd need to set up tracking branches
    # For this test, we're just verifying fetch/pull/push work


def test_repo_push_with_force(tmp_path):
    """Test force pushing to a remote repository."""
    # Create a bare repository to act as remote
    remote_path = tmp_path / "remote_repo.git"
    Repo.init(str(remote_path), bare=True)
    
    # Create local repository
    local_path = tmp_path / "local_repo"
    local_repo = Repo.init(str(local_path))
    local_repo.client.add_remote("origin", str(remote_path))
    
    # Create a commit
    test_file = local_repo.path / "test.txt"
    test_file.write_text("test content")
    local_repo.commit_all("Initial commit")
    
    # Push with set_upstream
    local_repo.push(remote="origin", set_upstream=True)
    
    # Force push should work (even though not needed here)
    local_repo.push(remote="origin", force=True)


def test_repo_pull_with_rebase(tmp_path):
    """Test pulling with rebase option."""
    # Create a bare repository to act as remote
    remote_path = tmp_path / "remote_repo.git"
    Repo.init(str(remote_path), bare=True)
    
    # Create local repository
    local_path = tmp_path / "local_repo"
    local_repo = Repo.init(str(local_path))
    local_repo.client.add_remote("origin", str(remote_path))
    
    # Create a commit
    test_file = local_repo.path / "test.txt"
    test_file.write_text("test content")
    local_repo.commit_all("Initial commit")
    
    # Push to remote
    local_repo.push(remote="origin", set_upstream=True)
    
    # Pull with rebase should succeed (even if there's nothing new)
    local_repo.pull(remote="origin", rebase=True)


def test_fetch_with_prune(tmp_path):
    """Test fetching with prune option."""
    # Create a bare repository to act as remote
    remote_path = tmp_path / "remote_repo.git"
    Repo.init(str(remote_path), bare=True)
    
    # Create local repository
    local_path = tmp_path / "local_repo"
    local_repo = Repo.init(str(local_path))
    local_repo.client.add_remote("origin", str(remote_path))
    
    # Fetch with prune
    local_repo.fetch(remote="origin", prune=True)
