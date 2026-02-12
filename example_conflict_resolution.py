#!/usr/bin/env python3
"""
Simple CLI example for conflict resolution.
This demonstrates the core conflict resolution functionality without requiring GUI.
"""

from pathlib import Path
import tempfile
from clevergit.core.conflict import (
    parse_conflicted_file,
    resolve_conflict_take_ours,
    resolve_conflict_take_theirs,
    resolve_conflict_take_both,
    resolve_all_conflicts
)


def create_sample_conflict():
    """Create a sample file with conflicts for testing."""
    content = """# Configuration File
database:
<<<<<<< HEAD
  host: localhost
  port: 5432
  name: production_db
=======
  host: db.example.com
  port: 5433
  name: staging_db
>>>>>>> feature-branch

server:
<<<<<<< HEAD
  port: 8080
  ssl: true
||||||| base-commit
  port: 3000
  ssl: false
=======
  port: 8000
  ssl: true
>>>>>>> feature-branch

# End of config
"""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.conf',
        delete=False,
        encoding='utf-8'
    )
    temp_file.write(content)
    temp_file.close()
    return Path(temp_file.name)


def demonstrate_resolution():
    """Demonstrate conflict resolution functionality."""
    print("=" * 60)
    print("CleverGit Conflict Resolution Demo")
    print("=" * 60)
    
    # Create sample conflict file
    conflict_file = create_sample_conflict()
    print(f"\n✓ Created sample conflict file: {conflict_file}")
    
    # Parse the file
    conflicted = parse_conflicted_file(conflict_file)
    print(f"\n✓ Parsed file: Found {conflicted.get_conflict_count()} conflicts")
    
    # Display conflicts
    resolutions = []
    for i, conflict in enumerate(conflicted.conflicts, 1):
        print(f"\n{'=' * 60}")
        print(f"Conflict #{i}")
        print(f"Label: {conflict.ours_label} vs {conflict.theirs_label}")
        print(f"Has base: {conflict.has_base()}")
        print(f"{'=' * 60}")
        
        print(f"\n[OURS] {conflict.ours_label}:")
        print("  " + "\n  ".join(conflict.ours_content))
        
        if conflict.has_base():
            print(f"\n[BASE] Common Ancestor:")
            print("  " + "\n  ".join(conflict.base_content))
        
        print(f"\n[THEIRS] {conflict.theirs_label}:")
        print("  " + "\n  ".join(conflict.theirs_content))
        
        # Demonstrate different resolution strategies
        if i == 1:
            # First conflict: take ours
            resolution = resolve_conflict_take_ours(conflict)
            print(f"\n→ Strategy: Take OURS")
            resolutions.append(resolution)
        else:
            # Second conflict: take theirs
            resolution = resolve_conflict_take_theirs(conflict)
            print(f"\n→ Strategy: Take THEIRS")
            resolutions.append(resolution)
        
        print(f"\n[RESOLUTION]:")
        print("  " + "\n  ".join(resolution))
    
    # Apply all resolutions
    print(f"\n{'=' * 60}")
    print("Applying all resolutions...")
    resolved_content = resolve_all_conflicts(conflicted, resolutions)
    
    # Write to file
    with open(conflict_file, 'w') as f:
        f.write(resolved_content)
    
    print(f"✓ All conflicts resolved!")
    print(f"\n{'=' * 60}")
    print("Resolved File Content:")
    print(f"{'=' * 60}")
    print(resolved_content)
    print(f"{'=' * 60}")
    
    # Cleanup
    conflict_file.unlink()
    print(f"\n✓ Cleaned up temporary file")
    
    # Demonstrate other resolution strategies
    print(f"\n{'=' * 60}")
    print("Other Resolution Strategies Available:")
    print(f"{'=' * 60}")
    print("1. resolve_conflict_take_ours(conflict)")
    print("   → Take the version from the current branch")
    print("\n2. resolve_conflict_take_theirs(conflict)")
    print("   → Take the version from the incoming branch")
    print("\n3. resolve_conflict_take_both(conflict, ours_first=True)")
    print("   → Combine both versions (ours first, then theirs)")
    print("\n4. resolve_conflict_take_both(conflict, ours_first=False)")
    print("   → Combine both versions (theirs first, then ours)")
    print("\n5. Manual editing (provide custom list of lines)")
    print("   → Create your own resolution by providing lines")
    
    print(f"\n{'=' * 60}")
    print("✅ Demo completed successfully!")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    try:
        demonstrate_resolution()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
