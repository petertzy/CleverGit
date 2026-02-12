"""Conflict detection and resolution for Git merge conflicts."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import re


@dataclass
class ConflictBlock:
    """Represents a single conflict block in a file."""
    
    start_line: int  # Line number where conflict starts (<<<<<<< marker)
    end_line: int    # Line number where conflict ends (>>>>>>> marker)
    ours_label: str  # Label from <<<<<<< line (e.g., "HEAD")
    theirs_label: str  # Label from >>>>>>> line (e.g., "branch-name")
    
    # Content sections
    ours_content: List[str]  # Lines between <<<<<<< and =======
    theirs_content: List[str]  # Lines between ======= and >>>>>>>
    base_content: Optional[List[str]] = None  # Lines in ||||||| section if present
    
    def has_base(self) -> bool:
        """Check if this conflict has a base (diff3 style)."""
        return self.base_content is not None
    
    def get_ours_text(self) -> str:
        """Get the 'ours' content as a single string."""
        return '\n'.join(self.ours_content)
    
    def get_theirs_text(self) -> str:
        """Get the 'theirs' content as a single string."""
        return '\n'.join(self.theirs_content)
    
    def get_base_text(self) -> str:
        """Get the 'base' content as a single string."""
        if self.base_content is None:
            return ""
        return '\n'.join(self.base_content)


@dataclass
class ConflictedFile:
    """Represents a file with merge conflicts."""
    
    file_path: str
    conflicts: List[ConflictBlock]
    original_content: List[str]  # Original file lines with conflict markers
    
    def get_conflict_count(self) -> int:
        """Get the number of conflicts in the file."""
        return len(self.conflicts)
    
    def has_conflicts(self) -> bool:
        """Check if the file has any conflicts."""
        return len(self.conflicts) > 0


def parse_conflict_markers(content: str) -> List[ConflictBlock]:
    """
    Parse conflict markers in file content and extract conflict blocks.
    
    Supports both standard merge conflicts:
        <<<<<<< ours
        our content
        =======
        their content
        >>>>>>> theirs
    
    And diff3-style conflicts with base:
        <<<<<<< ours
        our content
        ||||||| base
        base content
        =======
        their content
        >>>>>>> theirs
    
    Args:
        content: File content as string
        
    Returns:
        List of ConflictBlock objects
    """
    lines = content.split('\n')
    conflicts: List[ConflictBlock] = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for conflict start marker
        if line.startswith('<<<<<<<'):
            start_line = i
            ours_label = line[7:].strip()
            
            # Find the sections
            ours_content: List[str] = []
            base_content: Optional[List[str]] = None
            theirs_content: List[str] = []
            
            i += 1
            # Parse 'ours' section
            while i < len(lines) and not lines[i].startswith('|||||||') and not lines[i].startswith('======='):
                ours_content.append(lines[i])
                i += 1
            
            # Check for base section (diff3 style)
            if i < len(lines) and lines[i].startswith('|||||||'):
                base_content = []
                i += 1
                while i < len(lines) and not lines[i].startswith('======='):
                    base_content.append(lines[i])
                    i += 1
            
            # Should now be at separator
            if i < len(lines) and lines[i].startswith('======='):
                i += 1
                # Parse 'theirs' section
                while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                    theirs_content.append(lines[i])
                    i += 1
                
                # Should now be at end marker
                if i < len(lines) and lines[i].startswith('>>>>>>>'):
                    end_line = i
                    theirs_label = lines[i][7:].strip()
                    
                    conflict = ConflictBlock(
                        start_line=start_line,
                        end_line=end_line,
                        ours_label=ours_label,
                        theirs_label=theirs_label,
                        ours_content=ours_content,
                        theirs_content=theirs_content,
                        base_content=base_content
                    )
                    conflicts.append(conflict)
        
        i += 1
    
    return conflicts


def parse_conflicted_file(file_path: Path) -> ConflictedFile:
    """
    Parse a file with conflict markers.
    
    Args:
        file_path: Path to the file to parse
        
    Returns:
        ConflictedFile object with all conflicts
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    lines = content.split('\n')
    conflicts = parse_conflict_markers(content)
    
    return ConflictedFile(
        file_path=str(file_path),
        conflicts=conflicts,
        original_content=lines
    )


def has_conflict_markers(content: str) -> bool:
    """
    Check if content contains conflict markers.
    
    Args:
        content: File content to check
        
    Returns:
        True if conflict markers are present
    """
    lines = content.split('\n')
    return any(
        line.startswith('<<<<<<<') or 
        line.startswith('=======') or 
        line.startswith('>>>>>>>')
        for line in lines
    )


def resolve_conflict_take_ours(conflict: ConflictBlock) -> List[str]:
    """
    Resolve a conflict by taking the 'ours' version.
    
    Args:
        conflict: The conflict block to resolve
        
    Returns:
        List of lines (the 'ours' content)
    """
    return conflict.ours_content.copy()


def resolve_conflict_take_theirs(conflict: ConflictBlock) -> List[str]:
    """
    Resolve a conflict by taking the 'theirs' version.
    
    Args:
        conflict: The conflict block to resolve
        
    Returns:
        List of lines (the 'theirs' content)
    """
    return conflict.theirs_content.copy()


def resolve_conflict_take_both(conflict: ConflictBlock, ours_first: bool = True) -> List[str]:
    """
    Resolve a conflict by taking both versions.
    
    Args:
        conflict: The conflict block to resolve
        ours_first: If True, put 'ours' first, otherwise 'theirs' first
        
    Returns:
        List of lines (both versions combined)
    """
    if ours_first:
        return conflict.ours_content.copy() + conflict.theirs_content.copy()
    else:
        return conflict.theirs_content.copy() + conflict.ours_content.copy()


def apply_resolution(
    conflicted_file: ConflictedFile,
    conflict_index: int,
    resolved_content: List[str]
) -> str:
    """
    Apply a resolution to a specific conflict in a file.
    
    Args:
        conflicted_file: The file with conflicts
        conflict_index: Index of the conflict to resolve (0-based)
        resolved_content: The resolved content lines to insert
        
    Returns:
        The new file content with the conflict resolved
        
    Raises:
        IndexError: If conflict_index is out of range
    """
    if conflict_index < 0 or conflict_index >= len(conflicted_file.conflicts):
        raise IndexError(f"Conflict index {conflict_index} out of range")
    
    conflict = conflicted_file.conflicts[conflict_index]
    lines = conflicted_file.original_content.copy()
    
    # Replace lines from start_line to end_line (inclusive) with resolved content
    # Remove the conflict markers and content
    new_lines = (
        lines[:conflict.start_line] +
        resolved_content +
        lines[conflict.end_line + 1:]
    )
    
    return '\n'.join(new_lines)


def resolve_all_conflicts(
    conflicted_file: ConflictedFile,
    resolutions: List[List[str]]
) -> str:
    """
    Apply resolutions to all conflicts in a file.
    
    Args:
        conflicted_file: The file with conflicts
        resolutions: List of resolved content for each conflict (in order)
        
    Returns:
        The new file content with all conflicts resolved
        
    Raises:
        ValueError: If number of resolutions doesn't match number of conflicts
    """
    if len(resolutions) != len(conflicted_file.conflicts):
        raise ValueError(
            f"Expected {len(conflicted_file.conflicts)} resolutions, "
            f"got {len(resolutions)}"
        )
    
    lines = conflicted_file.original_content.copy()
    
    # Process conflicts in reverse order to maintain line numbers
    for i in range(len(conflicted_file.conflicts) - 1, -1, -1):
        conflict = conflicted_file.conflicts[i]
        resolved_content = resolutions[i]
        
        # Replace lines from start_line to end_line (inclusive)
        lines = (
            lines[:conflict.start_line] +
            resolved_content +
            lines[conflict.end_line + 1:]
        )
    
    return '\n'.join(lines)
