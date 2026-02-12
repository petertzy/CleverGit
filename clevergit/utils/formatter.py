"""Output formatting utilities."""

from typing import List
from clevergit.models.file_status import FileStatusList, ChangeType
from clevergit.models.commit_info import CommitInfo
from clevergit.models.branch_info import BranchInfo


def format_status(status: FileStatusList) -> str:
    """
    Format file status list for display.
    
    Args:
        status: FileStatusList object
        
    Returns:
        Formatted status string
    """
    lines = []
    
    if not status.has_changes:
        lines.append("Nothing to commit, working tree clean")
        return "\n".join(lines)
    
    # Staged changes
    if status.staged:
        lines.append("Changes to be committed:")
        for file in status.staged:
            change_type = _format_change_type(file.change_type)
            lines.append(f"  {change_type:12} {file.path}")
        lines.append("")
    
    # Unstaged changes
    if status.unstaged:
        lines.append("Changes not staged for commit:")
        for file in status.unstaged:
            change_type = _format_change_type(file.change_type)
            lines.append(f"  {change_type:12} {file.path}")
        lines.append("")
    
    # Untracked files
    if status.untracked:
        lines.append("Untracked files:")
        for file in status.untracked:
            lines.append(f"  {file.path}")
        lines.append("")
    
    return "\n".join(lines)


def format_log(commits: List[CommitInfo], oneline: bool = False) -> str:
    """
    Format commit log for display.
    
    Args:
        commits: List of CommitInfo objects
        oneline: Use compact one-line format
        
    Returns:
        Formatted log string
    """
    if not commits:
        return "No commits yet"
    
    lines = []
    
    for commit in commits:
        if oneline:
            lines.append(commit.format_oneline())
        else:
            lines.append(commit.format_full())
            lines.append("")  # Blank line between commits
    
    return "\n".join(lines)


def format_branches(branches: List[BranchInfo]) -> str:
    """
    Format branch list for display.
    
    Args:
        branches: List of BranchInfo objects
        
    Returns:
        Formatted branch list string
    """
    if not branches:
        return "No branches found"
    
    lines = []
    
    for branch in branches:
        prefix = "* " if branch.is_current else "  "
        line = f"{prefix}{branch.name}"
        
        # Add tracking info if available
        if branch.upstream:
            if branch.ahead > 0 or branch.behind > 0:
                tracking_info = []
                if branch.ahead > 0:
                    tracking_info.append(f"ahead {branch.ahead}")
                if branch.behind > 0:
                    tracking_info.append(f"behind {branch.behind}")
                line += f" [{', '.join(tracking_info)}]"
        
        lines.append(line)
    
    return "\n".join(lines)


def _format_change_type(change_type: ChangeType) -> str:
    """
    Format change type for display.
    
    Args:
        change_type: ChangeType enum value
        
    Returns:
        Formatted change type string
    """
    mapping = {
        ChangeType.ADDED: "new file:",
        ChangeType.MODIFIED: "modified:",
        ChangeType.DELETED: "deleted:",
        ChangeType.RENAMED: "renamed:",
        ChangeType.COPIED: "copied:",
        ChangeType.CONFLICTED: "conflicted:",
        ChangeType.UNTRACKED: "untracked:",
    }
    return mapping.get(change_type, str(change_type))


def format_diff_stats(additions: int, deletions: int) -> str:
    """
    Format diff statistics.
    
    Args:
        additions: Number of lines added
        deletions: Number of lines deleted
        
    Returns:
        Formatted diff stats string
    """
    parts = []
    if additions > 0:
        parts.append(f"+{additions}")
    if deletions > 0:
        parts.append(f"-{deletions}")
    return ", ".join(parts) if parts else "no changes"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 KB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
