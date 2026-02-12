"""
Blame information models.

This module defines data structures for representing git blame information.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BlameInfo:
    """
    Represents blame information for a single line of code.
    
    Attributes:
        line_number: Line number (1-indexed)
        commit_sha: Full commit SHA
        short_sha: Short commit SHA (7 characters)
        author: Author name
        author_email: Author email
        date: Commit date
        content: Line content
        summary: Commit message summary (first line)
    """
    line_number: int
    commit_sha: str
    short_sha: str
    author: str
    author_email: str
    date: datetime
    content: str
    summary: str
    
    def format_oneline(self) -> str:
        """Format as one-line blame entry."""
        date_str = self.date.strftime("%Y-%m-%d")
        return f"{self.short_sha} ({self.author} {date_str}) {self.content}"
    
    def __str__(self) -> str:
        """String representation."""
        return self.format_oneline()
