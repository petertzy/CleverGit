"""
Branch comparison data model.

This module defines data structures for representing branch comparison results.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class BranchComparison:
    """
    Represents a comparison between two branches.
    
    Attributes:
        base_branch: The base branch name
        compare_branch: The branch being compared
        ahead_commits: List of commit SHAs that compare_branch has but base_branch doesn't
        behind_commits: List of commit SHAs that base_branch has but compare_branch doesn't
        different_files: List of file paths that differ between branches
        ahead_count: Number of commits ahead
        behind_count: Number of commits behind
    """
    base_branch: str
    compare_branch: str
    ahead_commits: List[str]
    behind_commits: List[str]
    different_files: List[str]
    
    @property
    def ahead_count(self) -> int:
        """Get number of commits ahead."""
        return len(self.ahead_commits)
    
    @property
    def behind_count(self) -> int:
        """Get number of commits behind."""
        return len(self.behind_commits)
    
    @property
    def is_up_to_date(self) -> bool:
        """Check if branches are up to date (no differences)."""
        return self.ahead_count == 0 and self.behind_count == 0
    
    def summary(self) -> str:
        """Get a human-readable summary of the comparison."""
        if self.is_up_to_date:
            return f"'{self.compare_branch}' is up to date with '{self.base_branch}'"
        
        parts = []
        if self.ahead_count > 0:
            parts.append(f"{self.ahead_count} commit(s) ahead")
        if self.behind_count > 0:
            parts.append(f"{self.behind_count} commit(s) behind")
        
        return f"'{self.compare_branch}' is {', '.join(parts)} of '{self.base_branch}'"
