"""
Stash information models.

This module defines data structures for representing stash information.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StashInfo:
    """
    Represents information about a Git stash entry.
    
    Attributes:
        index: Stash index (e.g., 0 for stash@{0})
        message: Stash message/description
        branch: Branch the stash was created on
        commit_sha: SHA of the stash commit
        created_at: When the stash was created
    """
    index: int
    message: str
    branch: str
    commit_sha: str
    created_at: Optional[datetime] = None
    
    @property
    def ref(self) -> str:
        """
        Get stash reference.
        
        Returns:
            String like "stash@{0}"
        """
        return f"stash@{{{self.index}}}"
    
    def format_oneline(self) -> str:
        """
        Format as one-line stash information.
        
        Returns:
            String like "stash@{0}: WIP on main: abc1234 message"
        """
        return f"{self.ref}: {self.message}"
    
    def __str__(self) -> str:
        """String representation."""
        return self.format_oneline()
