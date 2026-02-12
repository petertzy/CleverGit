"""
Branch information models.

This module defines data structures for representing branch information.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BranchInfo:
    """
    Represents information about a Git branch.
    
    Attributes:
        name: Branch name
        commit_sha: SHA of the commit the branch points to
        is_current: Whether this is the currently checked out branch
        is_remote: Whether this is a remote branch
        upstream: Name of the upstream branch (if tracking)
        ahead: Number of commits ahead of upstream
        behind: Number of commits behind upstream
    """
    name: str
    commit_sha: str
    is_current: bool
    is_remote: bool
    upstream: Optional[str] = None
    ahead: int = 0
    behind: int = 0
    
    @property
    def short_name(self) -> str:
        """Get short branch name (without remote prefix). Example: origin/main -> main"""
        if self.is_remote and "/" in self.name:
            return self.name.split("/", 1)[1]
        return self.name
    
    @property
    def remote_name(self) -> Optional[str]:
        """Get remote name for remote branches. Example: origin/main -> origin"""
        if self.is_remote and "/" in self.name:
            return self.name.split("/", 1)[0]
        return None
    
    @property
    def tracking_status(self) -> str:
        """Get tracking status as a string. Returns: String like "ahead 2, behind 1" or empty if no tracking"""
        if not self.upstream:
            return ""
        
        parts = []
        if self.ahead > 0:
            parts.append(f"ahead {self.ahead}")
        if self.behind > 0:
            parts.append(f"behind {self.behind}")
        
        return ", ".join(parts) if parts else "up to date"
    
    def format_oneline(self) -> str:
        """Format as one-line branch information. Returns: String like "* main [ahead 2] abc1234" """
        marker = "*" if self.is_current else " "
        tracking = f" [{self.tracking_status}]" if self.tracking_status else ""
        return f"{marker} {self.name}{tracking} {self.commit_sha[:7]}"
    
    def __str__(self) -> str:
        """String representation."""
        return self.format_oneline()
