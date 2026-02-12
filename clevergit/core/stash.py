"""Stash management module."""

from typing import List, Optional
from clevergit.git.client import GitClient
from clevergit.models.stash_info import StashInfo


def save_stash(client: GitClient, message: Optional[str] = None, include_untracked: bool = False) -> None:
    """
    Save current changes to stash.
    
    Args:
        client: Git client instance
        message: Optional message for the stash
        include_untracked: Whether to include untracked files
    """
    client.stash_save(message, include_untracked)


def list_stashes(client: GitClient) -> List[StashInfo]:
    """
    List all stashes.
    
    Args:
        client: Git client instance
        
    Returns:
        List of StashInfo objects
    """
    stash_dicts = client.stash_list()
    stashes = []
    
    for stash_dict in stash_dicts:
        stashes.append(StashInfo(
            index=stash_dict["index"],
            message=stash_dict["message"],
            branch=stash_dict["branch"],
            commit_sha=stash_dict["sha"]
        ))
    
    return stashes


def apply_stash(client: GitClient, index: int = 0) -> None:
    """
    Apply a stash without removing it.
    
    Args:
        client: Git client instance
        index: Stash index (0 for most recent)
    """
    client.stash_apply(index)


def pop_stash(client: GitClient, index: int = 0) -> None:
    """
    Apply a stash and remove it from the stash list.
    
    Args:
        client: Git client instance
        index: Stash index (0 for most recent)
    """
    client.stash_pop(index)


def drop_stash(client: GitClient, index: int = 0) -> None:
    """
    Remove a stash from the stash list.
    
    Args:
        client: Git client instance
        index: Stash index (0 for most recent)
    """
    client.stash_drop(index)


def clear_stashes(client: GitClient) -> None:
    """
    Remove all stashes.
    
    Args:
        client: Git client instance
    """
    client.stash_clear()


def show_stash(client: GitClient, index: int = 0) -> str:
    """
    Show the changes recorded in a stash as a diff.
    
    Args:
        client: Git client instance
        index: Stash index (0 for most recent)
        
    Returns:
        Diff output showing stash changes
    """
    return client.stash_show(index)
