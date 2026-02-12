"""Commit operations module."""

from typing import List, Optional
from clevergit.git.client import GitClient
from clevergit.git.errors import CommitError, NothingToCommitError, ResetError
from clevergit.models.commit_info import CommitInfo


def commit_all(client: GitClient, message: str, allow_empty: bool = False) -> CommitInfo:
    """Commit all changes (tracked and untracked files)."""
    if not allow_empty and client.is_clean():
        raise NothingToCommitError("No changes to commit")
    client.add_all()
    commit_hash = client.commit(message, allow_empty=allow_empty)
    # Get the commit info
    commits = client.log(max_count=1)
    if commits:
        c = commits[0]
        sha = c.get('sha', commit_hash)
        return CommitInfo(
            sha=sha,
            short_sha=sha[:7],
            message=c.get('message', message),
            author=c.get('author', ''),
            author_email=c.get('author_email', ''),
            date=c.get('date'),
            parents=c.get('parents', [])
        )
    return CommitInfo(sha=commit_hash, short_sha=commit_hash[:7], message=message, author="", author_email="", date=None, parents=[])


def commit_files(client: GitClient, files: List[str], message: str) -> CommitInfo:
    """Commit specific files."""
    if not files:
        raise CommitError("No files specified for commit")
    client.add(files)
    commit_hash = client.commit(message)
    # Get the commit info
    commits = client.log(max_count=1)
    if commits:
        c = commits[0]
        sha = c.get('sha', commit_hash)
        return CommitInfo(
            sha=sha,
            short_sha=sha[:7],
            message=c.get('message', message),
            author=c.get('author', ''),
            author_email=c.get('author_email', ''),
            date=c.get('date'),
            parents=c.get('parents', [])
        )
    return CommitInfo(sha=commit_hash, short_sha=commit_hash[:7], message=message, author="", author_email="", date=None, parents=[])


def amend_commit(client: GitClient, message: Optional[str] = None) -> str:
    """Amend the last commit."""
    return client.amend(message)


def validate_commit_message(message: str) -> bool:
    """Validate commit message format."""
    if not message or not message.strip():
        raise ValueError("Commit message cannot be empty")
    if len(message.strip()) < 3:
        raise ValueError("Commit message too short (minimum 3 characters)")
    return True


def generate_commit_message(client: GitClient) -> str:
    """Generate a simple commit message based on changed files."""
    from clevergit.core.status import get_status
    
    status = get_status(client)
    total_changes = len(status.modified) + len(status.staged) + len(status.untracked) + len(status.deleted)
    
    if total_changes == 0:
        return "chore: no changes"
    
    if total_changes == 1:
        if status.modified:
            return f"update: {status.modified[0].path}"
        if status.staged:
            return f"update: {status.staged[0].path}"
        if status.untracked:
            return f"add: {status.untracked[0].path}"
        if status.deleted:
            return f"remove: {status.deleted[0].path}"
    
    return f"update: {total_changes} files changed"


def revert_commit(client: GitClient, commit_sha: str, no_commit: bool = False) -> Optional[CommitInfo]:
    """
    Revert a commit.
    
    Args:
        client: GitClient instance
        commit_sha: SHA of the commit to revert
        no_commit: If True, apply changes but don't create commit
        
    Returns:
        CommitInfo of the revert commit if created, None if no_commit is True
    """
    from clevergit.core.revert import revert
    
    revert(client.repo_path, commit_sha, no_commit=no_commit)
    
    if not no_commit:
        # Get the revert commit info
        commits = client.log(max_count=1)
        if commits:
            c = commits[0]
            sha = c.get('sha', '')
            return CommitInfo(
                sha=sha,
                short_sha=sha[:7],
                message=c.get('message', ''),
                author=c.get('author', ''),
                author_email=c.get('author_email', ''),
                date=c.get('date'),
                parents=c.get('parents', [])
            )
    return None


def soft_reset(client: GitClient, target: str = "HEAD") -> None:
    """
    Perform a soft reset to the specified target.
    
    Soft reset moves HEAD but keeps staged and working directory changes.
    
    Args:
        client: GitClient instance
        target: Commit SHA/ref to reset to (defaults to HEAD)
    """
    try:
        client.reset(target, mode="soft")
    except Exception as e:
        raise ResetError(f"Soft reset failed: {e}")


def mixed_reset(client: GitClient, target: str = "HEAD") -> None:
    """
    Perform a mixed reset to the specified target.
    
    Mixed reset moves HEAD and resets staging area, but keeps working directory changes.
    This is the default git reset behavior.
    
    Args:
        client: GitClient instance
        target: Commit SHA/ref to reset to (defaults to HEAD)
    """
    try:
        client.reset(target, mode="mixed")
    except Exception as e:
        raise ResetError(f"Mixed reset failed: {e}")


def hard_reset(client: GitClient, target: str = "HEAD") -> None:
    """
    Perform a hard reset to the specified target.
    
    Hard reset moves HEAD, resets staging area, and discards all working directory changes.
    WARNING: This operation is destructive and cannot be easily undone without reflog.
    
    Args:
        client: GitClient instance
        target: Commit SHA/ref to reset to (defaults to HEAD)
    """
    try:
        client.reset(target, mode="hard")
    except Exception as e:
        raise ResetError(f"Hard reset failed: {e}")


def get_reflog(client: GitClient, max_count: Optional[int] = None) -> List[dict]:
    """
    Get reflog entries for undo operations.
    
    Args:
        client: GitClient instance
        max_count: Maximum number of reflog entries to return
        
    Returns:
        List of reflog entries with 'sha', 'message', and 'selector' keys
    """
    try:
        return client.reflog(max_count=max_count)
    except Exception as e:
        raise ResetError(f"Failed to get reflog: {e}")


