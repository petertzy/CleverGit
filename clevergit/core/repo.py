"""
Repository management module.
"""

from pathlib import Path
from typing import Optional, List, Callable
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

    @classmethod
    def clone(
        cls,
        url: str,
        path: str,
        branch: Optional[str] = None,
        depth: Optional[int] = None,
        recurse_submodules: bool = False,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> "Repo":
        """
        Clone a remote Git repository.

        Args:
            url: Repository URL (HTTPS or SSH)
            path: Destination path for the cloned repository
            branch: Specific branch to clone (optional)
            depth: Clone depth for shallow clone (optional)
            recurse_submodules: Clone submodules recursively
            progress_callback: Callback function for progress updates

        Returns:
            Repo instance of the cloned repository
        """
        repo_path = Path(path).resolve()

        # Ensure parent directory exists
        repo_path.parent.mkdir(parents=True, exist_ok=True)

        # Import here to avoid circular dependency
        try:
            from git import Repo as GitPythonRepo
            from git.remote import RemoteProgress

            class ProgressReporter(RemoteProgress):
                """Custom progress reporter for git clone operation."""

                def __init__(self, callback: Optional[Callable[[str], None]] = None):
                    super().__init__()
                    self.callback = callback

                def update(self, op_code, cur_count, max_count=None, message=""):
                    """Update progress."""
                    if self.callback:
                        if max_count:
                            percentage = int((cur_count / max_count) * 100) if max_count > 0 else 0
                            progress_msg = f"{message}: {percentage}% ({cur_count}/{max_count})"
                        else:
                            progress_msg = f"{message}: {cur_count}"
                        self.callback(progress_msg)

            # Prepare clone options
            kwargs = {}
            if branch:
                kwargs["branch"] = branch
            if depth:
                kwargs["depth"] = depth
            if recurse_submodules:
                kwargs["recurse_submodules"] = True

            # Add progress reporter if callback is provided
            if progress_callback:
                kwargs["progress"] = ProgressReporter(progress_callback)
                progress_callback("Starting clone operation...")

            # Perform the clone
            GitPythonRepo.clone_from(url, str(repo_path), **kwargs)

            if progress_callback:
                progress_callback("Clone completed successfully!")

        except ImportError:
            # Fallback to subprocess if GitPython is not available
            import subprocess

            cmd = ["git", "clone"]

            if branch:
                cmd.extend(["--branch", branch])
            if depth:
                cmd.extend(["--depth", str(depth)])
            if recurse_submodules:
                cmd.append("--recurse-submodules")

            cmd.extend([url, str(repo_path)])

            if progress_callback:
                progress_callback(f"Cloning from {url}...")

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                if progress_callback:
                    progress_callback("Clone completed successfully!")
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr or e.stdout or str(e)
                raise Exception(f"Clone failed: {error_msg}")

        # Open and return the cloned repository
        client = GitClient(repo_path)
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

    def delete_branch(self, name: str, force: bool = False) -> None:
        """Delete a branch."""
        from clevergit.core.branch import delete_branch

        delete_branch(self.client, name, force)

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

    def fetch(self, remote: str = "origin", prune: bool = False) -> None:
        """Fetch updates from a remote repository."""
        from clevergit.core.remote import fetch

        fetch(self.path, remote, prune)

    def pull(
        self, remote: str = "origin", branch: Optional[str] = None, rebase: bool = False
    ) -> None:
        """Pull updates from a remote repository."""
        from clevergit.core.remote import pull

        pull(self.path, remote, branch, rebase)

    def push(
        self,
        remote: str = "origin",
        branch: Optional[str] = None,
        force: bool = False,
        set_upstream: bool = False,
    ) -> None:
        """Push commits to a remote repository."""
        from clevergit.core.remote import push

        push(self.path, remote, branch, force, set_upstream)
    
    def stash_save(self, message: Optional[str] = None, include_untracked: bool = False) -> None:
        """Save current changes to stash."""
        from clevergit.core.stash import save_stash
        
        save_stash(self.client, message, include_untracked)
    
    def stash_list(self) -> List:
        """List all stashes."""
        from clevergit.core.stash import list_stashes
        
        return list_stashes(self.client)
    
    def stash_apply(self, index: int = 0) -> None:
        """Apply a stash without removing it."""
        from clevergit.core.stash import apply_stash
        
        apply_stash(self.client, index)
    
    def stash_pop(self, index: int = 0) -> None:
        """Apply a stash and remove it from the stash list."""
        from clevergit.core.stash import pop_stash
        
        pop_stash(self.client, index)
    
    def stash_drop(self, index: int = 0) -> None:
        """Remove a stash from the stash list."""
        from clevergit.core.stash import drop_stash
        
        drop_stash(self.client, index)
    
    def stash_clear(self) -> None:
        """Remove all stashes."""
        from clevergit.core.stash import clear_stashes
        
        clear_stashes(self.client)
    
    def stash_show(self, index: int = 0) -> str:
        """Show the changes recorded in a stash as a diff."""
        from clevergit.core.stash import show_stash
        
        return show_stash(self.client, index)
    
    def create_tag(self, name: str, commit: Optional[str] = None):
        """Create a lightweight tag."""
        from clevergit.core import tag
        return tag.create_tag(self.client, name, commit)
    
    def create_annotated_tag(self, name: str, message: str, commit: Optional[str] = None):
        """Create an annotated tag."""
        from clevergit.core import tag
        return tag.create_annotated_tag(self.client, name, message, commit)
    
    def delete_tag(self, name: str) -> None:
        """Delete a tag."""
        from clevergit.core import tag
        tag.delete_tag(self.client, name)
    
    def list_tags(self):
        """List all tags."""
        from clevergit.core import tag
        return tag.list_tags(self.client)
    
    def push_tag(self, name: str, remote: str = "origin") -> None:
        """Push a specific tag to remote."""
        from clevergit.core import tag
        tag.push_tag(self.client, name, remote)
    
    def push_all_tags(self, remote: str = "origin") -> None:
        """Push all tags to remote."""
        from clevergit.core import tag
        tag.push_all_tags(self.client, remote)
    
    def revert_commit(self, commit_sha: str, no_commit: bool = False):
        """
        Revert a specific commit.
        
        Args:
            commit_sha: SHA of the commit to revert
            no_commit: If True, apply changes but don't create commit
            
        Returns:
            CommitInfo of the revert commit if created, None if no_commit is True
        """
        from clevergit.core.commit import revert_commit
        return revert_commit(self.client, commit_sha, no_commit)
    
    def revert_multiple(self, commit_shas: List[str], no_commit: bool = False) -> None:
        """
        Revert multiple commits in sequence.
        
        Args:
            commit_shas: List of commit SHAs to revert in order
            no_commit: If True, apply changes but don't create commits
        """
        from clevergit.core.revert import revert_multiple
        revert_multiple(self.path, commit_shas, no_commit)
    
    def abort_revert(self) -> None:
        """Abort an ongoing revert operation."""
        from clevergit.core.revert import abort_revert
        abort_revert(self.path)
    
    def continue_revert(self) -> None:
        """Continue a revert operation after resolving conflicts."""
        from clevergit.core.revert import continue_revert
        continue_revert(self.path)
    
    def is_reverting(self) -> bool:
        """Check if a revert operation is in progress."""
        from clevergit.core.revert import is_reverting
        return is_reverting(self.path)
    
    def compare_branches(self, base_branch: str, compare_branch: str):
        """
        Compare two branches.
        
        Args:
            base_branch: The base branch name
            compare_branch: The branch to compare against base
            
        Returns:
            BranchComparison object with detailed comparison information
        """
        from clevergit.core.branch import compare_branches
        return compare_branches(self.client, base_branch, compare_branch)

    def __repr__(self) -> str:
        return f"<Repo: {self.path}>"
