"""Repository status analysis module."""

from clevergit.git.client import GitClient
from clevergit.models.file_status import FileStatusList, FileStatus, ChangeType


def get_status(client: GitClient) -> FileStatusList:
    """Get comprehensive repository status."""
    modified, untracked, staged, conflicted, deleted = [], [], [], [], []
    
    status_items = client.status()
    
    for file_path, status_code in status_items.items():
        # Ensure status_code is exactly 2 characters
        if len(status_code) < 2:
            status_code = status_code.ljust(2)
            
        if status_code.startswith('?'):
            untracked.append(FileStatus(path=file_path, change_type=ChangeType.UNTRACKED, staged=False))
        elif 'U' in status_code or 'AA' in status_code or 'DD' in status_code:
            conflicted.append(FileStatus(path=file_path, change_type=ChangeType.CONFLICTED, staged=False))
        elif status_code[0] != ' ' and status_code[0] != '?':
            change_type = _parse_change_type(status_code[0])
            staged.append(FileStatus(path=file_path, change_type=change_type, staged=True))
        elif status_code[1] == 'M':
            modified.append(FileStatus(path=file_path, change_type=ChangeType.MODIFIED, staged=False))
        elif status_code[1] == 'D':
            deleted.append(FileStatus(path=file_path, change_type=ChangeType.DELETED, staged=False))
    
    return FileStatusList(modified=modified, untracked=untracked, staged=staged, 
                         conflicted=conflicted, deleted=deleted)


def _parse_change_type(code: str) -> ChangeType:
    """Parse Git status code to ChangeType."""
    mapping = {'M': ChangeType.MODIFIED, 'A': ChangeType.ADDED, 'D': ChangeType.DELETED,
               'R': ChangeType.RENAMED, 'C': ChangeType.COPIED}
    return mapping.get(code, ChangeType.MODIFIED)


def has_uncommitted_changes(client: GitClient) -> bool:
    """Quick check if there are any uncommitted changes."""
    return not client.is_clean()


def has_conflicts(client: GitClient) -> bool:
    """Check if there are any conflicted files."""
    status = get_status(client)
    return len(status.conflicted) > 0
