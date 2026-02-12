#!/usr/bin/env python3
"""
Example demonstrating reset operations in CleverGit.

This example shows:
1. How to perform soft, mixed, and hard resets
2. How to view reflog for undo operations
3. How to use the ResetDialog UI
"""

from pathlib import Path
import tempfile
from clevergit.core.repo import Repo
from clevergit.core.commit import soft_reset, mixed_reset, hard_reset, get_reflog


def demonstrate_reset_operations():
    """Demonstrate reset operations."""
    
    # Create a temporary repository for demonstration
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        print(f"Creating test repository at: {repo_path}")
        repo = Repo.init(str(repo_path))
        
        # Create some commits
        print("\n=== Creating commits ===")
        file1 = repo_path / "file1.txt"
        file1.write_text("Initial content")
        commit1 = repo.commit_all("feat: add file1")
        print(f"Commit 1: {commit1.sha[:8]} - {commit1.message}")
        
        file2 = repo_path / "file2.txt"
        file2.write_text("Second file")
        commit2 = repo.commit_all("feat: add file2")
        print(f"Commit 2: {commit2.sha[:8]} - {commit2.message}")
        
        file3 = repo_path / "file3.txt"
        file3.write_text("Third file")
        commit3 = repo.commit_all("feat: add file3")
        print(f"Commit 3: {commit3.sha[:8]} - {commit3.message}")
        
        # Demonstrate soft reset
        print("\n=== Soft Reset ===")
        print(f"Resetting to commit 2 (soft mode)...")
        soft_reset(repo.client, commit2.sha)
        print("Soft reset complete: HEAD moved, changes staged")
        status = repo.status()
        print(f"Staged files: {[f.path for f in status.staged]}")
        
        # Recommit
        repo.commit_all("feat: re-add file3")
        
        # Demonstrate mixed reset
        print("\n=== Mixed Reset ===")
        print(f"Resetting to commit 2 (mixed mode)...")
        mixed_reset(repo.client, commit2.sha)
        print("Mixed reset complete: HEAD moved, staging reset")
        status = repo.status()
        print(f"Untracked files: {[f.path for f in status.untracked]}")
        
        # Recommit
        repo.commit_all("feat: re-add file3 again")
        
        # Demonstrate hard reset
        print("\n=== Hard Reset ===")
        print(f"Resetting to commit 1 (hard mode)...")
        hard_reset(repo.client, commit1.sha)
        print("Hard reset complete: HEAD moved, all changes discarded")
        print(f"Working directory clean: {repo.is_clean()}")
        print(f"Files in repo: {list(f.name for f in repo_path.iterdir() if f.is_file())}")
        
        # Demonstrate reflog
        print("\n=== Reflog (Command History) ===")
        reflog_entries = get_reflog(repo.client, max_count=10)
        print("Recent HEAD movements:")
        for i, entry in enumerate(reflog_entries[:5]):
            print(f"  {entry['selector']}: {entry['sha'][:8]} - {entry['message']}")
        
        # Demonstrate recovery using reflog
        print("\n=== Recovery Using Reflog ===")
        if len(reflog_entries) > 0:
            # Get the SHA from before the hard reset
            previous_sha = reflog_entries[0]['sha']
            print(f"Recovering to: {previous_sha[:8]}")
            soft_reset(repo.client, previous_sha)
            print("Recovery successful!")
            status = repo.status()
            print(f"Staged files after recovery: {[f.path for f in status.staged]}")


def demonstrate_ui_dialog():
    """Demonstrate the ResetDialog UI (requires GUI environment)."""
    print("\n=== Reset Dialog UI ===")
    print("To use the Reset Dialog in your application:")
    print("""
from clevergit.ui.widgets.reset_dialog import ResetDialog
from clevergit.core.repo import Repo

# Open repository
repo = Repo.open("path/to/repo")

# Show reset dialog
dialog = ResetDialog(parent_widget, repo)
if dialog.exec():
    selected_commit = dialog.selected_commit
    reset_mode = dialog.reset_mode
    print(f"Reset to {selected_commit} using {reset_mode} mode")
    """)


if __name__ == "__main__":
    print("=" * 60)
    print("CleverGit Reset Operations Example")
    print("=" * 60)
    
    demonstrate_reset_operations()
    demonstrate_ui_dialog()
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)
