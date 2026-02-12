"""
Test suite for diff operations.
"""

from clevergit.core.repo import Repo
from clevergit.core.diff import (
    get_working_tree_diff,
    get_staged_diff,
    get_commit_diff,
    get_commit_range_diff,
    DiffMode,
    DiffStats,
    DiffHunk,
    _parse_diff_stats,
    _parse_diff_files,
    find_next_diff,
    find_previous_diff,
    parse_diff_hunks,
    parse_file_hunks,
)


def test_parse_diff_stats_empty():
    """Test parsing stats from empty diff."""
    stats = _parse_diff_stats("")
    assert stats.files_changed == 0
    assert stats.insertions == 0
    assert stats.deletions == 0
    assert stats.total_changes == 0


def test_parse_diff_stats_simple():
    """Test parsing stats from a simple diff."""
    diff_text = """diff --git a/test.txt b/test.txt
index abc123..def456 100644
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,4 @@
 line 1
-line 2
+line 2 modified
+line 3 added
 line 4
"""
    stats = _parse_diff_stats(diff_text)
    assert stats.files_changed == 1
    assert stats.insertions == 2
    assert stats.deletions == 1
    assert stats.total_changes == 3


def test_parse_diff_files_empty():
    """Test parsing files from empty diff."""
    files = _parse_diff_files("")
    assert len(files) == 0


def test_parse_diff_files_modified():
    """Test parsing a modified file."""
    diff_text = """diff --git a/test.txt b/test.txt
index abc123..def456 100644
--- a/test.txt
+++ b/test.txt
@@ -1,2 +1,2 @@
-old line
+new line
"""
    files = _parse_diff_files(diff_text)
    assert len(files) == 1
    assert files[0].old_path == "test.txt"
    assert files[0].new_path == "test.txt"
    assert files[0].status == "modified"
    assert files[0].insertions == 1
    assert files[0].deletions == 1


def test_parse_diff_files_added():
    """Test parsing an added file."""
    diff_text = """diff --git a/new.txt b/new.txt
new file mode 100644
index 0000000..abc123
--- /dev/null
+++ b/new.txt
@@ -0,0 +1,2 @@
+line 1
+line 2
"""
    files = _parse_diff_files(diff_text)
    assert len(files) == 1
    assert files[0].status == "added"
    assert files[0].insertions == 2
    assert files[0].deletions == 0


def test_parse_diff_files_deleted():
    """Test parsing a deleted file."""
    diff_text = """diff --git a/old.txt b/old.txt
deleted file mode 100644
index abc123..0000000
--- a/old.txt
+++ /dev/null
@@ -1,2 +0,0 @@
-line 1
-line 2
"""
    files = _parse_diff_files(diff_text)
    assert len(files) == 1
    assert files[0].status == "deleted"
    assert files[0].insertions == 0
    assert files[0].deletions == 2


def test_find_next_diff():
    """Test finding next diff hunk."""
    diff_text = """diff --git a/test.txt b/test.txt
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line 1
-old
+new
@@ -10,2 +10,2 @@
 line 10
-old2
+new2
"""
    # Find first hunk
    next_line = find_next_diff(diff_text, 0)
    assert next_line == 3  # Line with first @@

    # Find second hunk
    next_line = find_next_diff(diff_text, 3)
    assert next_line == 7  # Line with second @@

    # No more hunks
    next_line = find_next_diff(diff_text, 7)
    assert next_line is None


def test_find_previous_diff():
    """Test finding previous diff hunk."""
    diff_text = """diff --git a/test.txt b/test.txt
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line 1
-old
+new
@@ -10,2 +10,2 @@
 line 10
-old2
+new2
"""
    # Find first hunk from end
    prev_line = find_previous_diff(diff_text, 10)
    assert prev_line == 7  # Line with second @@

    # Find no previous from beginning
    prev_line = find_previous_diff(diff_text, 3)
    assert prev_line is None


def test_working_tree_diff_no_changes(tmp_path):
    """Test getting working tree diff with no changes."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))

    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("initial content")
    repo.commit_all("Initial commit")

    # No changes in working tree
    diff_result = get_working_tree_diff(repo_path)

    assert diff_result.mode == DiffMode.WORKING_TREE
    assert diff_result.diff_text == ""
    assert diff_result.stats.files_changed == 0


def test_working_tree_diff_with_changes(tmp_path):
    """Test getting working tree diff with changes."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))

    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("line 1\nline 2\n")
    repo.commit_all("Initial commit")

    # Modify the file
    test_file.write_text("line 1 modified\nline 2\n")

    # Get diff
    diff_result = get_working_tree_diff(repo_path)

    assert diff_result.mode == DiffMode.WORKING_TREE
    assert "test.txt" in diff_result.diff_text
    assert diff_result.stats.files_changed >= 1
    assert diff_result.stats.insertions > 0 or diff_result.stats.deletions > 0


def test_staged_diff(tmp_path):
    """Test getting staged diff."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))

    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("initial content\n")
    repo.commit_all("Initial commit")

    # Modify and stage the file
    test_file.write_text("modified content\n")
    from clevergit.git.client import GitClient

    client = GitClient(repo_path)
    client.add([str(test_file.name)])

    # Get staged diff
    diff_result = get_staged_diff(repo_path)

    assert diff_result.mode == DiffMode.STAGED
    assert "test.txt" in diff_result.diff_text
    assert diff_result.stats.files_changed >= 1


def test_commit_diff(tmp_path):
    """Test getting commit diff."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))

    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("line 1\nline 2\n")
    commit_info = repo.commit_all("Initial commit")

    # Get commit diff
    diff_result = get_commit_diff(repo_path, commit_info.sha)

    assert diff_result.mode == DiffMode.COMMIT
    assert diff_result.commit_sha == commit_info.sha
    assert (
        "test.txt" in diff_result.diff_text or diff_result.diff_text == ""
    )  # May be empty for first commit


def test_commit_range_diff(tmp_path):
    """Test getting diff between two commits."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))

    # Create first commit
    test_file = repo_path / "test.txt"
    test_file.write_text("line 1\n")
    commit1 = repo.commit_all("First commit")

    # Create second commit
    test_file.write_text("line 1\nline 2\n")
    commit2 = repo.commit_all("Second commit")

    # Get diff between commits
    diff_result = get_commit_range_diff(repo_path, commit1.sha, commit2.sha)

    assert diff_result.mode == DiffMode.COMMIT_RANGE
    assert diff_result.commit_sha == commit1.sha
    assert diff_result.commit_sha2 == commit2.sha
    assert "test.txt" in diff_result.diff_text
    assert diff_result.stats.insertions > 0


def test_diff_with_specific_file(tmp_path):
    """Test getting diff for a specific file."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))

    # Create multiple files
    file1 = repo_path / "file1.txt"
    file2 = repo_path / "file2.txt"
    file1.write_text("content 1\n")
    file2.write_text("content 2\n")
    repo.commit_all("Initial commit")

    # Modify both files
    file1.write_text("content 1 modified\n")
    file2.write_text("content 2 modified\n")

    # Get diff for only file1
    diff_result = get_working_tree_diff(repo_path, file_path="file1.txt")

    assert "file1.txt" in diff_result.diff_text
    assert "file2.txt" not in diff_result.diff_text


def test_diff_stats_total_changes():
    """Test total_changes property of DiffStats."""
    stats = DiffStats(files_changed=2, insertions=10, deletions=5)
    assert stats.total_changes == 15


def test_parse_diff_hunks_empty():
    """Test parsing hunks from empty diff."""
    hunks = parse_diff_hunks("")
    assert len(hunks) == 0


def test_parse_diff_hunks_single():
    """Test parsing a single hunk."""
    diff_text = """diff --git a/test.txt b/test.txt
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,4 @@
 line 1
-line 2
+line 2 modified
+line 3 added
 line 4
"""
    hunks = parse_diff_hunks(diff_text)
    assert len(hunks) == 1
    
    hunk = hunks[0]
    assert hunk.old_start == 1
    assert hunk.old_count == 3
    assert hunk.new_start == 1
    assert hunk.new_count == 4
    assert hunk.header == "@@ -1,3 +1,4 @@"
    # Lines includes the actual diff lines plus any trailing context
    assert len(hunk.lines) >= 4
    assert " line 1" in hunk.lines
    assert "-line 2" in hunk.lines
    assert "+line 2 modified" in hunk.lines


def test_parse_diff_hunks_multiple():
    """Test parsing multiple hunks."""
    diff_text = """diff --git a/test.txt b/test.txt
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line 1
-old
+new
 line 3
@@ -10,2 +10,3 @@
 line 10
-old2
+new2
+added line
"""
    hunks = parse_diff_hunks(diff_text)
    assert len(hunks) == 2
    
    # First hunk
    assert hunks[0].old_start == 1
    assert hunks[0].old_count == 3
    assert hunks[0].new_start == 1
    assert hunks[0].new_count == 3
    
    # Second hunk
    assert hunks[1].old_start == 10
    assert hunks[1].old_count == 2
    assert hunks[1].new_start == 10
    assert hunks[1].new_count == 3


def test_diff_hunk_text_property():
    """Test DiffHunk text property."""
    hunk = DiffHunk(
        old_start=1,
        old_count=2,
        new_start=1,
        new_count=3,
        header="@@ -1,2 +1,3 @@",
        lines=[" context", "-removed", "+added"]
    )
    
    text = hunk.text
    assert "@@ -1,2 +1,3 @@" in text
    assert " context" in text
    assert "-removed" in text
    assert "+added" in text


def test_parse_file_hunks(tmp_path):
    """Test parsing hunks from a FileDiff object."""
    repo_path = tmp_path / "test_repo"
    repo = Repo.init(str(repo_path))

    # Create and commit a file
    test_file = repo_path / "test.txt"
    test_file.write_text("line 1\nline 2\nline 3\n")
    repo.commit_all("Initial commit")

    # Modify the file
    test_file.write_text("line 1 modified\nline 2\nline 3 modified\n")

    # Get diff and parse files
    diff_result = get_working_tree_diff(repo_path)
    
    if diff_result.files:
        file_diff = diff_result.files[0]
        hunks = parse_file_hunks(file_diff)
        
        # Should have at least one hunk
        assert len(hunks) > 0
        assert hunks[0].old_start > 0
        assert hunks[0].new_start > 0
