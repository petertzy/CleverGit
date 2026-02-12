"""Merge and rebase operations for Git repositories."""

from pathlib import Path
from typing import Optional, List

from clevergit.git.client import GitClient
from clevergit.git.errors import MergeError, CleverGitError


def merge_branch(
    repo_path: Path,
    branch_name: str,
    no_ff: bool = False,
    message: Optional[str] = None
) -> None:
    """
    Merge a branch into the current branch.
    
    Args:
        repo_path: Path to the repository
        branch_name: Name of the branch to merge
        no_ff: Force a merge commit even if fast-forward is possible
        message: Custom merge commit message
        
    Raises:
        MergeError: If merge fails or conflicts occur
    """
    client = GitClient(repo_path)
    
    try:
        client.merge(branch_name, no_ff=no_ff, message=message)
    except Exception as e:
        raise MergeError(f"Failed to merge branch '{branch_name}': {e}")


def abort_merge(repo_path: Path) -> None:
    """
    Abort an ongoing merge operation.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        MergeError: If no merge is in progress or abort fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['merge', '--abort'])
        if not result.success:
            raise MergeError(f"Failed to abort merge: {result.error}")
    except Exception as e:
        raise MergeError(f"Failed to abort merge: {e}")


def rebase_branch(
    repo_path: Path,
    branch_name: str,
    interactive: bool = False
) -> None:
    """
    Rebase current branch onto another branch.
    
    Args:
        repo_path: Path to the repository
        branch_name: Name of the branch to rebase onto
        interactive: Whether to perform an interactive rebase
        
    Raises:
        MergeError: If rebase fails or conflicts occur
    """
    client = GitClient(repo_path)
    
    try:
        client.rebase(branch_name, interactive=interactive)
    except Exception as e:
        raise MergeError(f"Failed to rebase onto '{branch_name}': {e}")


def abort_rebase(repo_path: Path) -> None:
    """
    Abort an ongoing rebase operation.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        MergeError: If no rebase is in progress or abort fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['rebase', '--abort'])
        if not result.success:
            raise MergeError(f"Failed to abort rebase: {result.error}")
    except Exception as e:
        raise MergeError(f"Failed to abort rebase: {e}")


def continue_rebase(repo_path: Path) -> None:
    """
    Continue a rebase operation after resolving conflicts.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        MergeError: If continue fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['rebase', '--continue'])
        if not result.success:
            raise MergeError(f"Failed to continue rebase: {result.error}")
    except Exception as e:
        raise MergeError(f"Failed to continue rebase: {e}")


def skip_rebase_commit(repo_path: Path) -> None:
    """
    Skip the current commit during a rebase.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        MergeError: If skip fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['rebase', '--skip'])
        if not result.success:
            raise MergeError(f"Failed to skip rebase commit: {result.error}")
    except Exception as e:
        raise MergeError(f"Failed to skip rebase commit: {e}")


def get_conflict_files(repo_path: Path) -> List[str]:
    """
    Get list of files with merge conflicts.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        List of file paths with conflicts
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['diff', '--name-only', '--diff-filter=U'])
        if result.success and result.output:
            return [f.strip() for f in result.output.strip().split('\n') if f.strip()]
        return []
    except Exception:
        return []


def resolve_conflict_with_ours(repo_path: Path, file_path: str) -> None:
    """
    Resolve conflict by keeping our version of the file.
    
    Args:
        repo_path: Path to the repository
        file_path: Path to the conflicted file
        
    Raises:
        MergeError: If resolution fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['checkout', '--ours', file_path])
        if not result.success:
            raise MergeError(f"Failed to resolve conflict: {result.error}")
        
        # Stage the resolved file
        client.run_command(['add', file_path])
    except Exception as e:
        raise MergeError(f"Failed to resolve conflict: {e}")


def resolve_conflict_with_theirs(repo_path: Path, file_path: str) -> None:
    """
    Resolve conflict by keeping their version of the file.
    
    Args:
        repo_path: Path to the repository
        file_path: Path to the conflicted file
        
    Raises:
        MergeError: If resolution fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['checkout', '--theirs', file_path])
        if not result.success:
            raise MergeError(f"Failed to resolve conflict: {result.error}")
        
        # Stage the resolved file
        client.run_command(['add', file_path])
    except Exception as e:
        raise MergeError(f"Failed to resolve conflict: {e}")
