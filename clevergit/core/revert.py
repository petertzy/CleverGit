"""Revert operations for Git repositories."""

from pathlib import Path
from typing import Optional, List

from clevergit.git.client import GitClient
from clevergit.git.errors import RevertError


def revert(
    repo_path: Path,
    commit_sha: str,
    no_commit: bool = False
) -> None:
    """
    Revert a specific commit.
    
    Args:
        repo_path: Path to the repository
        commit_sha: SHA of the commit to revert
        no_commit: If True, apply changes but don't create commit
        
    Raises:
        RevertError: If revert fails or conflicts occur
    """
    client = GitClient(repo_path)
    
    try:
        client.revert(commit_sha, no_commit=no_commit)
    except Exception as e:
        raise RevertError(f"Failed to revert commit '{commit_sha}': {e}")


def revert_multiple(
    repo_path: Path,
    commit_shas: List[str],
    no_commit: bool = False
) -> None:
    """
    Revert multiple commits in sequence.
    
    Args:
        repo_path: Path to the repository
        commit_shas: List of commit SHAs to revert in order
        no_commit: If True, apply changes but don't create commits
        
    Raises:
        RevertError: If any revert fails or conflicts occur
    """
    for commit_sha in commit_shas:
        revert(repo_path, commit_sha, no_commit=no_commit)


def abort_revert(repo_path: Path) -> None:
    """
    Abort an ongoing revert operation.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        RevertError: If no revert is in progress or abort fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['revert', '--abort'])
        if not result.success:
            raise RevertError(f"Failed to abort revert: {result.error}")
    except Exception as e:
        raise RevertError(f"Failed to abort revert: {e}")


def continue_revert(repo_path: Path) -> None:
    """
    Continue a revert operation after resolving conflicts.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        RevertError: If continue fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['revert', '--continue'])
        if not result.success:
            raise RevertError(f"Failed to continue revert: {result.error}")
    except Exception as e:
        raise RevertError(f"Failed to continue revert: {e}")


def quit_revert(repo_path: Path) -> None:
    """
    Quit revert operation, keeping successfully reverted commits.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        RevertError: If quit fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['revert', '--quit'])
        if not result.success:
            raise RevertError(f"Failed to quit revert: {result.error}")
    except Exception as e:
        raise RevertError(f"Failed to quit revert: {e}")


def is_reverting(repo_path: Path) -> bool:
    """
    Check if a revert operation is in progress.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if revert is in progress, False otherwise
    """
    # Check for REVERT_HEAD file which indicates ongoing revert
    revert_head = repo_path / ".git" / "REVERT_HEAD"
    return revert_head.exists()


def get_revert_head(repo_path: Path) -> Optional[str]:
    """
    Get the SHA of the commit being reverted.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Commit SHA if revert is in progress, None otherwise
    """
    revert_head = repo_path / ".git" / "REVERT_HEAD"
    if revert_head.exists():
        try:
            return revert_head.read_text().strip()
        except Exception:
            return None
    return None
