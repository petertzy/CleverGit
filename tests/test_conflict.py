"""
Test suite for conflict detection and resolution.
"""

import tempfile
from pathlib import Path
import pytest

from clevergit.core.conflict import (
    ConflictBlock,
    ConflictedFile,
    parse_conflict_markers,
    parse_conflicted_file,
    has_conflict_markers,
    resolve_conflict_take_ours,
    resolve_conflict_take_theirs,
    resolve_conflict_take_both,
    apply_resolution,
    resolve_all_conflicts,
)


def test_parse_simple_conflict():
    """Test parsing a simple two-way conflict."""
    content = """line 1
line 2
<<<<<<< HEAD
our change
=======
their change
>>>>>>> feature-branch
line 3
"""
    conflicts = parse_conflict_markers(content)
    
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.start_line == 2
    assert conflict.end_line == 6
    assert conflict.ours_label == "HEAD"
    assert conflict.theirs_label == "feature-branch"
    assert conflict.ours_content == ["our change"]
    assert conflict.theirs_content == ["their change"]
    assert conflict.base_content is None
    assert not conflict.has_base()


def test_parse_diff3_conflict():
    """Test parsing a diff3-style conflict with base."""
    content = """line 1
<<<<<<< HEAD
our change
||||||| base-commit
original line
=======
their change
>>>>>>> feature-branch
line 2
"""
    conflicts = parse_conflict_markers(content)
    
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.start_line == 1
    assert conflict.end_line == 7
    assert conflict.ours_label == "HEAD"
    assert conflict.theirs_label == "feature-branch"
    assert conflict.ours_content == ["our change"]
    assert conflict.theirs_content == ["their change"]
    assert conflict.base_content == ["original line"]
    assert conflict.has_base()


def test_parse_multiple_conflicts():
    """Test parsing multiple conflicts in one file."""
    content = """line 1
<<<<<<< HEAD
first our change
=======
first their change
>>>>>>> branch1
line 2
<<<<<<< HEAD
second our change
=======
second their change
>>>>>>> branch2
line 3
"""
    conflicts = parse_conflict_markers(content)
    
    assert len(conflicts) == 2
    
    assert conflicts[0].ours_label == "HEAD"
    assert conflicts[0].theirs_label == "branch1"
    assert conflicts[0].ours_content == ["first our change"]
    assert conflicts[0].theirs_content == ["first their change"]
    
    assert conflicts[1].ours_label == "HEAD"
    assert conflicts[1].theirs_label == "branch2"
    assert conflicts[1].ours_content == ["second our change"]
    assert conflicts[1].theirs_content == ["second their change"]


def test_parse_multiline_conflict():
    """Test parsing conflict with multiple lines in each section."""
    content = """start
<<<<<<< HEAD
our line 1
our line 2
our line 3
=======
their line 1
their line 2
>>>>>>> feature
end
"""
    conflicts = parse_conflict_markers(content)
    
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict.ours_content == ["our line 1", "our line 2", "our line 3"]
    assert conflict.theirs_content == ["their line 1", "their line 2"]


def test_parse_no_conflicts():
    """Test parsing file with no conflicts."""
    content = """line 1
line 2
line 3
"""
    conflicts = parse_conflict_markers(content)
    assert len(conflicts) == 0


def test_has_conflict_markers():
    """Test detecting presence of conflict markers."""
    assert has_conflict_markers("<<<<<<< HEAD\ntest\n=======\ntest\n>>>>>>> branch")
    assert has_conflict_markers("no conflict\n<<<<<<< HEAD\ntest")
    assert has_conflict_markers("test\n=======\ntest")
    assert has_conflict_markers("test\n>>>>>>> branch")
    assert not has_conflict_markers("normal content\nno markers here")


def test_parse_conflicted_file():
    """Test parsing a real file with conflicts."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("""line 1
<<<<<<< HEAD
our content
=======
their content
>>>>>>> feature
line 2
""")
        temp_path = Path(f.name)
    
    try:
        conflicted_file = parse_conflicted_file(temp_path)
        
        assert conflicted_file.file_path == str(temp_path)
        assert conflicted_file.get_conflict_count() == 1
        assert conflicted_file.has_conflicts()
        assert len(conflicted_file.original_content) > 0
        
        conflict = conflicted_file.conflicts[0]
        assert conflict.ours_content == ["our content"]
        assert conflict.theirs_content == ["their content"]
    finally:
        temp_path.unlink()


def test_parse_conflicted_file_not_found():
    """Test parsing non-existent file raises error."""
    with pytest.raises(FileNotFoundError):
        parse_conflicted_file(Path("/nonexistent/file.txt"))


def test_resolve_conflict_take_ours():
    """Test resolving conflict by taking ours."""
    conflict = ConflictBlock(
        start_line=0,
        end_line=4,
        ours_label="HEAD",
        theirs_label="feature",
        ours_content=["our line 1", "our line 2"],
        theirs_content=["their line 1", "their line 2"]
    )
    
    result = resolve_conflict_take_ours(conflict)
    assert result == ["our line 1", "our line 2"]


def test_resolve_conflict_take_theirs():
    """Test resolving conflict by taking theirs."""
    conflict = ConflictBlock(
        start_line=0,
        end_line=4,
        ours_label="HEAD",
        theirs_label="feature",
        ours_content=["our line 1", "our line 2"],
        theirs_content=["their line 1", "their line 2"]
    )
    
    result = resolve_conflict_take_theirs(conflict)
    assert result == ["their line 1", "their line 2"]


def test_resolve_conflict_take_both_ours_first():
    """Test resolving conflict by taking both (ours first)."""
    conflict = ConflictBlock(
        start_line=0,
        end_line=4,
        ours_label="HEAD",
        theirs_label="feature",
        ours_content=["our line"],
        theirs_content=["their line"]
    )
    
    result = resolve_conflict_take_both(conflict, ours_first=True)
    assert result == ["our line", "their line"]


def test_resolve_conflict_take_both_theirs_first():
    """Test resolving conflict by taking both (theirs first)."""
    conflict = ConflictBlock(
        start_line=0,
        end_line=4,
        ours_label="HEAD",
        theirs_label="feature",
        ours_content=["our line"],
        theirs_content=["their line"]
    )
    
    result = resolve_conflict_take_both(conflict, ours_first=False)
    assert result == ["their line", "our line"]


def test_apply_resolution():
    """Test applying a resolution to a specific conflict."""
    original_content = [
        "line 1",
        "<<<<<<< HEAD",
        "our change",
        "=======",
        "their change",
        ">>>>>>> feature",
        "line 2"
    ]
    
    conflicts = parse_conflict_markers('\n'.join(original_content))
    conflicted_file = ConflictedFile(
        file_path="test.txt",
        conflicts=conflicts,
        original_content=original_content
    )
    
    resolved = apply_resolution(conflicted_file, 0, ["resolved line"])
    expected = "line 1\nresolved line\nline 2"
    assert resolved == expected


def test_apply_resolution_invalid_index():
    """Test applying resolution with invalid index."""
    conflicted_file = ConflictedFile(
        file_path="test.txt",
        conflicts=[],
        original_content=["line 1"]
    )
    
    with pytest.raises(IndexError):
        apply_resolution(conflicted_file, 0, ["resolved"])


def test_resolve_all_conflicts():
    """Test resolving all conflicts in a file."""
    original_content = [
        "line 1",
        "<<<<<<< HEAD",
        "first our",
        "=======",
        "first their",
        ">>>>>>> branch1",
        "line 2",
        "<<<<<<< HEAD",
        "second our",
        "=======",
        "second their",
        ">>>>>>> branch2",
        "line 3"
    ]
    
    conflicts = parse_conflict_markers('\n'.join(original_content))
    conflicted_file = ConflictedFile(
        file_path="test.txt",
        conflicts=conflicts,
        original_content=original_content
    )
    
    resolutions = [
        ["first resolved"],
        ["second resolved"]
    ]
    
    resolved = resolve_all_conflicts(conflicted_file, resolutions)
    expected = "line 1\nfirst resolved\nline 2\nsecond resolved\nline 3"
    assert resolved == expected


def test_resolve_all_conflicts_wrong_count():
    """Test resolving all conflicts with wrong number of resolutions."""
    conflicts = parse_conflict_markers("<<<<<<< HEAD\na\n=======\nb\n>>>>>>> branch")
    conflicted_file = ConflictedFile(
        file_path="test.txt",
        conflicts=conflicts,
        original_content=["line 1"]
    )
    
    with pytest.raises(ValueError):
        resolve_all_conflicts(conflicted_file, [])


def test_conflict_block_methods():
    """Test ConflictBlock helper methods."""
    conflict = ConflictBlock(
        start_line=0,
        end_line=4,
        ours_label="HEAD",
        theirs_label="feature",
        ours_content=["our line 1", "our line 2"],
        theirs_content=["their line 1"],
        base_content=["base line"]
    )
    
    assert conflict.get_ours_text() == "our line 1\nour line 2"
    assert conflict.get_theirs_text() == "their line 1"
    assert conflict.get_base_text() == "base line"
    assert conflict.has_base()


def test_conflict_block_no_base():
    """Test ConflictBlock without base."""
    conflict = ConflictBlock(
        start_line=0,
        end_line=4,
        ours_label="HEAD",
        theirs_label="feature",
        ours_content=["our line"],
        theirs_content=["their line"]
    )
    
    assert conflict.get_base_text() == ""
    assert not conflict.has_base()


def test_conflicted_file_methods():
    """Test ConflictedFile helper methods."""
    conflict1 = ConflictBlock(
        start_line=0,
        end_line=4,
        ours_label="HEAD",
        theirs_label="feature",
        ours_content=["our"],
        theirs_content=["their"]
    )
    conflict2 = ConflictBlock(
        start_line=5,
        end_line=9,
        ours_label="HEAD",
        theirs_label="feature",
        ours_content=["our2"],
        theirs_content=["their2"]
    )
    
    conflicted_file = ConflictedFile(
        file_path="test.txt",
        conflicts=[conflict1, conflict2],
        original_content=[]
    )
    
    assert conflicted_file.get_conflict_count() == 2
    assert conflicted_file.has_conflicts()


def test_empty_conflicted_file():
    """Test ConflictedFile with no conflicts."""
    conflicted_file = ConflictedFile(
        file_path="test.txt",
        conflicts=[],
        original_content=[]
    )
    
    assert conflicted_file.get_conflict_count() == 0
    assert not conflicted_file.has_conflicts()
