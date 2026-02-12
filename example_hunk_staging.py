#!/usr/bin/env python3
"""
Example script demonstrating hunk-based staging functionality.

This script creates a test repository, makes changes to a file,
and demonstrates how to stage/unstage specific hunks.
"""

from pathlib import Path
import tempfile
import shutil

from clevergit.core.repo import Repo
from clevergit.core.diff import (
    get_working_tree_diff,
    get_staged_diff,
    parse_diff_hunks,
    create_patch_from_file_hunk,
)
from clevergit.git.client import GitClient


def main():
    """Run the example."""
    # Create a temporary directory for the test repo
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = Path(tmp_dir) / "test_repo"
        
        print("=" * 60)
        print("Hunk-Based Staging Example")
        print("=" * 60)
        
        # Initialize repository
        print("\n1. Initializing repository...")
        repo = Repo.init(str(repo_path))
        client = GitClient(repo_path)
        print(f"   Created repo at: {repo_path}")
        
        # Create initial file
        print("\n2. Creating initial file with content...")
        test_file = repo_path / "example.txt"
        initial_content = "\n".join([f"Line {i}" for i in range(1, 31)])
        test_file.write_text(initial_content)
        client.add(["example.txt"])
        client.commit("Initial commit")
        print("   Committed initial file with 30 lines")
        
        # Make multiple changes far apart
        print("\n3. Making changes at different locations...")
        lines = initial_content.split("\n")
        lines[0] = "Line 1 - MODIFIED"  # Line 1
        lines[14] = "Line 15 - MODIFIED"  # Line 15
        lines[29] = "Line 30 - MODIFIED"  # Line 30
        modified_content = "\n".join(lines)
        test_file.write_text(modified_content)
        print("   Modified lines 1, 15, and 30 (far apart)")
        
        # Get working tree diff
        print("\n4. Getting working tree diff...")
        diff_result = get_working_tree_diff(repo_path)
        print(f"   Files changed: {diff_result.stats.files_changed}")
        print(f"   Insertions: {diff_result.stats.insertions}")
        print(f"   Deletions: {diff_result.stats.deletions}")
        
        # Parse hunks
        print("\n5. Parsing diff hunks...")
        if diff_result.files:
            file_diff = diff_result.files[0]
            hunks = parse_diff_hunks(file_diff.diff_text)
            print(f"   Found {len(hunks)} hunk(s)")
            
            for i, hunk in enumerate(hunks):
                print(f"\n   Hunk {i+1}:")
                print(f"      Header: {hunk.header}")
                print(f"      Old lines: {hunk.old_start},{hunk.old_count}")
                print(f"      New lines: {hunk.new_start},{hunk.new_count}")
                print(f"      Content lines: {len(hunk.lines)}")
            
            # Stage the first hunk
            if hunks:
                print("\n6. Staging first hunk...")
                first_hunk = hunks[0]
                patch = create_patch_from_file_hunk(file_diff, first_hunk)
                
                print("   Generated patch:")
                for i, line in enumerate(patch.split("\n"), 1):
                    print(f"   {i:2d}: {line}")
                
                try:
                    client.stage_hunk(patch)
                    print("   ✓ First hunk staged successfully!")
                    
                    # Check staged diff
                    staged_diff = get_staged_diff(repo_path)
                    print(f"\n7. Staged changes:")
                    print(f"   Files changed: {staged_diff.stats.files_changed}")
                    print(f"   Insertions: {staged_diff.stats.insertions}")
                    print(f"   Deletions: {staged_diff.stats.deletions}")
                    
                    # Check remaining working tree diff
                    remaining_diff = get_working_tree_diff(repo_path)
                    print(f"\n8. Remaining unstaged changes:")
                    print(f"   Insertions: {remaining_diff.stats.insertions}")
                    print(f"   Deletions: {remaining_diff.stats.deletions}")
                    
                except Exception as e:
                    print(f"   ✗ Failed to stage hunk: {e}")
                    print("   (This may fail due to git index format requirements)")
        
        print("\n" + "=" * 60)
        print("Example completed!")
        print("=" * 60)
        print("\nNote: This example demonstrates the hunk parsing and")
        print("patch creation functionality. In a real GUI application,")
        print("users would select hunks in the diff viewer and stage/")
        print("unstage them with a right-click menu or buttons.")


if __name__ == "__main__":
    main()
