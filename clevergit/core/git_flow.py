"""
Git Flow workflow management module.

Implements Git Flow workflow pattern for branch management:
- Feature branches: develop -> feature/* -> develop
- Release branches: develop -> release/* -> main + develop
- Hotfix branches: main -> hotfix/* -> main + develop
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from clevergit.git.client import GitClient
from clevergit.git.errors import BranchError, UncommittedChangesError


@dataclass
class GitFlowConfig:
    """Git Flow configuration."""

    master_branch: str = "main"
    develop_branch: str = "develop"
    feature_prefix: str = "feature/"
    release_prefix: str = "release/"
    hotfix_prefix: str = "hotfix/"
    version_tag_prefix: str = "v"


class GitFlow:
    """Git Flow workflow manager."""

    def __init__(self, client: GitClient, config: Optional[GitFlowConfig] = None):
        """
        Initialize Git Flow manager.

        Args:
            client: Git client instance
            config: Git Flow configuration (uses defaults if None)
        """
        self.client = client
        self.config = config or GitFlowConfig()

    def is_initialized(self) -> bool:
        """
        Check if Git Flow is initialized for this repository.

        Returns:
            True if both master and develop branches exist
        """
        try:
            branches = self.client.list_branches()
            return self.config.master_branch in branches and self.config.develop_branch in branches
        except Exception:
            return False

    def initialize(self, force: bool = False) -> None:
        """
        Initialize Git Flow in the repository.

        Creates the develop branch if it doesn't exist.

        Args:
            force: Force initialization even if already initialized

        Raises:
            BranchError: If initialization fails
        """
        if self.is_initialized() and not force:
            raise BranchError("Git Flow is already initialized")

        branches = self.client.list_branches()

        # Check if master branch exists
        if self.config.master_branch not in branches:
            raise BranchError(
                f"Master branch '{self.config.master_branch}' does not exist. "
                "Please ensure you have an initial commit."
            )

        # Create develop branch if it doesn't exist
        if self.config.develop_branch not in branches:
            current_branch = self.client.current_branch()
            # Create develop from master
            self.client.create_branch(
                self.config.develop_branch, start_point=self.config.master_branch
            )
            # Switch back to original branch if needed
            if current_branch and current_branch != self.config.develop_branch:
                self.client.checkout(current_branch)

    def start_feature(self, name: str) -> str:
        """
        Start a new feature branch.

        Creates a feature branch from develop.

        Args:
            name: Feature name (without prefix)

        Returns:
            Full branch name (with prefix)

        Raises:
            BranchError: If branch already exists or Git Flow not initialized
            UncommittedChangesError: If there are uncommitted changes
        """
        if not self.is_initialized():
            raise BranchError("Git Flow is not initialized. Run initialize() first.")

        if not self.client.is_clean():
            raise UncommittedChangesError(
                "Cannot start feature with uncommitted changes. "
                "Commit or stash your changes first."
            )

        branch_name = f"{self.config.feature_prefix}{name}"

        # Check if branch already exists
        if branch_name in self.client.list_branches():
            raise BranchError(f"Feature branch already exists: {branch_name}")

        # Create and checkout feature branch from develop
        self.client.create_branch(branch_name, start_point=self.config.develop_branch)
        self.client.checkout(branch_name)

        return branch_name

    def finish_feature(self, name: str, delete: bool = True) -> None:
        """
        Finish a feature branch.

        Merges feature branch into develop and optionally deletes it.

        Args:
            name: Feature name (without prefix) or full branch name
            delete: Delete feature branch after merging

        Raises:
            BranchError: If branch doesn't exist or merge fails
            UncommittedChangesError: If there are uncommitted changes
        """
        if not self.is_initialized():
            raise BranchError("Git Flow is not initialized. Run initialize() first.")

        if not self.client.is_clean():
            raise UncommittedChangesError(
                "Cannot finish feature with uncommitted changes. "
                "Commit or stash your changes first."
            )

        # Handle both full branch name and just the feature name
        if name.startswith(self.config.feature_prefix):
            branch_name = name
        else:
            branch_name = f"{self.config.feature_prefix}{name}"

        # Check if branch exists
        if branch_name not in self.client.list_branches():
            raise BranchError(f"Feature branch does not exist: {branch_name}")

        # Switch to develop
        self.client.checkout(self.config.develop_branch)

        # Merge feature into develop
        self.client.merge(branch_name, no_ff=True)

        # Delete feature branch if requested
        if delete:
            self.client.delete_branch(branch_name)

    def start_release(self, version: str) -> str:
        """
        Start a new release branch.

        Creates a release branch from develop.

        Args:
            version: Release version (without prefix)

        Returns:
            Full branch name (with prefix)

        Raises:
            BranchError: If branch already exists or Git Flow not initialized
            UncommittedChangesError: If there are uncommitted changes
        """
        if not self.is_initialized():
            raise BranchError("Git Flow is not initialized. Run initialize() first.")

        if not self.client.is_clean():
            raise UncommittedChangesError(
                "Cannot start release with uncommitted changes. "
                "Commit or stash your changes first."
            )

        branch_name = f"{self.config.release_prefix}{version}"

        # Check if branch already exists
        if branch_name in self.client.list_branches():
            raise BranchError(f"Release branch already exists: {branch_name}")

        # Create and checkout release branch from develop
        self.client.create_branch(branch_name, start_point=self.config.develop_branch)
        self.client.checkout(branch_name)

        return branch_name

    def finish_release(
        self, version: str, tag_message: Optional[str] = None, delete: bool = True
    ) -> None:
        """
        Finish a release branch.

        Merges release into master, tags the release, merges back into develop,
        and optionally deletes the release branch.

        Args:
            version: Release version (without prefix) or full branch name
            tag_message: Optional message for the version tag
            delete: Delete release branch after merging

        Raises:
            BranchError: If branch doesn't exist or merge fails
            UncommittedChangesError: If there are uncommitted changes
        """
        if not self.is_initialized():
            raise BranchError("Git Flow is not initialized. Run initialize() first.")

        if not self.client.is_clean():
            raise UncommittedChangesError(
                "Cannot finish release with uncommitted changes. "
                "Commit or stash your changes first."
            )

        # Handle both full branch name and just the version
        if version.startswith(self.config.release_prefix):
            branch_name = version
            version_name = version[len(self.config.release_prefix) :]
        else:
            branch_name = f"{self.config.release_prefix}{version}"
            version_name = version

        # Check if branch exists
        if branch_name not in self.client.list_branches():
            raise BranchError(f"Release branch does not exist: {branch_name}")

        # Merge into master
        self.client.checkout(self.config.master_branch)
        self.client.merge(branch_name, no_ff=True)

        # Create tag
        tag_name = f"{self.config.version_tag_prefix}{version_name}"
        if tag_message:
            self.client.create_annotated_tag(tag_name, message=tag_message)
        else:
            self.client.create_tag(tag_name)

        # Merge back into develop
        self.client.checkout(self.config.develop_branch)
        self.client.merge(branch_name, no_ff=True)

        # Delete release branch if requested
        if delete:
            self.client.delete_branch(branch_name)

    def start_hotfix(self, version: str) -> str:
        """
        Start a new hotfix branch.

        Creates a hotfix branch from master.

        Args:
            version: Hotfix version (without prefix)

        Returns:
            Full branch name (with prefix)

        Raises:
            BranchError: If branch already exists or Git Flow not initialized
            UncommittedChangesError: If there are uncommitted changes
        """
        if not self.is_initialized():
            raise BranchError("Git Flow is not initialized. Run initialize() first.")

        if not self.client.is_clean():
            raise UncommittedChangesError(
                "Cannot start hotfix with uncommitted changes. "
                "Commit or stash your changes first."
            )

        branch_name = f"{self.config.hotfix_prefix}{version}"

        # Check if branch already exists
        if branch_name in self.client.list_branches():
            raise BranchError(f"Hotfix branch already exists: {branch_name}")

        # Create and checkout hotfix branch from master
        self.client.create_branch(branch_name, start_point=self.config.master_branch)
        self.client.checkout(branch_name)

        return branch_name

    def finish_hotfix(
        self, version: str, tag_message: Optional[str] = None, delete: bool = True
    ) -> None:
        """
        Finish a hotfix branch.

        Merges hotfix into master, tags the hotfix, merges back into develop,
        and optionally deletes the hotfix branch.

        Args:
            version: Hotfix version (without prefix) or full branch name
            tag_message: Optional message for the version tag
            delete: Delete hotfix branch after merging

        Raises:
            BranchError: If branch doesn't exist or merge fails
            UncommittedChangesError: If there are uncommitted changes
        """
        if not self.is_initialized():
            raise BranchError("Git Flow is not initialized. Run initialize() first.")

        if not self.client.is_clean():
            raise UncommittedChangesError(
                "Cannot finish hotfix with uncommitted changes. "
                "Commit or stash your changes first."
            )

        # Handle both full branch name and just the version
        if version.startswith(self.config.hotfix_prefix):
            branch_name = version
            version_name = version[len(self.config.hotfix_prefix) :]
        else:
            branch_name = f"{self.config.hotfix_prefix}{version}"
            version_name = version

        # Check if branch exists
        if branch_name not in self.client.list_branches():
            raise BranchError(f"Hotfix branch does not exist: {branch_name}")

        # Merge into master
        self.client.checkout(self.config.master_branch)
        self.client.merge(branch_name, no_ff=True)

        # Create tag
        tag_name = f"{self.config.version_tag_prefix}{version_name}"
        if tag_message:
            self.client.create_annotated_tag(tag_name, message=tag_message)
        else:
            self.client.create_tag(tag_name)

        # Merge back into develop
        self.client.checkout(self.config.develop_branch)
        self.client.merge(branch_name, no_ff=True)

        # Delete hotfix branch if requested
        if delete:
            self.client.delete_branch(branch_name)

    def get_active_branches(self) -> Dict[str, List[str]]:
        """
        Get all active Git Flow branches.

        Returns:
            Dictionary with lists of feature, release, and hotfix branches
        """
        branches = self.client.list_branches()

        features = [b for b in branches if b.startswith(self.config.feature_prefix)]
        releases = [b for b in branches if b.startswith(self.config.release_prefix)]
        hotfixes = [b for b in branches if b.startswith(self.config.hotfix_prefix)]

        return {
            "features": features,
            "releases": releases,
            "hotfixes": hotfixes,
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get Git Flow status.

        Returns:
            Dictionary with initialization status and active branches
        """
        is_init = self.is_initialized()

        status = {
            "initialized": is_init,
            "config": {
                "master_branch": self.config.master_branch,
                "develop_branch": self.config.develop_branch,
                "feature_prefix": self.config.feature_prefix,
                "release_prefix": self.config.release_prefix,
                "hotfix_prefix": self.config.hotfix_prefix,
            },
        }

        if is_init:
            status["active_branches"] = self.get_active_branches()
            status["current_branch"] = self.client.current_branch()

        return status
