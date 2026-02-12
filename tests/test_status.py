"""
Test suite for status operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.core.status import get_status, has_uncommitted_changes


def test_status_clean_repo(tmp_path):
    """Test status on a clean repository."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    status = get_status(repo.client)
    
    assert not status.has_changes
    assert len(status.modified) == 0
    assert len(status.untracked) == 0


def test_status_with_untracked_file(tmp_path):
    """Test status with an untracked file."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create a new file
    test_file = repo_path / "test.txt"
    test_file.write_text("test content")
    
    status = get_status(repo.client)
    
    assert status.has_changes
    assert len(status.untracked) == 1
    assert status.untracked[0].path == "test.txt"


def test_has_uncommitted_changes(tmp_path):
    """Test checking for uncommitted changes."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Clean repo should have no uncommitted changes
    assert not has_uncommitted_changes(repo.client)
    
    # Add a file
    test_file = repo_path / "test.txt"
    test_file.write_text("test content")
    
    # Now should have uncommitted changes
    assert has_uncommitted_changes(repo.client)
