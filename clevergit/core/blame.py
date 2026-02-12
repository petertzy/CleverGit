"""Blame operations for Git."""

from pathlib import Path
from typing import List, Optional
from datetime import datetime
import re

from clevergit.git.client import GitClient
from clevergit.models.blame_info import BlameInfo
from clevergit.git.errors import CleverGitError


def get_blame(
    repo_path: Path,
    file_path: str,
    commit: Optional[str] = None
) -> List[BlameInfo]:
    """
    Get blame information for a file.
    
    Args:
        repo_path: Path to the repository
        file_path: Path to the file (relative to repo root)
        commit: Optional commit SHA to blame at (default: HEAD)
        
    Returns:
        List of BlameInfo objects, one per line
        
    Raises:
        CleverGitError: If blame operation fails
    """
    client = GitClient(repo_path)
    
    try:
        # Build git blame command with porcelain format for easier parsing
        cmd = ['blame', '--porcelain']
        
        if commit:
            cmd.append(commit)
        
        cmd.append('--')
        cmd.append(file_path)
        
        result = client.run_command(cmd)
        
        if not result.success:
            raise CleverGitError(f"Failed to get blame: {result.error}")
        
        # Parse porcelain format output
        return _parse_blame_porcelain(result.output)
    except Exception as e:
        raise CleverGitError(f"Failed to get blame for '{file_path}': {e}")


def _parse_blame_porcelain(output: str) -> List[BlameInfo]:
    """
    Parse git blame --porcelain output.
    
    The porcelain format outputs one block per line:
    - First line: <sha> <original line> <final line> [<lines in group>]
    - Following lines: metadata (author, author-mail, author-time, etc.)
    - Last line: tab + line content
    
    Args:
        output: Raw git blame --porcelain output
        
    Returns:
        List of BlameInfo objects
    """
    blame_list: List[BlameInfo] = []
    lines = output.split('\n')
    
    i = 0
    commit_cache = {}  # Cache commit metadata to avoid re-parsing
    
    while i < len(lines):
        line = lines[i]
        
        if not line or not line[0].isalnum():
            i += 1
            continue
        
        # Parse first line: <sha> <original line> <final line> [<lines in group>]
        parts = line.split()
        if len(parts) < 3:
            i += 1
            continue
        
        commit_sha = parts[0]
        final_line = int(parts[2])
        
        # Check if we have this commit's metadata cached
        if commit_sha in commit_cache:
            commit_data = commit_cache[commit_sha]
            i += 1
        else:
            # Parse commit metadata
            commit_data = {
                'sha': commit_sha,
                'author': '',
                'author_email': '',
                'author_time': 0,
                'summary': ''
            }
            
            i += 1
            while i < len(lines):
                meta_line = lines[i]
                
                if meta_line.startswith('author '):
                    commit_data['author'] = meta_line[7:]
                elif meta_line.startswith('author-mail '):
                    # Remove < and > from email
                    email = meta_line[12:].strip()
                    if email.startswith('<') and email.endswith('>'):
                        email = email[1:-1]
                    commit_data['author_email'] = email
                elif meta_line.startswith('author-time '):
                    commit_data['author_time'] = int(meta_line[12:])
                elif meta_line.startswith('summary '):
                    commit_data['summary'] = meta_line[8:]
                elif meta_line.startswith('\t'):
                    # This is the line content
                    break
                
                i += 1
            
            commit_cache[commit_sha] = commit_data
        
        # Get line content (starts with tab)
        content = ''
        if i < len(lines) and lines[i].startswith('\t'):
            content = lines[i][1:]  # Remove leading tab
        
        # Create BlameInfo object
        blame_info = BlameInfo(
            line_number=final_line,
            commit_sha=commit_data['sha'],
            short_sha=commit_data['sha'][:7],
            author=commit_data['author'],
            author_email=commit_data['author_email'],
            date=datetime.fromtimestamp(commit_data['author_time']),
            content=content,
            summary=commit_data['summary']
        )
        
        blame_list.append(blame_info)
        i += 1
    
    return blame_list


def get_blame_for_line(
    repo_path: Path,
    file_path: str,
    line_number: int,
    commit: Optional[str] = None
) -> Optional[BlameInfo]:
    """
    Get blame information for a specific line.
    
    Args:
        repo_path: Path to the repository
        file_path: Path to the file (relative to repo root)
        line_number: Line number (1-indexed)
        commit: Optional commit SHA to blame at (default: HEAD)
        
    Returns:
        BlameInfo object for the line, or None if not found
        
    Raises:
        CleverGitError: If blame operation fails
    """
    blame_list = get_blame(repo_path, file_path, commit)
    
    for blame_info in blame_list:
        if blame_info.line_number == line_number:
            return blame_info
    
    return None
