"""Diff computation and analysis."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from enum import Enum
import re

from clevergit.git.client import GitClient
from clevergit.git.errors import CleverGitError


class DiffMode(Enum):
    """Diff comparison modes."""

    WORKING_TREE = "working_tree"  # Working tree vs HEAD
    STAGED = "staged"  # Staged changes vs HEAD
    COMMIT = "commit"  # Commit vs parent(s)
    COMMIT_RANGE = "commit_range"  # Between two commits


@dataclass
class DiffStats:
    """Statistics about a diff."""

    files_changed: int
    insertions: int
    deletions: int

    @property
    def total_changes(self) -> int:
        """Total number of line changes."""
        return self.insertions + self.deletions


@dataclass
class DiffHunk:
    """Represents a single diff hunk."""

    old_start: int  # Starting line number in old file
    old_count: int  # Number of lines in old file
    new_start: int  # Starting line number in new file
    new_count: int  # Number of lines in new file
    header: str  # The @@ header line
    lines: List[str]  # The actual diff lines (including +, -, and context)

    @property
    def text(self) -> str:
        """Get the full text of the hunk including header."""
        return self.header + "\n" + "\n".join(self.lines)


@dataclass
class FileDiff:
    """Represents a file difference."""

    old_path: str
    new_path: str
    status: str  # 'added', 'deleted', 'modified', 'renamed'
    diff_text: str
    insertions: int = 0
    deletions: int = 0
    hunks: List[DiffHunk] = field(default_factory=list)  # Parsed hunks


@dataclass
class DiffResult:
    """Complete diff result."""

    mode: DiffMode
    diff_text: str
    stats: DiffStats
    files: List[FileDiff]
    commit_sha: Optional[str] = None
    commit_sha2: Optional[str] = None


def get_working_tree_diff(repo_path: Path, file_path: Optional[str] = None) -> DiffResult:
    """
    Get differences between working tree and HEAD.

    Args:
        repo_path: Path to the repository
        file_path: Optional specific file to diff

    Returns:
        DiffResult object containing diff information

    Raises:
        CleverGitError: If getting diff fails
    """
    client = GitClient(repo_path)

    try:
        # Get diff between working tree and HEAD
        diff_text = client.diff(commit1="HEAD", file_path=file_path)

        # Parse stats and file information
        stats = _parse_diff_stats(diff_text)
        files = _parse_diff_files(diff_text)

        return DiffResult(mode=DiffMode.WORKING_TREE, diff_text=diff_text, stats=stats, files=files)
    except Exception as e:
        raise CleverGitError(f"Failed to get working tree diff: {e}")


def get_staged_diff(repo_path: Path, file_path: Optional[str] = None) -> DiffResult:
    """
    Get differences between staging area and HEAD.

    Args:
        repo_path: Path to the repository
        file_path: Optional specific file to diff

    Returns:
        DiffResult object containing diff information

    Raises:
        CleverGitError: If getting diff fails
    """
    client = GitClient(repo_path)

    try:
        # Get diff between staged changes and HEAD
        # Using --cached flag with git diff
        cmd = ["git", "diff", "--cached"]
        if file_path:
            cmd.extend(["--", file_path])

        diff_text = client._run_command(cmd)

        # Parse stats and file information
        stats = _parse_diff_stats(diff_text)
        files = _parse_diff_files(diff_text)

        return DiffResult(mode=DiffMode.STAGED, diff_text=diff_text, stats=stats, files=files)
    except Exception as e:
        raise CleverGitError(f"Failed to get staged diff: {e}")


def get_commit_diff(
    repo_path: Path, commit_sha: str, file_path: Optional[str] = None
) -> DiffResult:
    """
    Get differences introduced by a specific commit.

    Args:
        repo_path: Path to the repository
        commit_sha: SHA of the commit
        file_path: Optional specific file to diff

    Returns:
        DiffResult object containing diff information

    Raises:
        CleverGitError: If getting diff fails
    """
    client = GitClient(repo_path)

    try:
        # Get diff for a specific commit (commit vs parent)
        cmd = ["git", "show", "--format=", commit_sha]
        if file_path:
            cmd.extend(["--", file_path])

        diff_text = client._run_command(cmd)

        # Parse stats and file information
        stats = _parse_diff_stats(diff_text)
        files = _parse_diff_files(diff_text)

        return DiffResult(
            mode=DiffMode.COMMIT,
            diff_text=diff_text,
            stats=stats,
            files=files,
            commit_sha=commit_sha,
        )
    except Exception as e:
        raise CleverGitError(f"Failed to get commit diff: {e}")


def get_commit_range_diff(
    repo_path: Path, commit_sha1: str, commit_sha2: str, file_path: Optional[str] = None
) -> DiffResult:
    """
    Get differences between two commits.

    Args:
        repo_path: Path to the repository
        commit_sha1: SHA of the first commit
        commit_sha2: SHA of the second commit
        file_path: Optional specific file to diff

    Returns:
        DiffResult object containing diff information

    Raises:
        CleverGitError: If getting diff fails
    """
    client = GitClient(repo_path)

    try:
        # Get diff between two commits
        diff_text = client.diff(commit1=commit_sha1, commit2=commit_sha2, file_path=file_path)

        # Parse stats and file information
        stats = _parse_diff_stats(diff_text)
        files = _parse_diff_files(diff_text)

        return DiffResult(
            mode=DiffMode.COMMIT_RANGE,
            diff_text=diff_text,
            stats=stats,
            files=files,
            commit_sha=commit_sha1,
            commit_sha2=commit_sha2,
        )
    except Exception as e:
        raise CleverGitError(f"Failed to get diff between commits: {e}")


def _parse_diff_stats(diff_text: str) -> DiffStats:
    """
    Parse diff text to extract statistics.

    Args:
        diff_text: Raw diff output

    Returns:
        DiffStats object with file counts and line changes
    """
    if not diff_text:
        return DiffStats(files_changed=0, insertions=0, deletions=0)

    files_changed = 0
    insertions = 0
    deletions = 0

    # Count files changed by looking for diff --git lines
    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            files_changed += 1
        elif line.startswith("+") and not line.startswith("+++"):
            insertions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1

    return DiffStats(files_changed=files_changed, insertions=insertions, deletions=deletions)


def _parse_diff_files(diff_text: str) -> List[FileDiff]:
    """
    Parse diff text to extract per-file information.

    Args:
        diff_text: Raw diff output

    Returns:
        List of FileDiff objects
    """
    if not diff_text:
        return []

    files = []
    current_file = None
    current_diff = []
    insertions = 0
    deletions = 0

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            # Save previous file if exists
            if current_file:
                files.append(
                    FileDiff(
                        old_path=current_file[0],
                        new_path=current_file[1],
                        status=current_file[2],
                        diff_text="\n".join(current_diff),
                        insertions=insertions,
                        deletions=deletions,
                    )
                )

            # Parse new file header
            # Format: diff --git a/path b/path
            parts = line.split(" ")
            if len(parts) >= 4:
                old_path = parts[2][2:]  # Remove a/ prefix
                new_path = parts[3][2:]  # Remove b/ prefix
                current_file = [old_path, new_path, "modified"]
                current_diff = [line]
                insertions = 0
                deletions = 0
        elif current_file:
            current_diff.append(line)

            # Detect file status from headers
            if line.startswith("new file mode"):
                current_file[2] = "added"
            elif line.startswith("deleted file mode"):
                current_file[2] = "deleted"
            elif line.startswith("rename from"):
                current_file[2] = "renamed"

            # Count insertions and deletions
            if line.startswith("+") and not line.startswith("+++"):
                insertions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

    # Don't forget the last file
    if current_file:
        files.append(
            FileDiff(
                old_path=current_file[0],
                new_path=current_file[1],
                status=current_file[2],
                diff_text="\n".join(current_diff),
                insertions=insertions,
                deletions=deletions,
            )
        )

    return files


def find_next_diff(diff_text: str, current_line: int) -> Optional[int]:
    """
    Find the line number of the next diff hunk.

    Args:
        diff_text: Raw diff output
        current_line: Current line number (0-indexed)

    Returns:
        Line number of next diff hunk, or None if not found
    """
    lines = diff_text.split("\n")

    for i in range(current_line + 1, len(lines)):
        if lines[i].startswith("@@"):
            return i

    return None


def find_previous_diff(diff_text: str, current_line: int) -> Optional[int]:
    """
    Find the line number of the previous diff hunk.

    Args:
        diff_text: Raw diff output
        current_line: Current line number (0-indexed)

    Returns:
        Line number of previous diff hunk, or None if not found
    """
    lines = diff_text.split("\n")

    for i in range(current_line - 1, -1, -1):
        if lines[i].startswith("@@"):
            return i

    return None


def parse_diff_hunks(diff_text: str) -> List[DiffHunk]:
    """
    Parse diff text to extract individual hunks.

    Args:
        diff_text: Raw unified diff output

    Returns:
        List of DiffHunk objects
    """
    hunks = []
    lines = diff_text.split("\n")
    
    # Regular expression to parse hunk headers: @@ -old_start,old_count +new_start,new_count @@
    hunk_header_pattern = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    
    i = 0
    while i < len(lines):
        line = lines[i]
        match = hunk_header_pattern.match(line)
        
        if match:
            old_start = int(match.group(1))
            old_count = int(match.group(2)) if match.group(2) else 1
            new_start = int(match.group(3))
            new_count = int(match.group(4)) if match.group(4) else 1
            
            header = line
            hunk_lines = []
            
            # Collect all lines belonging to this hunk
            i += 1
            while i < len(lines):
                next_line = lines[i]
                
                # Check if we've reached the next hunk or file header
                if (next_line.startswith("@@") or 
                    next_line.startswith("diff --git") or
                    next_line.startswith("--- ") or
                    next_line.startswith("+++ ")):
                    break
                
                hunk_lines.append(next_line)
                i += 1
            
            hunks.append(DiffHunk(
                old_start=old_start,
                old_count=old_count,
                new_start=new_start,
                new_count=new_count,
                header=header,
                lines=hunk_lines
            ))
        else:
            i += 1
    
    return hunks


def parse_file_hunks(file_diff: FileDiff) -> List[DiffHunk]:
    """
    Parse hunks from a FileDiff object.

    Args:
        file_diff: FileDiff object with diff_text

    Returns:
        List of DiffHunk objects
    """
    return parse_diff_hunks(file_diff.diff_text)


def create_patch_from_hunk(file_path: str, hunk: DiffHunk, is_new_file: bool = False, index_line: str = None) -> str:
    """
    Create a complete patch from a single hunk that can be applied with git apply.

    Args:
        file_path: Path to the file
        hunk: The DiffHunk object
        is_new_file: Whether this is for a new file
        index_line: Optional index line from original diff (e.g., "index abc123..def456 100644")

    Returns:
        Complete patch string including file headers
    """
    lines = []
    
    # Add file header
    lines.append(f"diff --git a/{file_path} b/{file_path}")
    
    if is_new_file:
        lines.append("new file mode 100644")
        if index_line:
            lines.append(index_line)
        else:
            lines.append("index 0000000..0000000")
        lines.append("--- /dev/null")
    else:
        if index_line:
            lines.append(index_line)
        else:
            lines.append(f"index 0000000..0000000 100644")
        lines.append(f"--- a/{file_path}")
    
    lines.append(f"+++ b/{file_path}")
    
    # Add hunk
    lines.append(hunk.header)
    lines.extend(hunk.lines)
    
    return "\n".join(lines)


def extract_index_line_from_diff(diff_text: str) -> Optional[str]:
    """
    Extract the index line from a diff.
    
    Args:
        diff_text: The diff text
        
    Returns:
        The index line if found, otherwise None
    """
    for line in diff_text.split("\n"):
        if line.startswith("index "):
            return line
    return None


def create_patch_from_file_hunk(file_diff: FileDiff, hunk: DiffHunk) -> str:
    """
    Create a patch from a FileDiff and a hunk, including proper index.
    
    Args:
        file_diff: The FileDiff object containing the original diff
        hunk: The hunk to create a patch from
        
    Returns:
        Complete patch string
    """
    index_line = extract_index_line_from_diff(file_diff.diff_text)
    is_new = file_diff.status == "added"
    return create_patch_from_hunk(file_diff.new_path, hunk, is_new, index_line)



def create_patch_from_selection(
    file_path: str,
    diff_text: str,
    start_line: int,
    end_line: int
) -> str:
    """
    Create a patch from selected lines in a diff.

    Args:
        file_path: Path to the file
        diff_text: The complete diff text
        start_line: Start line number (0-indexed) in the diff text
        end_line: End line number (0-indexed) in the diff text

    Returns:
        Patch string that can be applied

    Note:
        This function extracts the selected lines and creates a valid patch.
        It handles context lines and ensures the patch is valid.
    """
    lines = diff_text.split("\n")
    
    # Find the hunk that contains the selected lines
    hunks = parse_diff_hunks(diff_text)
    
    # Determine which hunk(s) the selection belongs to
    selected_hunks = []
    for hunk in hunks:
        hunk_text = hunk.text
        # Simple check: if the selected text contains this hunk
        if start_line <= lines.index(hunk.header) <= end_line:
            selected_hunks.append(hunk)
    
    if not selected_hunks:
        # No complete hunk selected, create a partial hunk
        # This is more complex and may need context reconstruction
        return ""
    
    # Create patch with all selected hunks
    patch_lines = [
        f"diff --git a/{file_path} b/{file_path}",
        f"index 0000000..0000000 100644",
        f"--- a/{file_path}",
        f"+++ b/{file_path}"
    ]
    
    for hunk in selected_hunks:
        patch_lines.append(hunk.header)
        patch_lines.extend(hunk.lines)
    
    return "\n".join(patch_lines)
