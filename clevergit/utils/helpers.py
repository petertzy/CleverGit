"""Helper utility functions."""

import re
from pathlib import Path
from typing import Optional, List
from datetime import datetime


def is_valid_branch_name(name: str) -> bool:
    """
    Check if a branch name is valid according to Git rules.
    
    Args:
        name: Branch name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name or name.strip() != name:
        return False
    
    # Git branch name rules
    invalid_patterns = [
        r'^\.', # Cannot start with .
        r'\.\.',  # Cannot contain ..
        r'[~^:\?\*\[]',  # Cannot contain special chars
        r'@{',  # Cannot contain @{
        r'\\',  # Cannot contain backslash
        r'//',  # Cannot contain consecutive slashes
        r'^/',  # Cannot start with /
        r'/$',  # Cannot end with /
        r'\.lock$',  # Cannot end with .lock
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, name):
            return False
    
    return True


def parse_git_status_code(code: str) -> tuple:
    """
    Parse Git status code (XY format).
    
    Args:
        code: Two-character status code
        
    Returns:
        Tuple of (staged_status, unstaged_status)
    """
    if len(code) != 2:
        return ('', '')
    
    return (code[0], code[1])


def format_timestamp(timestamp: int, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format Unix timestamp to human-readable string.
    
    Args:
        timestamp: Unix timestamp
        format: strftime format string
        
    Returns:
        Formatted datetime string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format)


def get_relative_path(path: Path, base: Path) -> Path:
    """
    Get relative path from base to path.
    
    Args:
        path: Target path
        base: Base path
        
    Returns:
        Relative path
    """
    try:
        return path.relative_to(base)
    except ValueError:
        return path


def find_git_root(start_path: Path) -> Optional[Path]:
    """
    Find the root of a Git repository by searching for .git directory.
    
    Args:
        start_path: Path to start searching from
        
    Returns:
        Path to repository root or None if not found
    """
    current = start_path.resolve()
    
    while current != current.parent:
        git_dir = current / '.git'
        if git_dir.exists():
            return current
        current = current.parent
    
    return None


def normalize_path(path: str) -> str:
    """
    Normalize file path for Git (use forward slashes, relative paths).
    
    Args:
        path: Path string to normalize
        
    Returns:
        Normalized path string
    """
    # Convert to Path and back to normalize
    p = Path(path)
    # Use forward slashes (POSIX style)
    return str(p).replace('\\', '/')


def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix.
    
    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    
    return s[:max_length - len(suffix)] + suffix


def split_commit_message(message: str) -> tuple:
    """
    Split commit message into subject and body.
    
    Args:
        message: Full commit message
        
    Returns:
        Tuple of (subject, body)
    """
    lines = message.strip().split('\n', 1)
    subject = lines[0].strip()
    body = lines[1].strip() if len(lines) > 1 else ""
    return (subject, body)


def parse_remote_url(url: str) -> dict:
    """
    Parse remote URL into components.
    
    Args:
        url: Remote URL (HTTPS or SSH)
        
    Returns:
        Dictionary with url components
    """
    result = {
        'url': url,
        'protocol': None,
        'host': None,
        'owner': None,
        'repo': None
    }
    
    # HTTPS URL pattern
    https_pattern = r'https?://([^/]+)/([^/]+)/([^/.]+)(\.git)?'
    # SSH URL pattern
    ssh_pattern = r'git@([^:]+):([^/]+)/([^/.]+)(\.git)?'
    
    match = re.match(https_pattern, url)
    if match:
        result['protocol'] = 'https'
        result['host'] = match.group(1)
        result['owner'] = match.group(2)
        result['repo'] = match.group(3)
        return result
    
    match = re.match(ssh_pattern, url)
    if match:
        result['protocol'] = 'ssh'
        result['host'] = match.group(1)
        result['owner'] = match.group(2)
        result['repo'] = match.group(3)
        return result
    
    return result


def list_modified_files(repo_path: Path, include_untracked: bool = False) -> List[str]:
    """
    List all modified files in repository.
    
    Args:
        repo_path: Path to repository
        include_untracked: Include untracked files
        
    Returns:
        List of file paths
    """
    from clevergit.core.status import get_status
    
    status = get_status(repo_path)
    files = []
    
    for file in status.staged:
        files.append(str(file.path))
    for file in status.unstaged:
        files.append(str(file.path))
    
    if include_untracked:
        for file in status.untracked:
            files.append(str(file.path))
    
    return list(set(files))  # Remove duplicates
