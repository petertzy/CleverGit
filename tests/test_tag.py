"""
Test suite for tag operations.
"""

import pytest
from pathlib import Path
from clevergit.core.repo import Repo
from clevergit.git.errors import TagError


def test_create_lightweight_tag(tmp_path):
    """Test creating a lightweight tag."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create a lightweight tag
    tag_info = repo.create_tag("v1.0.0")
    
    assert tag_info.name == "v1.0.0"
    assert tag_info.is_annotated is False
    
    # Verify tag exists in list
    tags = repo.list_tags()
    tag_names = [t.name for t in tags]
    assert "v1.0.0" in tag_names


def test_create_annotated_tag(tmp_path):
    """Test creating an annotated tag."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create an annotated tag
    tag_info = repo.create_annotated_tag("v1.0.0", "Release version 1.0.0")
    
    assert tag_info.name == "v1.0.0"
    assert tag_info.is_annotated is True
    assert tag_info.message is not None
    
    # Verify tag exists in list
    tags = repo.list_tags()
    tag_names = [t.name for t in tags]
    assert "v1.0.0" in tag_names
    
    # Find the tag and check it's annotated
    for tag in tags:
        if tag.name == "v1.0.0":
            assert tag.is_annotated is True
            break


def test_delete_tag(tmp_path):
    """Test deleting a tag."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create a tag
    repo.create_tag("v1.0.0")
    
    # Verify tag exists
    tags = repo.list_tags()
    tag_names = [t.name for t in tags]
    assert "v1.0.0" in tag_names
    
    # Delete the tag
    repo.delete_tag("v1.0.0")
    
    # Verify tag is deleted
    tags = repo.list_tags()
    tag_names = [t.name for t in tags]
    assert "v1.0.0" not in tag_names


def test_delete_nonexistent_tag(tmp_path):
    """Test that deleting a non-existent tag raises an error."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Try to delete a tag that doesn't exist
    with pytest.raises(TagError) as exc_info:
        repo.delete_tag("nonexistent-tag")
    
    assert "does not exist" in str(exc_info.value).lower()


def test_create_duplicate_tag(tmp_path):
    """Test that creating a duplicate tag raises an error."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create a tag
    repo.create_tag("v1.0.0")
    
    # Try to create the same tag again
    with pytest.raises(TagError) as exc_info:
        repo.create_tag("v1.0.0")
    
    assert "already exists" in str(exc_info.value).lower()


def test_list_tags(tmp_path):
    """Test listing tags."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Initially no tags
    tags = repo.list_tags()
    assert len(tags) == 0
    
    # Create multiple tags
    repo.create_tag("v1.0.0")
    repo.create_tag("v1.0.1")
    repo.create_annotated_tag("v2.0.0", "Major release")
    
    # List tags
    tags = repo.list_tags()
    assert len(tags) == 3
    
    tag_names = [t.name for t in tags]
    assert "v1.0.0" in tag_names
    assert "v1.0.1" in tag_names
    assert "v2.0.0" in tag_names
    
    # Check for annotated tag
    annotated_tags = [t for t in tags if t.is_annotated]
    assert len(annotated_tags) == 1
    assert annotated_tags[0].name == "v2.0.0"


def test_create_tag_on_specific_commit(tmp_path):
    """Test creating a tag on a specific commit."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create first commit
    test_file = repo.path / "test.txt"
    test_file.write_text("first content")
    repo.commit_all("First commit", allow_empty=True)
    
    # Get first commit SHA using GitPython directly
    first_commit = repo.client._repo.head.commit.hexsha
    
    # Create second commit
    test_file.write_text("second content")
    repo.commit_all("Second commit", allow_empty=True)
    
    # Create tag on first commit
    tag_info = repo.create_tag("v1.0.0", commit=first_commit)
    
    # Verify tag points to first commit
    assert tag_info.commit_sha == first_commit


def test_invalid_tag_name(tmp_path):
    """Test that invalid tag names raise errors."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Test various invalid tag names
    invalid_names = [
        "",  # empty
        "tag with spaces",  # spaces
        "tag~1",  # tilde
        "tag^1",  # caret
        "tag:1",  # colon
        "tag?1",  # question mark
        ".hidden",  # starts with dot
        "tag.",  # ends with dot
        "tag..name",  # double dots
        "/tag",  # starts with slash
        "tag/",  # ends with slash
    ]
    
    for invalid_name in invalid_names:
        with pytest.raises(TagError) as exc_info:
            repo.create_tag(invalid_name)
        assert "invalid" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()


def test_annotated_tag_without_message(tmp_path):
    """Test that creating annotated tag without message raises error."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Try to create annotated tag without message
    with pytest.raises(TagError) as exc_info:
        repo.create_annotated_tag("v1.0.0", "")
    
    assert "message" in str(exc_info.value).lower()


def test_tag_info_properties(tmp_path):
    """Test TagInfo properties."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create tags
    repo.create_tag("v1.0.0")
    repo.create_annotated_tag("v2.0.0", "Release version 2.0.0")
    
    tags = repo.list_tags()
    
    # Test properties
    for tag in tags:
        assert tag.name
        assert tag.commit_sha
        assert len(tag.short_sha) == 7
        assert tag.format_oneline()
        assert str(tag)
        
        if tag.name == "v1.0.0":
            assert not tag.is_annotated
        elif tag.name == "v2.0.0":
            assert tag.is_annotated


def test_push_tag_without_remote(tmp_path):
    """Test pushing a tag when no remote exists (should fail gracefully)."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create a tag
    repo.create_tag("v1.0.0")
    
    # Try to push tag (should fail because no remote)
    with pytest.raises((IndexError, KeyError)):
        repo.push_tag("v1.0.0")


def test_multiple_tags_on_same_commit(tmp_path):
    """Test creating multiple tags on the same commit."""
    repo = Repo.init(str(tmp_path / "test_repo"))
    
    # Create initial commit
    test_file = repo.path / "test.txt"
    test_file.write_text("test content")
    repo.commit_all("Initial commit", allow_empty=True)
    
    # Create multiple tags on the same commit
    repo.create_tag("v1.0.0")
    repo.create_tag("stable")
    repo.create_annotated_tag("release-1.0", "First stable release")
    
    tags = repo.list_tags()
    assert len(tags) == 3
    
    # All tags should point to the same commit
    commit_shas = [t.commit_sha for t in tags]
    assert len(set(commit_shas)) == 1  # All unique shas should be the same
