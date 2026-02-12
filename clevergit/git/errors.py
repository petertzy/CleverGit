"""
Custom exception classes for Git operations.

This module defines user-friendly exceptions that wrap Git errors
with meaningful messages.
"""


class CleverGitError(Exception):
    """Base exception for all CleverGit errors."""
    pass


class RepoNotFoundError(CleverGitError):
    """Raised when a Git repository is not found."""
    pass


class InvalidRepoError(CleverGitError):
    """Raised when a repository is corrupted or invalid."""
    pass


class CommitError(CleverGitError):
    """Raised when a commit operation fails."""
    pass


class NothingToCommitError(CommitError):
    """Raised when attempting to commit with no changes."""
    pass


class BranchError(CleverGitError):
    """Raised when a branch operation fails."""
    pass


class UncommittedChangesError(CleverGitError):
    """Raised when operation requires clean working directory."""
    pass


class MergeError(CleverGitError):
    """Raised when a merge operation fails."""
    pass


class RebaseError(CleverGitError):
    """Raised when a rebase operation fails."""
    pass


class ConflictError(CleverGitError):
    """Raised when there are merge/rebase conflicts."""
    pass


class RemoteError(CleverGitError):
    """Raised when a remote operation fails."""
    pass


class PushError(RemoteError):
    """Raised when a push operation fails."""
    pass


class FetchError(RemoteError):
    """Raised when a fetch operation fails."""
    pass


class PullError(RemoteError):
    """Raised when a pull operation fails."""
    pass


class TagError(CleverGitError):
    """Raised when a tag operation fails."""
    pass


class CherryPickError(CleverGitError):
    """Raised when a cherry-pick operation fails."""
    pass


class RevertError(CleverGitError):
    """Raised when a revert operation fails."""
    pass


class ResetError(CleverGitError):
    """Raised when a reset operation fails."""
    pass
