"""
Tag information models.

This module defines data structures for representing tag information.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TagInfo:
    """
    Represents information about a Git tag.
    
    Attributes:
        name: Tag name
        commit_sha: SHA of the commit the tag points to
        is_annotated: Whether this is an annotated tag
        message: Tag message (for annotated tags)
        tagger: Name of the person who created the tag
        date: Date when the tag was created
    """
    name: str
    commit_sha: str
    is_annotated: bool = False
    message: Optional[str] = None
    tagger: Optional[str] = None
    date: Optional[datetime] = None
    
    @property
    def short_sha(self) -> str:
        """Get short commit SHA (7 characters)."""
        return self.commit_sha[:7] if self.commit_sha else ""
    
    def format_oneline(self) -> str:
        """Format as one-line tag information."""
        tag_type = "annotated" if self.is_annotated else "lightweight"
        return f"{self.name} ({tag_type}) -> {self.short_sha}"
    
    def __str__(self) -> str:
        """String representation."""
        return self.format_oneline()
