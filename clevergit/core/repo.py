"""
Repository management module.
"""

from pathlib import Path
from typing import Optional, List
from clevergit.git.client import GitClient
from clevergit.git.errors import RepoNotFoundError, InvalidRepoError
from clevergit.models.file_status import FileStatusList
from clevergit.models.branch_info import BranchInfo


class Repo:
    """Main repository class representing a Git repository."""
    
    def __init__(self, path: Path, client: GitClient):
        self.path = path
        self.client = client
    
    @classmethod
    def open(cls, path: str = ".") -> "Repo":
        """Open an existing Git repository."""
        repo_path = Path(path).resolve()
        if not repo_path.exists():
            raise RepoNotFoundError(f"Path not found: {repo_path}")
        client = GitClient(repo_path)
        if not client.is_repo():
            raise RepoNotFoundError(f"Not a Git repository: {repo_path}")
        return cls(repo_path, client)
    
    @classmethod
    def init(cls, path: str = ".", bare: bool = False) -> "Repo":
        """Initialize a new Git repository."""
        repo_path = Path(path).resolve()
        repo_path.mkdir(parents=True, exist_ok=True)
        client = GitClient(repo_path)
        client.init(bare=bare)
        return cls(repo_path, client)
    
    def status(self) -> FileStatusList:
        """Get the current repository status."""
        from clevergit.core.status import get_status
        return get_status(self.client)
    
    def commit_all(self, message: str, allow_empty: bool = False) -> str:
        """Commit all changes with a message."""
        from clevergit.core.commit import commit_all
        return commit_all(self.client, message, allow_empty)
    
    def commit_files(self, files: List[str], message: str) -> str:
        """Commit specific files."""
        from clevergit.core.commit import commit_files
        return commit_files(self.client, files, message)
    
    def create_branch(self, name: str, start_point: Optional[str] = None) -> BranchInfo:
        """Create a new branch."""
        from clevergit.core.branch import create_branch
        return create_branch(self.client, name, start_point)
    
    def checkout(self, branch_name: str) -> None:
        """Switch to a different branch."""
        from clevergit.core.branch import checkout
        checkout(self.client, branch_name)
    
    def current_branch(self) -> Optional[str]:
        """Get the name of the current branch."""
        return self.client.current_branch()
    
    def list_branches(self, remote: bool = False) -> List[BranchInfo]:
        """List all branches."""
        from clevergit.core.branch import list_branches
        return list_branches(self.client, remote)
    
    def is_clean(self) -> bool:
        """Check if the working directory is clean."""
        return self.client.is_clean()
    
    def log(self, max_count: int = 10) -> List:
        """Get commit log."""
        from clevergit.core.log import get_log
        return get_log(self.path, max_count=max_count)
    
    def __repr__(self) -> str:
        return f"<Repo: {self.path}>"
