"""Cherry-pick operations for Git repositories."""

from pathlib import Path
from typing import Optional, List

from clevergit.git.client import GitClient
from clevergit.git.errors import CherryPickError


def cherry_pick(
    repo_path: Path,
    commit_sha: str,
    no_commit: bool = False
) -> None:
    """
    Cherry-pick a specific commit onto the current branch.
    
    Args:
        repo_path: Path to the repository
        commit_sha: SHA of the commit to cherry-pick
        no_commit: If True, apply changes but don't create commit
        
    Raises:
        CherryPickError: If cherry-pick fails or conflicts occur
    """
    client = GitClient(repo_path)
    
    try:
        client.cherry_pick(commit_sha, no_commit=no_commit)
    except Exception as e:
        raise CherryPickError(f"Failed to cherry-pick commit '{commit_sha}': {e}")


def cherry_pick_multiple(
    repo_path: Path,
    commit_shas: List[str],
    no_commit: bool = False
) -> None:
    """
    Cherry-pick multiple commits in sequence.
    
    Args:
        repo_path: Path to the repository
        commit_shas: List of commit SHAs to cherry-pick in order
        no_commit: If True, apply changes but don't create commits
        
    Raises:
        CherryPickError: If any cherry-pick fails or conflicts occur
    """
    for commit_sha in commit_shas:
        cherry_pick(repo_path, commit_sha, no_commit=no_commit)


def abort_cherry_pick(repo_path: Path) -> None:
    """
    Abort an ongoing cherry-pick operation.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        CherryPickError: If no cherry-pick is in progress or abort fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['cherry-pick', '--abort'])
        if not result.success:
            raise CherryPickError(f"Failed to abort cherry-pick: {result.error}")
    except Exception as e:
        raise CherryPickError(f"Failed to abort cherry-pick: {e}")


def continue_cherry_pick(repo_path: Path) -> None:
    """
    Continue a cherry-pick operation after resolving conflicts.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        CherryPickError: If continue fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['cherry-pick', '--continue'])
        if not result.success:
            raise CherryPickError(f"Failed to continue cherry-pick: {result.error}")
    except Exception as e:
        raise CherryPickError(f"Failed to continue cherry-pick: {e}")


def quit_cherry_pick(repo_path: Path) -> None:
    """
    Quit cherry-pick operation, keeping successfully cherry-picked commits.
    
    Args:
        repo_path: Path to the repository
        
    Raises:
        CherryPickError: If quit fails
    """
    client = GitClient(repo_path)
    
    try:
        result = client.run_command(['cherry-pick', '--quit'])
        if not result.success:
            raise CherryPickError(f"Failed to quit cherry-pick: {result.error}")
    except Exception as e:
        raise CherryPickError(f"Failed to quit cherry-pick: {e}")


def is_cherry_picking(repo_path: Path) -> bool:
    """
    Check if a cherry-pick operation is in progress.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if cherry-pick is in progress, False otherwise
    """
    # Check for CHERRY_PICK_HEAD file which indicates ongoing cherry-pick
    cherry_pick_head = repo_path / ".git" / "CHERRY_PICK_HEAD"
    return cherry_pick_head.exists()


def get_cherry_pick_head(repo_path: Path) -> Optional[str]:
    """
    Get the SHA of the commit being cherry-picked.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Commit SHA if cherry-pick is in progress, None otherwise
    """
    cherry_pick_head = repo_path / ".git" / "CHERRY_PICK_HEAD"
    if cherry_pick_head.exists():
        try:
            return cherry_pick_head.read_text().strip()
        except Exception:
            return None
    return None
