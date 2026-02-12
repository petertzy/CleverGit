"""
Test suite for blame operations.
"""

import pytest
from pathlib import Path
from datetime import datetime

from clevergit.core.repo import Repo
from clevergit.core.blame import get_blame, get_blame_for_line, _parse_blame_porcelain
from clevergit.models.blame_info import BlameInfo
from clevergit.git.errors import CleverGitError


def test_blame_single_file(tmp_path):
    """Test blaming a file with a single commit."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("Line 1\nLine 2\nLine 3\n")
    
    commit_info = repo.commit_all("feat: add test file")
    
    # Get blame information
    blame_list = get_blame(repo_path, "test.txt")
    
    assert len(blame_list) == 3
    assert all(b.commit_sha == commit_info.sha for b in blame_list)
    assert blame_list[0].line_number == 1
    assert blame_list[0].content == "Line 1"
    assert blame_list[1].line_number == 2
    assert blame_list[1].content == "Line 2"
    assert blame_list[2].line_number == 3
    assert blame_list[2].content == "Line 3"


def test_blame_multiple_commits(tmp_path):
    """Test blaming a file with multiple commits."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create and commit initial file
    test_file = repo_path / "test.txt"
    test_file.write_text("Line 1\nLine 2\n")
    commit1 = repo.commit_all("feat: initial commit")
    
    # Modify and commit again
    test_file.write_text("Line 1\nLine 2\nLine 3\n")
    commit2 = repo.commit_all("feat: add line 3")
    
    # Get blame information
    blame_list = get_blame(repo_path, "test.txt")
    
    assert len(blame_list) == 3
    # First two lines from commit1
    assert blame_list[0].commit_sha == commit1.sha
    assert blame_list[1].commit_sha == commit1.sha
    # Third line from commit2
    assert blame_list[2].commit_sha == commit2.sha
    assert blame_list[2].content == "Line 3"


def test_blame_for_specific_line(tmp_path):
    """Test getting blame for a specific line."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("Line 1\nLine 2\nLine 3\n")
    commit_info = repo.commit_all("feat: add test file")
    
    # Get blame for line 2
    blame_info = get_blame_for_line(repo_path, "test.txt", 2)
    
    assert blame_info is not None
    assert blame_info.line_number == 2
    assert blame_info.content == "Line 2"
    assert blame_info.commit_sha == commit_info.sha


def test_blame_nonexistent_line(tmp_path):
    """Test getting blame for a nonexistent line."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("Line 1\n")
    repo.commit_all("feat: add test file")
    
    # Get blame for nonexistent line
    blame_info = get_blame_for_line(repo_path, "test.txt", 10)
    
    assert blame_info is None


def test_blame_nonexistent_file(tmp_path):
    """Test blaming a nonexistent file."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Try to blame nonexistent file
    with pytest.raises(CleverGitError):
        get_blame(repo_path, "nonexistent.txt")


def test_blame_info_format():
    """Test BlameInfo formatting methods."""
    blame = BlameInfo(
        line_number=10,
        commit_sha="abc123def456789",
        short_sha="abc123d",
        author="John Doe",
        author_email="john@example.com",
        date=datetime(2024, 1, 15, 10, 30),
        content="    print('hello')",
        summary="Add print statement"
    )
    
    # Test format_oneline
    oneline = blame.format_oneline()
    assert "abc123d" in oneline
    assert "John Doe" in oneline
    assert "2024-01-15" in oneline
    assert "print('hello')" in oneline
    
    # Test __str__
    str_repr = str(blame)
    assert str_repr == oneline


def test_parse_blame_porcelain():
    """Test parsing git blame porcelain output."""
    # Sample porcelain output
    porcelain_output = """abc123def456789 1 1 1
author John Doe
author-mail <john@example.com>
author-time 1705315800
summary First commit
\tLine 1
abc123def456789 2 2
\tLine 2
def456ghi789012 3 3 1
author Jane Smith
author-mail <jane@example.com>
author-time 1705402200
summary Second commit
\tLine 3"""
    
    blame_list = _parse_blame_porcelain(porcelain_output)
    
    assert len(blame_list) == 3
    
    # Check first line
    assert blame_list[0].line_number == 1
    assert blame_list[0].commit_sha == "abc123def456789"
    assert blame_list[0].author == "John Doe"
    assert blame_list[0].author_email == "john@example.com"
    assert blame_list[0].content == "Line 1"
    
    # Check second line (same commit, cached metadata)
    assert blame_list[1].line_number == 2
    assert blame_list[1].commit_sha == "abc123def456789"
    assert blame_list[1].content == "Line 2"
    
    # Check third line (different commit)
    assert blame_list[2].line_number == 3
    assert blame_list[2].commit_sha == "def456ghi789012"
    assert blame_list[2].author == "Jane Smith"
    assert blame_list[2].content == "Line 3"


def test_blame_empty_file(tmp_path):
    """Test blaming an empty file."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create and commit an empty file
    test_file = repo_path / "empty.txt"
    test_file.write_text("")
    repo.commit_all("feat: add empty file")
    
    # Get blame information
    blame_list = get_blame(repo_path, "empty.txt")
    
    # Empty file should have no blame lines
    assert len(blame_list) == 0


def test_blame_with_special_characters(tmp_path):
    """Test blaming a file with special characters."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))
    
    # Create file with special characters
    test_file = repo_path / "special.txt"
    test_file.write_text("Line with tabs\t\there\nLine with quotes: \"hello\"\n")
    commit_info = repo.commit_all("feat: add special file")
    
    # Get blame information
    blame_list = get_blame(repo_path, "special.txt")
    
    assert len(blame_list) == 2
    assert "\t" in blame_list[0].content
    assert "\"hello\"" in blame_list[1].content
