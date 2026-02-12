#!/usr/bin/env python3
"""
Example script demonstrating tag management functionality in CleverGit.

This script shows how to:
- Create lightweight tags
- Create annotated tags
- List tags
- Delete tags
- Push tags to remote (if remote is configured)
"""

from clevergit.core.repo import Repo
from pathlib import Path
import tempfile
import shutil


def main():
    # Create a temporary directory for our demo repo
    temp_dir = tempfile.mkdtemp(prefix="clevergit_tag_demo_")
    print(f"Creating demo repository in: {temp_dir}")
    
    try:
        # Initialize a new repository
        repo = Repo.init(temp_dir)
        print("✓ Repository initialized")
        
        # Create some commits
        test_file = Path(temp_dir) / "README.md"
        test_file.write_text("# Tag Management Demo\n\nThis is version 1.0")
        repo.commit_all("Initial commit", allow_empty=True)
        print("✓ Created initial commit")
        
        # Create a lightweight tag
        tag1 = repo.create_tag("v1.0.0")
        print(f"✓ Created lightweight tag: {tag1.name}")
        
        # Create another commit
        test_file.write_text("# Tag Management Demo\n\nThis is version 1.1")
        repo.commit_all("Update to version 1.1", allow_empty=True)
        print("✓ Created second commit")
        
        # Create an annotated tag
        tag2 = repo.create_annotated_tag("v1.1.0", "Release version 1.1.0\n\nNew features:\n- Tag management\n- UI improvements")
        print(f"✓ Created annotated tag: {tag2.name}")
        
        # List all tags
        print("\n📋 All tags in repository:")
        tags = repo.list_tags()
        for tag in tags:
            tag_type = "annotated" if tag.is_annotated else "lightweight"
            print(f"  • {tag.name} ({tag_type}) -> {tag.short_sha}")
            if tag.is_annotated and tag.message:
                print(f"    Message: {tag.message}")
        
        # Delete a tag
        print(f"\n🗑️  Deleting tag: v1.0.0")
        repo.delete_tag("v1.0.0")
        
        # List tags again
        print("\n📋 Tags after deletion:")
        tags = repo.list_tags()
        for tag in tags:
            print(f"  • {tag.name}")
        
        print("\n✅ Tag management demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
