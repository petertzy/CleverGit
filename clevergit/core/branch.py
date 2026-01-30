"""Branch management module."""

from typing import List, Optional
from clevergit.git.client import GitClient
from clevergit.git.errors import BranchError, UncommittedChangesError
from clevergit.models.branch_info import BranchInfo


def create_branch(client: GitClient, name: str, start_point: Optional[str] = None) -> BranchInfo:
    """Create a new branch."""
    if not name or not name.strip():
        raise BranchError("Branch name cannot be empty")
    
    if not _is_valid_branch_name(name):
        raise BranchError(f"Invalid branch name: {name}")
    
    existing_branches = [b.name for b in list_branches(client, remote=False)]
    if name in existing_branches:
        raise BranchError(f"Branch already exists: {name}")
    
    client.create_branch(name, start_point)
    
    return BranchInfo(name=name, commit_sha=client.get_branch_commit(name),
                     is_current=False, is_remote=False)


def delete_branch(client: GitClient, name: str, force: bool = False) -> None:
    """Delete a branch."""
    current = client.current_branch()
    if current == name:
        raise BranchError(f"Cannot delete current branch: {name}")
    client.delete_branch(name, force=force)


def rename_branch(client: GitClient, old_name: str, new_name: str) -> BranchInfo:
    """Rename a branch."""
    if not _is_valid_branch_name(new_name):
        raise BranchError(f"Invalid branch name: {new_name}")
    client.rename_branch(old_name, new_name)
    return BranchInfo(name=new_name, commit_sha=client.get_branch_commit(new_name),
                     is_current=client.current_branch() == new_name, is_remote=False)


def checkout(client: GitClient, branch_name: str, create: bool = False) -> None:
    """Switch to a different branch."""
    if not client.is_clean():
        raise UncommittedChangesError("Cannot switch branches with uncommitted changes. "
                                     "Commit or stash your changes first.")
    if create:
        client.create_branch(branch_name)
    client.checkout(branch_name)


def list_branches(client: GitClient, remote: bool = False) -> List[BranchInfo]:
    """List all branches."""
    current = client.current_branch()
    branches = []
    
    for branch_name in client.list_branches():
        branches.append(BranchInfo(name=branch_name, commit_sha=client.get_branch_commit(branch_name),
                                  is_current=(branch_name == current), is_remote=False))
    
    if remote:
        for branch_name in client.list_remote_branches():
            branches.append(BranchInfo(name=branch_name, commit_sha=client.get_branch_commit(branch_name),
                                      is_current=False, is_remote=True))
    
    return branches


def get_current_branch(client: GitClient) -> Optional[BranchInfo]:
    """Get information about the current branch."""
    current = client.current_branch()
    if not current:
        return None
    return BranchInfo(name=current, commit_sha=client.get_branch_commit(current),
                     is_current=True, is_remote=False)


def _is_valid_branch_name(name: str) -> bool:
    """Validate branch name according to Git rules."""
    if not name:
        return False
    invalid_chars = [' ', '~', '^', ':', '?', '*', '[', '\\']
    if any(char in name for char in invalid_chars):
        return False
    if name.startswith('.') or name.endswith('.'):
        return False
    if name.endswith('.lock'):
        return False
    if '..' in name:
        return False
    return True
