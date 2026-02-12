"""Commit history and log operations."""

from pathlib import Path
from typing import List, Optional

from clevergit.git.client import GitClient
from clevergit.models.commit_info import CommitInfo
from clevergit.git.errors import CleverGitError


def get_log(
    repo_path: Path,
    max_count: Optional[int] = None,
    branch: Optional[str] = None,
    file_path: Optional[str] = None
) -> List[CommitInfo]:
    """
    Get commit history.
    
    Args:
        repo_path: Path to the repository
        max_count: Maximum number of commits to return
        branch: Specific branch to get log from (default: current)
        file_path: Get log for a specific file
        
    Returns:
        List of CommitInfo objects
        
    Raises:
        CleverGitError: If getting log fails
    """
    client = GitClient(repo_path)
    
    try:
        commits_data = client.log(max_count=max_count, branch=branch)
        # Convert dict to CommitInfo
        commits = []
        for c in commits_data:
            commits.append(CommitInfo(
                sha=c.get('sha', ''),
                short_sha=c.get('sha', '')[:7] if c.get('sha') else '',
                message=c.get('message', ''),
                author=c.get('author', ''),
                author_email=c.get('author_email', ''),
                date=c.get('date'),
                parents=c.get('parents', [])
            ))
        return commits
    except Exception as e:
        raise CleverGitError(f"Failed to get commit log: {e}")


def get_commit(repo_path: Path, commit_hash: str) -> Optional[CommitInfo]:
    """
    Get information about a specific commit.
    
    Args:
        repo_path: Path to the repository
        commit_hash: Hash of the commit
        
    Returns:
        CommitInfo object or None if not found
        
    Raises:
        CleverGitError: If getting commit fails
    """
    client = GitClient(repo_path)
    
    try:
        commits = client.log(max_count=1, commit_hash=commit_hash)
        return commits[0] if commits else None
    except Exception as e:
        raise CleverGitError(f"Failed to get commit '{commit_hash}': {e}")


def get_file_history(
    repo_path: Path,
    file_path: str,
    max_count: Optional[int] = None
) -> List[CommitInfo]:
    """
    Get commit history for a specific file.
    
    Args:
        repo_path: Path to the repository
        file_path: Path to the file (relative to repo root)
        max_count: Maximum number of commits to return
        
    Returns:
        List of CommitInfo objects
        
    Raises:
        CleverGitError: If getting file history fails
    """
    return get_log(repo_path, max_count=max_count, file_path=file_path)


def search_commits(
    repo_path: Path,
    query: str,
    search_type: str = "message",
    max_count: Optional[int] = None
) -> List[CommitInfo]:
    """
    Search commits by message, author, or content.
    
    Args:
        repo_path: Path to the repository
        query: Search query
        search_type: Type of search - "message", "author", or "content"
        max_count: Maximum number of commits to return
        
    Returns:
        List of matching CommitInfo objects
        
    Raises:
        CleverGitError: If search fails
    """
    client = GitClient(repo_path)
    
    try:
        # Build git log command with search options
        cmd = ['log']
        
        if search_type == "message":
            cmd.extend(['--grep', query])
        elif search_type == "author":
            cmd.extend(['--author', query])
        elif search_type == "content":
            cmd.extend(['-S', query])  # Pickaxe search
        else:
            raise CleverGitError(f"Invalid search type: {search_type}")
        
        if max_count:
            cmd.extend(['-n', str(max_count)])
        
        # Add format for parsing
        cmd.append('--format=%H%n%aN%n%aE%n%at%n%s%n%b%n---COMMIT---')
        
        result = client.run_command(cmd)
        
        if not result.success:
            raise CleverGitError(f"Search failed: {result.error}")
        
        # Parse commits
        commits = []
        if result.output:
            commit_texts = result.output.split('---COMMIT---')
            for commit_text in commit_texts:
                if commit_text.strip():
                    lines = commit_text.strip().split('\n')
                    if len(lines) >= 5:
                        commits.append(CommitInfo(
                            hash=lines[0],
                            author_name=lines[1],
                            author_email=lines[2],
                            timestamp=int(lines[3]),
                            message=lines[4],
                            body='\n'.join(lines[5:]) if len(lines) > 5 else ""
                        ))
        
        return commits
    except Exception as e:
        raise CleverGitError(f"Failed to search commits: {e}")


def get_commit_diff(
    repo_path: Path,
    commit_hash: str,
    file_path: Optional[str] = None
) -> str:
    """
    Get the diff for a specific commit.
    
    Args:
        repo_path: Path to the repository
        commit_hash: Hash of the commit
        file_path: Optional specific file to show diff for
        
    Returns:
        Diff content as string
        
    Raises:
        CleverGitError: If getting diff fails
    """
    client = GitClient(repo_path)
    
    try:
        cmd = ['show', commit_hash]
        if file_path:
            cmd.append('--')
            cmd.append(file_path)
        
        result = client.run_command(cmd)
        
        if not result.success:
            raise CleverGitError(f"Failed to get diff: {result.error}")
        
        return result.output or ""
    except Exception as e:
        raise CleverGitError(f"Failed to get commit diff: {e}")


def get_commits_between(
    repo_path: Path,
    from_ref: str,
    to_ref: str = "HEAD"
) -> List[CommitInfo]:
    """
    Get commits between two references (branches, tags, commits).
    
    Args:
        repo_path: Path to the repository
        from_ref: Starting reference
        to_ref: Ending reference (default: HEAD)
        
    Returns:
        List of CommitInfo objects
        
    Raises:
        CleverGitError: If getting commits fails
    """
    client = GitClient(repo_path)
    
    try:
        # Use range notation: from_ref..to_ref
        cmd = [
            'log',
            f'{from_ref}..{to_ref}',
            '--format=%H%n%aN%n%aE%n%at%n%s%n%b%n---COMMIT---'
        ]
        
        result = client.run_command(cmd)
        
        if not result.success:
            raise CleverGitError(f"Failed to get commits: {result.error}")
        
        # Parse commits
        commits = []
        if result.output:
            commit_texts = result.output.split('---COMMIT---')
            for commit_text in commit_texts:
                if commit_text.strip():
                    lines = commit_text.strip().split('\n')
                    if len(lines) >= 5:
                        commits.append(CommitInfo(
                            hash=lines[0],
                            author_name=lines[1],
                            author_email=lines[2],
                            timestamp=int(lines[3]),
                            message=lines[4],
                            body='\n'.join(lines[5:]) if len(lines) > 5 else ""
                        ))
        
        return commits
    except Exception as e:
        raise CleverGitError(f"Failed to get commits between '{from_ref}' and '{to_ref}': {e}")


def get_branches_containing(
    repo_path: Path,
    commit_hash: str
) -> List[str]:
    """
    Get list of branches that contain a specific commit.
    
    Args:
        repo_path: Path to the repository
        commit_hash: Hash of the commit
        
    Returns:
        List of branch names
        
    Raises:
        CleverGitError: If getting branches fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['branch', '--contains', commit_hash])
        
        if not result.success:
            raise CleverGitError(f"Failed to get branches: {result.error}")
        
        branches = []
        if result.output:
            for line in result.output.strip().split('\n'):
                branch = line.strip().lstrip('* ').strip()
                if branch:
                    branches.append(branch)
        
        return branches
    except Exception as e:
        raise CleverGitError(f"Failed to get branches containing '{commit_hash}': {e}")
