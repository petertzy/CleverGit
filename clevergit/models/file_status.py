"""
File status models.

This module defines data structures for representing file status information.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List


class ChangeType(Enum):
    """Enumeration of file change types."""
    MODIFIED = "modified"
    ADDED = "added"
    DELETED = "deleted"
    RENAMED = "renamed"
    COPIED = "copied"
    UNTRACKED = "untracked"
    CONFLICTED = "conflicted"


@dataclass
class FileStatus:
    """
    Represents the status of a single file.
    
    Attributes:
        path: File path relative to repository root
        change_type: Type of change
        staged: Whether the file is staged for commit
        old_path: Original path (for renamed files)
    """
    path: str
    change_type: ChangeType
    staged: bool
    old_path: str = ""
    
    @property
    def is_modified(self) -> bool:
        """Check if file is modified."""
        return self.change_type == ChangeType.MODIFIED
    
    @property
    def is_untracked(self) -> bool:
        """Check if file is untracked."""
        return self.change_type == ChangeType.UNTRACKED
    
    @property
    def is_conflicted(self) -> bool:
        """Check if file has conflicts."""
        return self.change_type == ChangeType.CONFLICTED
    
    def __str__(self) -> str:
        """String representation."""
        status_char = "S" if self.staged else " "
        return f"[{status_char}] {self.change_type.value:10s} {self.path}"


@dataclass
class FileStatusList:
    """Container for categorized file status information."""
    modified: List[FileStatus]
    untracked: List[FileStatus]
    staged: List[FileStatus]
    conflicted: List[FileStatus]
    deleted: List[FileStatus]
    
    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return bool(self.modified or self.untracked or self.staged or self.conflicted or self.deleted)
    
    @property
    def has_staged_changes(self) -> bool:
        """Check if there are staged changes."""
        return bool(self.staged)
    
    @property
    def has_conflicts(self) -> bool:
        """Check if there are conflicts."""
        return bool(self.conflicted)
    
    @property
    def unstaged(self) -> List[FileStatus]:
        """Get all unstaged files (modified + deleted, excluding untracked and conflicted)."""
        return self.modified + self.deleted
    
    @property
    def total_count(self) -> int:
        """Get total number of changed files."""
        return len(self.modified) + len(self.untracked) + len(self.staged) + len(self.conflicted) + len(self.deleted)
    
    def __str__(self) -> str:
        """String representation."""
        lines = []
        
        if self.staged:
            lines.append("Staged changes:")
            for file in self.staged:
                lines.append(f"  {file}")
        
        if self.modified:
            lines.append("Modified (not staged):")
            for file in self.modified:
                lines.append(f"  {file}")
        
        if self.deleted:
            lines.append("Deleted:")
            for file in self.deleted:
                lines.append(f"  {file}")
        
        if self.untracked:
            lines.append("Untracked files:")
            for file in self.untracked:
                lines.append(f"  {file}")
        
        if self.conflicted:
            lines.append("Conflicted files:")
            for file in self.conflicted:
                lines.append(f"  {file}")
        
        if not self.has_changes:
            lines.append("No changes")
        
        return "\n".join(lines)
