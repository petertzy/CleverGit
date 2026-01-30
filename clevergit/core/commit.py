"""Commit operations module."""

from typing import List, Optional
from clevergit.git.client import GitClient
from clevergit.git.errors import CommitError, NothingToCommitError


def commit_all(client: GitClient, message: str, allow_empty: bool = False) -> str:
    """Commit all changes (tracked and untracked files)."""
    if not allow_empty and client.is_clean():
        raise NothingToCommitError("No changes to commit")
    client.add_all()
    return client.commit(message, allow_empty=allow_empty)


def commit_files(client: GitClient, files: List[str], message: str) -> str:
    """Commit specific files."""
    if not files:
        raise CommitError("No files specified for commit")
    client.add(files)
    return client.commit(message)


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
