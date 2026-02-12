"""
Git client adapter module.

This module provides a unified interface to interact with Git,
using GitPython as the primary method and subprocess as fallback.
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import re

try:
    from git import Repo as GitPythonRepo
    from git.exc import GitCommandError, InvalidGitRepositoryError
    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False
    GitPythonRepo = None
    GitCommandError = Exception
    InvalidGitRepositoryError = Exception


@dataclass
class CommandResult:
    """Result of a git command execution."""
    success: bool
    output: str = ""
    error: str = ""


class GitClient:
    """
    Git client that wraps GitPython or subprocess.
    
    This provides a consistent interface for Git operations,
    abstracting away the underlying implementation.
    """
    
    def __init__(self, repo_path: Path):
        """
        Initialize Git client.
        
        Args:
            repo_path: Path to the repository
        """
        self.repo_path = repo_path
        self._repo = None
        
        if HAS_GITPYTHON:
            try:
                self._repo = GitPythonRepo(repo_path)
            except InvalidGitRepositoryError:
                self._repo = None
    
    def is_repo(self) -> bool:
        """Check if the path is a valid Git repository."""
        if HAS_GITPYTHON and self._repo:
            return True
        
        # Fallback: check for .git directory
        git_dir = self.repo_path / ".git"
        return git_dir.exists()
    
    def init(self, bare: bool = False) -> None:
        """Initialize a new Git repository."""
        if HAS_GITPYTHON:
            self._repo = GitPythonRepo.init(self.repo_path, bare=bare)
        else:
            cmd = ["git", "init"]
            if bare:
                cmd.append("--bare")
            self._run_command(cmd)
    
    def status(self) -> Dict[str, str]:
        """
        Get repository status.
        
        Returns:
            Dict mapping file paths to status codes
        """
        if HAS_GITPYTHON and self._repo:
            status_dict = {}
            # Untracked files
            for item in self._repo.untracked_files:
                status_dict[item] = "??"
            
            # Changed files
            diff_index = self._repo.index.diff(None)
            for diff in diff_index:
                status_dict[diff.a_path] = " M"
            
            # Staged files - handle initial commit case
            try:
                diff_staged = self._repo.index.diff("HEAD")
                for diff in diff_staged:
                    if diff.change_type == "A":
                        status_dict[diff.b_path] = "A "
                    elif diff.change_type == "M":
                        status_dict[diff.a_path] = "M "
                    elif diff.change_type == "D":
                        status_dict[diff.a_path] = "D "
            except Exception:
                # No HEAD yet (initial commit), check staged files directly
                for entry in self._repo.index.entries:
                    status_dict[entry[0]] = "A "
            
            return status_dict
        
        # Fallback to subprocess
        output = self._run_command(["git", "status", "--porcelain"])
        status_dict = {}
        for line in output.strip().split("\n"):
            if line:
                status_code = line[:2]
                file_path = line[3:]
                status_dict[file_path] = status_code
        return status_dict
    
    def is_clean(self) -> bool:
        """Check if working directory is clean."""
        if HAS_GITPYTHON and self._repo:
            return not self._repo.is_dirty(untracked_files=True)
        
        output = self._run_command(["git", "status", "--porcelain"])
        return not output.strip()
    
    def add(self, files: List[str]) -> None:
        """Stage specific files."""
        if HAS_GITPYTHON and self._repo:
            self._repo.index.add(files)
        else:
            self._run_command(["git", "add"] + files)
    
    def add_all(self) -> None:
        """Stage all changes."""
        if HAS_GITPYTHON and self._repo:
            self._repo.git.add(A=True)
        else:
            self._run_command(["git", "add", "-A"])
    
    def commit(self, message: str, allow_empty: bool = False) -> str:
        """
        Create a commit.
        
        Returns:
            Commit SHA
        """
        if HAS_GITPYTHON and self._repo:
            commit = self._repo.index.commit(message, skip_hooks=False)
            return commit.hexsha
        
        cmd = ["git", "commit", "-m", message]
        if allow_empty:
            cmd.append("--allow-empty")
        self._run_command(cmd)
        return self.get_head_sha()
    
    def amend(self, message: Optional[str] = None) -> str:
        """Amend the last commit."""
        if HAS_GITPYTHON and self._repo:
            if message:
                self._repo.git.commit(amend=True, m=message)
            else:
                self._repo.git.commit(amend=True, no_edit=True)
            return self._repo.head.commit.hexsha
        
        cmd = ["git", "commit", "--amend"]
        if message:
            cmd.extend(["-m", message])
        else:
            cmd.append("--no-edit")
        self._run_command(cmd)
        return self.get_head_sha()
    
    def current_branch(self) -> Optional[str]:
        """Get current branch name."""
        if HAS_GITPYTHON and self._repo:
            try:
                return self._repo.active_branch.name
            except TypeError:
                return None  # Detached HEAD
        
        try:
            output = self._run_command(["git", "branch", "--show-current"])
            return output.strip() or None
        except Exception:
            return None
    
    def list_branches(self) -> List[str]:
        """List local branches."""
        if HAS_GITPYTHON and self._repo:
            return [branch.name for branch in self._repo.branches]
        
        output = self._run_command(["git", "branch"])
        branches = []
        for line in output.strip().split("\n"):
            branch = line.strip().lstrip("* ")
            if branch:
                branches.append(branch)
        return branches
    
    def list_remote_branches(self) -> List[str]:
        """List remote branches."""
        if HAS_GITPYTHON and self._repo:
            # Filter out symbolic refs like origin/HEAD
            return [ref.name for ref in self._repo.remote().refs 
                    if not ref.name.endswith('/HEAD')]
        
        output = self._run_command(["git", "branch", "-r"])
        # Filter out symbolic refs (marked with ->)
        return [line.strip() for line in output.strip().split("\n") 
                if line.strip() and '->' not in line]
    
    def create_branch(self, name: str, start_point: Optional[str] = None) -> None:
        """Create a new branch."""
        if HAS_GITPYTHON and self._repo:
            if start_point:
                self._repo.create_head(name, start_point)
            else:
                self._repo.create_head(name)
        else:
            cmd = ["git", "branch", name]
            if start_point:
                cmd.append(start_point)
            self._run_command(cmd)
    
    def delete_branch(self, name: str, force: bool = False) -> None:
        """Delete a branch."""
        # Normalize branch name - strip refs/heads/ prefix if present
        if name.startswith("refs/heads/"):
            name = name[len("refs/heads/"):]
        
        if HAS_GITPYTHON and self._repo:
            self._repo.delete_head(name, force=force)
        else:
            flag = "-D" if force else "-d"
            self._run_command(["git", "branch", flag, name])
    
    def rename_branch(self, old_name: str, new_name: str) -> None:
        """Rename a branch."""
        if HAS_GITPYTHON and self._repo:
            branch = self._repo.branches[old_name]
            branch.rename(new_name)
        else:
            self._run_command(["git", "branch", "-m", old_name, new_name])
    
    def checkout(self, branch_name: str) -> None:
        """Switch to a branch."""
        if HAS_GITPYTHON and self._repo:
            self._repo.git.checkout(branch_name)
        else:
            self._run_command(["git", "checkout", branch_name])
    
    def get_branch_commit(self, branch_name: str) -> str:
        """Get the commit SHA of a branch."""
        if HAS_GITPYTHON and self._repo:
            # Try local branches first
            try:
                return self._repo.branches[branch_name].commit.hexsha
            except (IndexError, KeyError):
                pass
            
            # Try remote references
            try:
                for ref in self._repo.remote().refs:
                    if ref.name == branch_name:
                        return ref.commit.hexsha
            except (ValueError, AttributeError):
                # No remote configured or other issue, fall through to subprocess
                pass
        
        output = self._run_command(["git", "rev-parse", branch_name])
        return output.strip()
    
    def get_head_sha(self) -> str:
        """Get HEAD commit SHA."""
        if HAS_GITPYTHON and self._repo:
            return self._repo.head.commit.hexsha
        
        output = self._run_command(["git", "rev-parse", "HEAD"])
        return output.strip()
    
    def merge(self, branch: str, strategy: Optional[str] = None, no_ff: bool = False) -> str:
        """Merge a branch."""
        if HAS_GITPYTHON and self._repo:
            kwargs = {}
            if strategy:
                kwargs['strategy'] = strategy
            if no_ff:
                kwargs['no_ff'] = True
            self._repo.git.merge(branch, **kwargs)
            return self._repo.head.commit.hexsha
        
        cmd = ["git", "merge", branch]
        if strategy:
            cmd.extend(["-s", strategy])
        if no_ff:
            cmd.append("--no-ff")
        self._run_command(cmd)
        return self.get_head_sha()
    
    def abort_merge(self) -> None:
        """Abort an ongoing merge."""
        if HAS_GITPYTHON and self._repo:
            self._repo.git.merge(abort=True)
        else:
            self._run_command(["git", "merge", "--abort"])
    
    def rebase(self, branch: str, interactive: bool = False) -> None:
        """Rebase onto a branch."""
        if HAS_GITPYTHON and self._repo:
            if interactive:
                self._repo.git.rebase(branch, interactive=True)
            else:
                self._repo.git.rebase(branch)
        else:
            cmd = ["git", "rebase"]
            if interactive:
                cmd.append("-i")
            cmd.append(branch)
            self._run_command(cmd)
    
    def continue_rebase(self) -> None:
        """Continue rebase after resolving conflicts."""
        if HAS_GITPYTHON and self._repo:
            self._repo.git.rebase(continue_=True)
        else:
            self._run_command(["git", "rebase", "--continue"])
    
    def abort_rebase(self) -> None:
        """Abort an ongoing rebase."""
        if HAS_GITPYTHON and self._repo:
            self._repo.git.rebase(abort=True)
        else:
            self._run_command(["git", "rebase", "--abort"])
    
    def can_fast_forward(self, branch: str) -> bool:
        """Check if merge would be fast-forward."""
        try:
            if HAS_GITPYTHON and self._repo:
                merge_base = self._repo.merge_base(self._repo.head, branch)[0]
                return merge_base.hexsha == self._repo.head.commit.hexsha
            
            merge_base = self.merge_base("HEAD", branch)
            head_sha = self.get_head_sha()
            return merge_base == head_sha
        except Exception:
            return False
    
    def merge_base(self, ref1: str, ref2: str) -> str:
        """Find merge base of two refs."""
        if HAS_GITPYTHON and self._repo:
            base = self._repo.merge_base(ref1, ref2)[0]
            return base.hexsha
        
        output = self._run_command(["git", "merge-base", ref1, ref2])
        return output.strip()
    
    def fetch(self, remote: str = "origin", prune: bool = False) -> None:
        """Fetch from remote."""
        if HAS_GITPYTHON and self._repo:
            self._repo.remote(remote).fetch(prune=prune)
        else:
            cmd = ["git", "fetch", remote]
            if prune:
                cmd.append("--prune")
            self._run_command(cmd)
    
    def pull(self, remote: str = "origin", branch: Optional[str] = None, rebase: bool = False) -> None:
        """Pull from remote."""
        if HAS_GITPYTHON and self._repo:
            kwargs = {}
            if rebase:
                kwargs['rebase'] = True
            if branch:
                self._repo.remote(remote).pull(branch, **kwargs)
            else:
                self._repo.remote(remote).pull(**kwargs)
        else:
            cmd = ["git", "pull", remote]
            if branch:
                cmd.append(branch)
            if rebase:
                cmd.append("--rebase")
            self._run_command(cmd)
    
    def push(self, remote: str = "origin", branch: Optional[str] = None, force: bool = False, set_upstream: bool = False) -> None:
        """Push to remote."""
        if HAS_GITPYTHON and self._repo:
            ref = branch if branch else self.current_branch()
            kwargs = {}
            if force:
                kwargs['force'] = True
            if set_upstream:
                kwargs['set_upstream'] = True
            self._repo.remote(remote).push(ref, **kwargs)
        else:
            cmd = ["git", "push", remote]
            if branch:
                cmd.append(branch)
            if force:
                cmd.append("--force")
            if set_upstream:
                cmd.append("--set-upstream")
            self._run_command(cmd)
    
    def list_remotes(self) -> Dict[str, str]:
        """List remotes."""
        if HAS_GITPYTHON and self._repo:
            return {remote.name: list(remote.urls)[0] for remote in self._repo.remotes}
        
        output = self._run_command(["git", "remote", "-v"])
        remotes = {}
        for line in output.strip().split("\n"):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    remotes[parts[0]] = parts[1]
        return remotes
    
    def add_remote(self, name: str, url: str) -> None:
        """Add a remote."""
        if HAS_GITPYTHON and self._repo:
            self._repo.create_remote(name, url)
        else:
            self._run_command(["git", "remote", "add", name, url])
    
    def remove_remote(self, name: str) -> None:
        """Remove a remote."""
        if HAS_GITPYTHON and self._repo:
            self._repo.delete_remote(name)
        else:
            self._run_command(["git", "remote", "remove", name])
    
    def get_tracking_info(self, branch: str) -> Tuple[int, int]:
        """Get ahead/behind counts for a branch. Returns: Tuple of (ahead, behind) counts"""
        try:
            output = self._run_command(["git", "rev-list", "--left-right", "--count", f"{branch}...@{{upstream}}"])
            parts = output.strip().split()
            ahead = int(parts[0])
            behind = int(parts[1])
            return ahead, behind
        except Exception:
            return 0, 0
    
    def commits_ahead(self, branch: str) -> List[str]:
        """Get list of commits ahead of upstream."""
        try:
            output = self._run_command(["git", "rev-list", f"@{{upstream}}..{branch}"])
            return [line.strip() for line in output.strip().split("\n") if line.strip()]
        except Exception:
            return []
    
    def commits_behind(self, branch: str) -> List[str]:
        """Get list of commits behind upstream."""
        try:
            output = self._run_command(["git", "rev-list", f"{branch}..@{{upstream}}"])
            return [line.strip() for line in output.strip().split("\n") if line.strip()]
        except Exception:
            return []
    
    def log(self, max_count: Optional[int] = None, branch: Optional[str] = None, author: Optional[str] = None, since: Optional[datetime] = None, until: Optional[datetime] = None) -> List[dict]:
        """Get commit log."""
        if HAS_GITPYTHON and self._repo:
            kwargs = {}
            if max_count:
                kwargs['max_count'] = max_count
            if author:
                kwargs['author'] = author
            if since:
                kwargs['since'] = since
            if until:
                kwargs['until'] = until
            
            ref = branch if branch else "HEAD"
            commits = list(self._repo.iter_commits(ref, **kwargs))
            
            return [{"sha": c.hexsha, "message": c.message.strip(), "author": c.author.name, "author_email": c.author.email, "date": c.committed_datetime, "parents": [p.hexsha for p in c.parents]} for c in commits]
        
        # Fallback implementation
        cmd = ["git", "log", "--format=%H|%an|%ae|%ct|%s"]
        if max_count:
            cmd.append(f"-{max_count}")
        if branch:
            cmd.append(branch)
        if author:
            cmd.extend(["--author", author])
        
        output = self._run_command(cmd)
        commits = []
        for line in output.strip().split("\n"):
            if line:
                parts = line.split("|", 4)
                if len(parts) >= 5:
                    commits.append({"sha": parts[0], "author": parts[1], "author_email": parts[2], "date": datetime.fromtimestamp(int(parts[3])), "message": parts[4], "parents": []})
        return commits
    
    def show_commit(self, commit_sha: str) -> dict:
        """Get detailed commit information."""
        cmd = ["git", "show", "-s", "--format=%H|%an|%ae|%ct|%s", commit_sha]
        output = self._run_command(cmd)
        
        parts = output.strip().split("|", 4)
        return {"sha": parts[0], "author": parts[1], "author_email": parts[2], "date": datetime.fromtimestamp(int(parts[3])), "message": parts[4], "parents": []}
    
    def file_log(self, file_path: str, max_count: Optional[int] = None) -> List[dict]:
        """Get commit history for a file."""
        cmd = ["git", "log", "--format=%H|%an|%ae|%ct|%s"]
        if max_count:
            cmd.append(f"-{max_count}")
        cmd.append("--")
        cmd.append(file_path)
        
        output = self._run_command(cmd)
        commits = []
        for line in output.strip().split("\n"):
            if line:
                parts = line.split("|", 4)
                if len(parts) >= 5:
                    commits.append({"sha": parts[0], "author": parts[1], "author_email": parts[2], "date": datetime.fromtimestamp(int(parts[3])), "message": parts[4], "parents": []})
        return commits
    
    def diff(self, commit1: Optional[str] = None, commit2: Optional[str] = None, file_path: Optional[str] = None) -> str:
        """Get diff."""
        cmd = ["git", "diff"]
        if commit1:
            cmd.append(commit1)
        if commit2:
            cmd.append(commit2)
        if file_path:
            cmd.extend(["--", file_path])
        
        return self._run_command(cmd)
    
    def apply_patch(self, patch: str, cached: bool = False, reverse: bool = False) -> None:
        """
        Apply a patch to the working directory or index.
        
        Args:
            patch: The patch content to apply
            cached: If True, apply to index (stage changes)
            reverse: If True, reverse the patch (unstage changes)
            
        Raises:
            Exception: If patch application fails
        """
        cmd = ["git", "apply"]
        if cached:
            cmd.append("--cached")
        if reverse:
            cmd.append("--reverse")
        cmd.append("--unidiff-zero")  # Allow context-free patches
        cmd.append("-")  # Read from stdin
        
        # Ensure patch ends with newline
        if not patch.endswith("\n"):
            patch = patch + "\n"
        
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            input=patch,
            text=True,
            capture_output=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to apply patch: {result.stderr}")
    
    def stage_hunk(self, hunk_patch: str) -> None:
        """
        Stage a specific hunk.
        
        Args:
            hunk_patch: The complete patch including file headers and hunk
        """
        self.apply_patch(hunk_patch, cached=True)
    
    def unstage_hunk(self, hunk_patch: str) -> None:
        """
        Unstage a specific hunk.
        
        Args:
            hunk_patch: The complete patch including file headers and hunk
        """
        self.apply_patch(hunk_patch, cached=True, reverse=True)
    
    def search_log(self, query: str, max_count: Optional[int] = None) -> List[dict]:
        """Search commits by message."""
        cmd = ["git", "log", "--format=%H|%an|%ae|%ct|%s", f"--grep={query}"]
        if max_count:
            cmd.append(f"-{max_count}")
        
        output = self._run_command(cmd)
        commits = []
        for line in output.strip().split("\n"):
            if line:
                parts = line.split("|", 4)
                if len(parts) >= 5:
                    commits.append({"sha": parts[0], "author": parts[1], "author_email": parts[2], "date": datetime.fromtimestamp(int(parts[3])), "message": parts[4], "parents": []})
        return commits
    
    def get_contributors(self) -> List[dict]:
        """Get list of contributors."""
        output = self._run_command(["git", "shortlog", "-sn", "--all"])
        contributors = []
        for line in output.strip().split("\n"):
            if line:
                parts = line.strip().split(None, 1)
                if len(parts) >= 2:
                    contributors.append({"commits": int(parts[0]), "name": parts[1]})
        return contributors
    
    def stash_save(self, message: Optional[str] = None, include_untracked: bool = False) -> None:
        """
        Save current changes to stash.
        
        Args:
            message: Optional message for the stash
            include_untracked: Whether to include untracked files
        """
        cmd = ["git", "stash", "push"]
        if include_untracked:
            cmd.append("--include-untracked")
        if message:
            cmd.extend(["-m", message])
        self._run_command(cmd)
    
    def stash_list(self) -> List[dict]:
        """
        List all stashes.
        
        Returns:
            List of stash entries with index, message, branch, and sha
        """
        output = self._run_command(["git", "stash", "list", "--format=%gd|%gs|%H|%cr"])
        stashes = []
        for idx, line in enumerate(output.strip().split("\n")):
            if line:
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    # Extract branch from message like "WIP on main: abc1234 message"
                    message = parts[1]
                    branch = ""
                    if message.startswith("WIP on ") or message.startswith("On "):
                        # Parse branch name from stash message
                        msg_parts = message.split(":", 1)
                        if len(msg_parts) >= 1:
                            branch_part = msg_parts[0].replace("WIP on ", "").replace("On ", "").strip()
                            branch = branch_part
                    
                    stashes.append({
                        "index": idx,
                        "ref": parts[0],
                        "message": message,
                        "branch": branch,
                        "sha": parts[2],
                        "date": parts[3] if len(parts) > 3 else ""
                    })
        return stashes
    
    def stash_apply(self, index: int = 0) -> None:
        """
        Apply a stash without removing it.
        
        Args:
            index: Stash index (0 for most recent)
        """
        if HAS_GITPYTHON and self._repo:
            self._repo.git.stash("apply", f"stash@{{{index}}}")
        else:
            self._run_command(["git", "stash", "apply", f"stash@{{{index}}}"])
    
    def stash_pop(self, index: int = 0) -> None:
        """
        Apply a stash and remove it from the stash list.
        
        Args:
            index: Stash index (0 for most recent)
        """
        if HAS_GITPYTHON and self._repo:
            self._repo.git.stash("pop", f"stash@{{{index}}}")
        else:
            self._run_command(["git", "stash", "pop", f"stash@{{{index}}}"])
    
    def stash_drop(self, index: int = 0) -> None:
        """
        Remove a stash from the stash list.
        
        Args:
            index: Stash index (0 for most recent)
        """
        if HAS_GITPYTHON and self._repo:
            self._repo.git.stash("drop", f"stash@{{{index}}}")
        else:
            self._run_command(["git", "stash", "drop", f"stash@{{{index}}}"])
    
    def stash_clear(self) -> None:
        """Remove all stashes."""
        if HAS_GITPYTHON and self._repo:
            self._repo.git.stash("clear")
        else:
            self._run_command(["git", "stash", "clear"])
    
    def stash_show(self, index: int = 0) -> str:
        """
        Show the changes recorded in a stash as a diff.
        
        Args:
            index: Stash index (0 for most recent)
            
        Returns:
            Diff output showing stash changes
        """
        if HAS_GITPYTHON and self._repo:
            return self._repo.git.stash("show", "-p", f"stash@{{{index}}}")
        else:
            return self._run_command(["git", "stash", "show", "-p", f"stash@{{{index}}}"])
    
    def create_tag(self, name: str, commit: Optional[str] = None) -> None:
        """
        Create a lightweight tag.
        
        Args:
            name: Tag name
            commit: Optional commit SHA/ref to tag (defaults to HEAD)
        """
        if HAS_GITPYTHON and self._repo:
            if commit:
                self._repo.create_tag(name, ref=commit)
            else:
                self._repo.create_tag(name)
        else:
            cmd = ["git", "tag", name]
            if commit:
                cmd.append(commit)
            self._run_command(cmd)
    
    def create_annotated_tag(self, name: str, message: str, commit: Optional[str] = None) -> None:
        """
        Create an annotated tag.
        
        Args:
            name: Tag name
            message: Tag message
            commit: Optional commit SHA/ref to tag (defaults to HEAD)
        """
        if HAS_GITPYTHON and self._repo:
            if commit:
                self._repo.create_tag(name, ref=commit, message=message)
            else:
                self._repo.create_tag(name, message=message)
        else:
            cmd = ["git", "tag", "-a", name, "-m", message]
            if commit:
                cmd.append(commit)
            self._run_command(cmd)
    
    def list_tags(self) -> List[Dict[str, str]]:
        """
        List all tags with their information.
        
        Returns:
            List of dicts containing tag information
        """
        tags = []
        
        if HAS_GITPYTHON and self._repo:
            for tag in self._repo.tags:
                tag_info = {
                    "name": tag.name,
                    "commit_sha": str(tag.commit),
                    "is_annotated": hasattr(tag.tag, "message"),
                    "message": None,
                    "tagger": None,
                    "date": None,
                }
                
                # Check if annotated tag
                if hasattr(tag, "tag") and tag.tag:
                    tag_info["is_annotated"] = True
                    tag_info["message"] = tag.tag.message if hasattr(tag.tag, "message") else None
                    if hasattr(tag.tag, "tagger") and tag.tag.tagger:
                        tag_info["tagger"] = tag.tag.tagger.name
                        # Convert timestamp to datetime
                        if hasattr(tag.tag.tagger, "authored_datetime"):
                            tag_info["date"] = tag.tag.tagger.authored_datetime
                
                tags.append(tag_info)
        else:
            # Use subprocess to get tag list
            output = self._run_command(["git", "tag", "-l"])
            for tag_name in output.strip().split("\n"):
                if not tag_name:
                    continue
                
                tag_info = {
                    "name": tag_name,
                    "commit_sha": "",
                    "is_annotated": False,
                    "message": None,
                    "tagger": None,
                    "date": None,
                }
                
                # Get commit SHA
                try:
                    sha = self._run_command(["git", "rev-list", "-n", "1", tag_name]).strip()
                    tag_info["commit_sha"] = sha
                except Exception:
                    pass
                
                # Check if annotated and get info
                try:
                    tag_type = self._run_command(["git", "cat-file", "-t", tag_name]).strip()
                    if tag_type == "tag":
                        tag_info["is_annotated"] = True
                        # Get tag details
                        tag_content = self._run_command(["git", "cat-file", "tag", tag_name])
                        
                        # Parse tag content
                        lines = tag_content.split("\n")
                        message_lines = []
                        in_message = False
                        
                        for line in lines:
                            if in_message:
                                message_lines.append(line)
                            elif line.startswith("tagger "):
                                # Parse tagger line: "tagger Name <email> timestamp timezone"
                                tagger_match = re.match(r"tagger\s+([^<]+)", line)
                                if tagger_match:
                                    tag_info["tagger"] = tagger_match.group(1).strip()
                                
                                # Parse timestamp
                                timestamp_match = re.search(r"(\d+)\s+[+-]\d{4}", line)
                                if timestamp_match:
                                    timestamp = int(timestamp_match.group(1))
                                    tag_info["date"] = datetime.fromtimestamp(timestamp)
                            elif not line.strip():
                                in_message = True
                        
                        if message_lines:
                            tag_info["message"] = "\n".join(message_lines).strip()
                except Exception:
                    pass
                
                tags.append(tag_info)
        
        return tags
    
    def delete_tag(self, name: str) -> None:
        """
        Delete a tag.
        
        Args:
            name: Tag name to delete
        """
        if HAS_GITPYTHON and self._repo:
            self._repo.delete_tag(name)
        else:
            self._run_command(["git", "tag", "-d", name])
    
    def push_tag(self, name: str, remote: str = "origin") -> None:
        """
        Push a specific tag to remote.
        
        Args:
            name: Tag name to push
            remote: Remote name (defaults to "origin")
        """
        if HAS_GITPYTHON and self._repo:
            self._repo.remotes[remote].push(name)
        else:
            self._run_command(["git", "push", remote, name])
    
    def push_all_tags(self, remote: str = "origin") -> None:
        """
        Push all tags to remote.
        
        Args:
            remote: Remote name (defaults to "origin")
        """
        if HAS_GITPYTHON and self._repo:
            self._repo.remotes[remote].push(tags=True)
        else:
            self._run_command(["git", "push", remote, "--tags"])
    
    def cherry_pick(self, commit_sha: str, no_commit: bool = False) -> None:
        """
        Cherry-pick a commit.
        
        Args:
            commit_sha: SHA of commit to cherry-pick
            no_commit: If True, apply changes but don't commit
        """
        if HAS_GITPYTHON and self._repo:
            kwargs = {}
            if no_commit:
                kwargs['n'] = True
            self._repo.git.cherry_pick(commit_sha, **kwargs)
        else:
            cmd = ["git", "cherry-pick", commit_sha]
            if no_commit:
                cmd.append("-n")
            self._run_command(cmd)
    
    def revert(self, commit_sha: str, no_commit: bool = False) -> None:
        """
        Revert a commit.
        
        Args:
            commit_sha: SHA of commit to revert
            no_commit: If True, apply changes but don't commit
        """
        if HAS_GITPYTHON and self._repo:
            kwargs = {}
            if no_commit:
                kwargs['n'] = True
            self._repo.git.revert(commit_sha, **kwargs)
        else:
            cmd = ["git", "revert", commit_sha]
            if no_commit:
                cmd.append("-n")
            self._run_command(cmd)
    
    def reset(self, target: str = "HEAD", mode: str = "mixed") -> None:
        """
        Reset HEAD to target with specified mode.
        
        Args:
            target: Commit SHA/ref to reset to (defaults to HEAD)
            mode: Reset mode - 'soft', 'mixed', or 'hard' (defaults to 'mixed')
        """
        valid_modes = ['soft', 'mixed', 'hard']
        if mode not in valid_modes:
            raise ValueError(f"Invalid reset mode: {mode}. Must be one of {valid_modes}")
        
        if HAS_GITPYTHON and self._repo:
            self._repo.git.reset(f"--{mode}", target)
        else:
            self._run_command(["git", "reset", f"--{mode}", target])
    
    def reflog(self, max_count: Optional[int] = None) -> List[Dict]:
        """
        Get reflog entries.
        
        Args:
            max_count: Maximum number of reflog entries to return
            
        Returns:
            List of reflog entries with 'sha', 'message', and 'selector' keys
        """
        cmd = ["git", "reflog", "--format=%H%x00%gs%x00%gd"]
        if max_count:
            cmd.extend(["-n", str(max_count)])
        
        output = self._run_command(cmd)
        entries = []
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('\x00')
            if len(parts) >= 3:
                entries.append({
                    'sha': parts[0],
                    'message': parts[1],
                    'selector': parts[2]  # e.g., HEAD@{0}
                })
        
        return entries
    
    def run_command(self, args: List[str]) -> CommandResult:
        """
        Run a git command and return the result.
        
        Args:
            args: Command arguments (without 'git' prefix)
            
        Returns:
            CommandResult with success status, output, and error
        """
        cmd = ["git"] + args
        result = subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        return CommandResult(
            success=result.returncode == 0,
            output=result.stdout,
            error=result.stderr
        )
    
    def compare_branches(self, base_branch: str, compare_branch: str) -> Tuple[List[str], List[str]]:
        """
        Compare two branches and get commits that differ.
        
        Args:
            base_branch: The base branch name
            compare_branch: The branch to compare
            
        Returns:
            Tuple of (ahead_commits, behind_commits) where:
            - ahead_commits: List of commit SHAs that compare_branch has but base_branch doesn't
            - behind_commits: List of commit SHAs that base_branch has but compare_branch doesn't
        """
        # Get commits ahead (in compare_branch but not in base_branch)
        try:
            output_ahead = self._run_command(["git", "rev-list", f"{base_branch}..{compare_branch}"])
            ahead_commits = [line.strip() for line in output_ahead.strip().split("\n") if line.strip()] if output_ahead.strip() else []
        except Exception:
            ahead_commits = []
        
        # Get commits behind (in base_branch but not in compare_branch)
        try:
            output_behind = self._run_command(["git", "rev-list", f"{compare_branch}..{base_branch}"])
            behind_commits = [line.strip() for line in output_behind.strip().split("\n") if line.strip()] if output_behind.strip() else []
        except Exception:
            behind_commits = []
        
        return ahead_commits, behind_commits
    
    def get_different_files(self, base_branch: str, compare_branch: str) -> List[str]:
        """
        Get list of files that differ between two branches.
        
        Args:
            base_branch: The base branch name
            compare_branch: The branch to compare
            
        Returns:
            List of file paths that differ between the branches
        """
        try:
            output = self._run_command(["git", "diff", "--name-only", base_branch, compare_branch])
            return [line.strip() for line in output.strip().split("\n") if line.strip()]
        except Exception:
            return []
    
    def _run_command(self, cmd: List[str]) -> str:
        """Run a Git command using subprocess."""
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
        return result.stdout
