#!/usr/bin/env python3
"""
Example script to test the blame feature.
"""

from pathlib import Path
import sys
import tempfile

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from clevergit.core.repo import Repo
from clevergit.core.blame import get_blame


def main():
    """Test the blame functionality."""
    # Create a temporary repository
    with tempfile.TemporaryDirectory() as tmp_dir:
        repo_path = Path(tmp_dir)
        
        print(f"Creating test repository in {repo_path}")
        repo = Repo.init(str(repo_path))
        
        # Create a test file with multiple commits
        test_file = repo_path / "test.py"
        
        # First commit
        test_file.write_text("# Test file\n")
        repo.commit_all("feat: initial commit")
        print("✓ Created initial commit")
        
        # Second commit - add more lines
        test_file.write_text("# Test file\nprint('Hello')\n")
        repo.commit_all("feat: add print statement")
        print("✓ Added second commit")
        
        # Third commit - add final line
        test_file.write_text("# Test file\nprint('Hello')\nprint('World')\n")
        repo.commit_all("feat: add world print")
        print("✓ Added third commit")
        
        # Now get blame information
        print("\nGetting blame information for test.py...")
        blame_list = get_blame(repo_path, "test.py")
        
        print(f"\n{'='*80}")
        print(f"Blame information for test.py ({len(blame_list)} lines)")
        print(f"{'='*80}")
        
        for blame in blame_list:
            print(f"Line {blame.line_number:3d} | {blame.short_sha} | {blame.author:20s} | {blame.date.strftime('%Y-%m-%d')} | {blame.content}")
        
        print(f"\n{'='*80}")
        print("✓ Blame feature test completed successfully!")
        print(f"{'='*80}")


if __name__ == "__main__":
    main()
