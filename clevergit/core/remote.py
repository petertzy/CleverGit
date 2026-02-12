"""Remote repository operations."""

import subprocess
from pathlib import Path
from typing import Optional, List, Dict

from clevergit.git.client import GitClient
from clevergit.git.errors import RemoteError, CleverGitError


def fetch(
    repo_path: Path,
    remote: str = "origin",
    prune: bool = False
) -> None:
    """
    Fetch updates from a remote repository.
    
    Args:
        repo_path: Path to the repository
        remote: Name of the remote (default: origin)
        prune: Remove deleted remote branches
        
    Raises:
        RemoteError: If fetch fails
    """
    client = GitClient(repo_path)
    
    try:
        client.fetch(remote, prune=prune)
    except Exception as e:
        raise RemoteError(f"Failed to fetch from '{remote}': {e}")


def pull(
    repo_path: Path,
    remote: str = "origin",
    branch: Optional[str] = None,
    rebase: bool = False
) -> None:
    """
    Pull updates from a remote repository.
    
    Args:
        repo_path: Path to the repository
        remote: Name of the remote (default: origin)
        branch: Branch to pull (default: current branch)
        rebase: Use rebase instead of merge
        
    Raises:
        RemoteError: If pull fails
    """
    client = GitClient(repo_path)
    
    try:
        client.pull(remote, branch=branch, rebase=rebase)
    except Exception as e:
        raise RemoteError(f"Failed to pull from '{remote}': {e}")


def push(
    repo_path: Path,
    remote: str = "origin",
    branch: Optional[str] = None,
    force: bool = False,
    set_upstream: bool = False
) -> None:
    """
    Push commits to a remote repository.
    
    Args:
        repo_path: Path to the repository
        remote: Name of the remote (default: origin)
        branch: Branch to push (default: current branch)
        force: Force push (use with caution!)
        set_upstream: Set upstream tracking branch
        
    Raises:
        RemoteError: If push fails
    """
    client = GitClient(repo_path)
    
    try:
        client.push(remote, branch=branch, force=force, set_upstream=set_upstream)
    except Exception as e:
        raise RemoteError(f"Failed to push to '{remote}': {e}")


def add_remote(repo_path: Path, name: str, url: str) -> None:
    """
    Add a new remote repository.
    
    Args:
        repo_path: Path to the repository
        name: Name for the remote
        url: URL of the remote repository
        
    Raises:
        RemoteError: If adding remote fails
    """
    client = GitClient(repo_path)
    
    try:
        client.add_remote(name, url)
    except Exception as e:
        raise RemoteError(f"Failed to add remote '{name}': {e}")


def remove_remote(repo_path: Path, name: str) -> None:
    """
    Remove a remote repository.
    
    Args:
        repo_path: Path to the repository
        name: Name of the remote to remove
        
    Raises:
        RemoteError: If removing remote fails
    """
    client = GitClient(repo_path)
    
    try:
        client.remove_remote(name)
    except Exception as e:
        raise RemoteError(f"Failed to remove remote '{name}': {e}")


def rename_remote(repo_path: Path, old_name: str, new_name: str) -> None:
    """
    Rename a remote repository.
    
    Args:
        repo_path: Path to the repository
        old_name: Current name of the remote
        new_name: New name for the remote
        
    Raises:
        RemoteError: If renaming remote fails
    """
    client = GitClient(repo_path)
    
    try:
        subprocess.run(
            ['git', 'remote', 'rename', old_name, new_name],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
    except Exception as e:
        raise RemoteError(f"Failed to rename remote '{old_name}' to '{new_name}': {e}")


def set_remote_url(repo_path: Path, name: str, url: str) -> None:
    """
    Change the URL of a remote repository.
    
    Args:
        repo_path: Path to the repository
        name: Name of the remote
        url: New URL for the remote
        
    Raises:
        RemoteError: If setting URL fails
    """
    client = GitClient(repo_path)
    
    try:
        subprocess.run(
            ['git', 'remote', 'set-url', name, url],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
    except Exception as e:
        raise RemoteError(f"Failed to set URL for remote '{name}': {e}")


def list_remotes(repo_path: Path, verbose: bool = False) -> Dict[str, str]:
    """
    List all remote repositories.
    
    Args:
        repo_path: Path to the repository
        verbose: Include URLs in the output
        
    Returns:
        Dictionary mapping remote names to URLs
        
    Raises:
        RemoteError: If listing remotes fails
    """
    client = GitClient(repo_path)
    remotes = {}
    
    try:
        cmd = ['git', 'remote', '-v'] if verbose else ['git', 'remote']
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            if verbose:
                # Parse output like: "origin  https://... (fetch)"
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            url = parts[1]
                            # Only include fetch URLs
                            if len(parts) >= 3 and parts[2] == '(fetch)':
                                remotes[name] = url
            else:
                # Simple list of remote names
                for name in result.stdout.strip().split('\n'):
                    if name.strip():
                        remotes[name.strip()] = ""
        
        return remotes
    except Exception as e:
        raise RemoteError(f"Failed to list remotes: {e}")


def get_remote_url(repo_path: Path, name: str = "origin") -> Optional[str]:
    """
    Get the URL of a specific remote.
    
    Args:
        repo_path: Path to the repository
        name: Name of the remote (default: origin)
        
    Returns:
        Remote URL or None if not found
        
    Raises:
        RemoteError: If getting URL fails
    """
    client = GitClient(repo_path)
    
    try:
        result = subprocess.run(
            ['git', 'remote', 'get-url', name],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def show_remote(repo_path: Path, name: str = "origin") -> Dict[str, any]:
    """
    Show detailed information about a remote.
    
    Args:
        repo_path: Path to the repository
        name: Name of the remote (default: origin)
        
    Returns:
        Dictionary with remote information
        
    Raises:
        RemoteError: If showing remote fails
    """
    client = GitClient(repo_path)
    
    try:
        result = subprocess.run(
            ['git', 'remote', 'show', name],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        
        # Parse basic info
        info = {
            'name': name,
            'url': get_remote_url(repo_path, name),
            'details': result.stdout
        }
        
        return info
    except Exception as e:
        raise RemoteError(f"Failed to show remote '{name}': {e}")
