#!/usr/bin/env python3
"""
Example demonstrating stash functionality in CleverGit.

This script shows how to:
1. Save changes to stash
2. List stashes
3. Apply stashes
4. Pop stashes
5. Drop stashes
6. Clear all stashes
"""

from pathlib import Path
from clevergit.core.repo import Repo


def main():
    """Demonstrate stash operations."""
    print("=== CleverGit Stash Management Demo ===\n")
    
    # Open repository (or use current directory)
    repo_path = input("Enter repository path (or press Enter for current directory): ").strip()
    if not repo_path:
        repo_path = "."
    
    try:
        repo = Repo.open(repo_path)
        print(f"✓ Opened repository: {repo.path}\n")
    except Exception as e:
        print(f"✗ Failed to open repository: {e}")
        return
    
    while True:
        print("\n--- Stash Operations Menu ---")
        print("1. List stashes")
        print("2. Save stash")
        print("3. Show stash (preview)")
        print("4. Apply stash")
        print("5. Pop stash")
        print("6. Drop stash")
        print("7. Clear all stashes")
        print("8. Check repository status")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        try:
            if choice == "1":
                list_stashes(repo)
            elif choice == "2":
                save_stash(repo)
            elif choice == "3":
                show_stash(repo)
            elif choice == "4":
                apply_stash(repo)
            elif choice == "5":
                pop_stash(repo)
            elif choice == "6":
                drop_stash(repo)
            elif choice == "7":
                clear_stashes(repo)
            elif choice == "8":
                check_status(repo)
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            print(f"✗ Error: {e}")


def list_stashes(repo: Repo):
    """List all stashes."""
    stashes = repo.stash_list()
    
    if not stashes:
        print("No stashes found.")
        return
    
    print(f"\nFound {len(stashes)} stash(es):")
    for stash in stashes:
        print(f"  {stash.ref}: {stash.message}")
        print(f"    Branch: {stash.branch}")
        print(f"    Commit: {stash.commit_sha[:8]}")


def save_stash(repo: Repo):
    """Save changes to stash."""
    if repo.is_clean():
        print("✓ Working directory is clean. Nothing to stash.")
        return
    
    message = input("Enter stash message (optional): ").strip()
    include_untracked = input("Include untracked files? (y/n): ").strip().lower() == "y"
    
    repo.stash_save(
        message=message if message else None,
        include_untracked=include_untracked
    )
    print("✓ Stash saved successfully!")


def show_stash(repo: Repo):
    """Show stash content."""
    stashes = repo.stash_list()
    
    if not stashes:
        print("No stashes found.")
        return
    
    list_stashes(repo)
    index = int(input("\nEnter stash index to preview: ").strip())
    
    if index < 0 or index >= len(stashes):
        print("Invalid stash index.")
        return
    
    print(f"\n--- Stash Preview: stash@{{{index}}} ---")
    diff = repo.stash_show(index)
    print(diff)


def apply_stash(repo: Repo):
    """Apply a stash without removing it."""
    stashes = repo.stash_list()
    
    if not stashes:
        print("No stashes found.")
        return
    
    list_stashes(repo)
    index = int(input("\nEnter stash index to apply: ").strip())
    
    if index < 0 or index >= len(stashes):
        print("Invalid stash index.")
        return
    
    repo.stash_apply(index)
    print(f"✓ Applied stash@{{{index}}} successfully!")


def pop_stash(repo: Repo):
    """Pop a stash (apply and remove)."""
    stashes = repo.stash_list()
    
    if not stashes:
        print("No stashes found.")
        return
    
    list_stashes(repo)
    index = int(input("\nEnter stash index to pop: ").strip())
    
    if index < 0 or index >= len(stashes):
        print("Invalid stash index.")
        return
    
    repo.stash_pop(index)
    print(f"✓ Popped stash@{{{index}}} successfully!")


def drop_stash(repo: Repo):
    """Drop a stash."""
    stashes = repo.stash_list()
    
    if not stashes:
        print("No stashes found.")
        return
    
    list_stashes(repo)
    index = int(input("\nEnter stash index to drop: ").strip())
    
    if index < 0 or index >= len(stashes):
        print("Invalid stash index.")
        return
    
    confirm = input(f"Are you sure you want to drop stash@{{{index}}}? (y/n): ").strip().lower()
    if confirm == "y":
        repo.stash_drop(index)
        print(f"✓ Dropped stash@{{{index}}} successfully!")
    else:
        print("Cancelled.")


def clear_stashes(repo: Repo):
    """Clear all stashes."""
    stashes = repo.stash_list()
    
    if not stashes:
        print("No stashes found.")
        return
    
    print(f"Found {len(stashes)} stash(es).")
    confirm = input("Are you sure you want to clear ALL stashes? (y/n): ").strip().lower()
    
    if confirm == "y":
        repo.stash_clear()
        print("✓ All stashes cleared successfully!")
    else:
        print("Cancelled.")


def check_status(repo: Repo):
    """Check repository status."""
    is_clean = repo.is_clean()
    current_branch = repo.current_branch()
    
    print(f"\nCurrent branch: {current_branch or 'unknown'}")
    print(f"Working directory: {'clean' if is_clean else 'has changes'}")
    
    if not is_clean:
        status = repo.status()
        if status.modified:
            print(f"  Modified files: {len(status.modified)}")
        if status.untracked:
            print(f"  Untracked files: {len(status.untracked)}")
        if status.staged:
            print(f"  Staged files: {len(status.staged)}")


if __name__ == "__main__":
    main()
