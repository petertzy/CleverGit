"""
Commit information models.

This module defines data structures for representing commit information.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CommitInfo:
    """
    Represents information about a Git commit.
    
    Attributes:
        sha: Full commit SHA
        short_sha: Short commit SHA (7 characters)
        message: Commit message
        author: Author name
        author_email: Author email
        date: Commit date
        parents: List of parent commit SHAs
    """
    sha: str
    short_sha: str
    message: str
    author: str
    author_email: str
    date: Optional[datetime]
    parents: List[str]
    
    @property
    def subject(self) -> str:
        """Get the first line of the commit message (subject)."""
        return self.message.split("\n")[0]
    
    @property
    def body(self) -> str:
        """Get the body of the commit message (everything after first line)."""
        lines = self.message.split("\n")
        if len(lines) > 1:
            return "\n".join(lines[1:]).strip()
        return ""
    
    @property
    def is_merge(self) -> bool:
        """Check if this is a merge commit."""
        return len(self.parents) > 1
    
    def format_oneline(self) -> str:
        """Format as one-line log entry."""
        return f"{self.short_sha} {self.subject}"
    
    def format_full(self) -> str:
        """Format as full commit information."""
        lines = [f"commit {self.sha}", f"Author: {self.author} <{self.author_email}>"]
        
        if self.date:
            lines.append(f"Date:   {self.date.strftime('%a %b %d %H:%M:%S %Y')}")
        
        lines.append("")
        lines.append(f"    {self.message}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """String representation."""
        return self.format_oneline()
