# Stash Management Guide

## Overview

CleverGit provides comprehensive stash management functionality to save and restore working directory changes. Stashing is useful when you need to switch branches or pull changes but have uncommitted work you want to preserve.

## Features

- **Save Stash**: Save current changes (modified, staged, and optionally untracked files) to stash
- **List Stashes**: View all saved stashes with their messages and metadata
- **Preview Stash**: View the diff of a stash before applying it
- **Apply Stash**: Restore stashed changes without removing the stash
- **Pop Stash**: Restore stashed changes and remove the stash
- **Drop Stash**: Delete a specific stash
- **Clear All**: Remove all stashes at once

## Using Stash in GUI

### Accessing Stash View

1. Open a repository in CleverGit
2. Click the **📦 Stash** button in the toolbar
3. The stash panel will appear in the left sidebar

### Saving a Stash

1. Make changes to your working directory
2. Click **💾 Save Stash** button
3. Enter an optional message to describe the stash
4. The stash will be created and your working directory will be clean

**Note**: Untracked files are automatically included in the stash.

### Viewing Stashes

The stash list displays all saved stashes with their messages. Click on a stash to preview its content in the diff viewer below.

### Applying a Stash

**Option 1: Apply (Keep Stash)**
1. Select a stash from the list
2. Click **📥 Apply** button
3. The stash changes will be restored to your working directory
4. The stash remains in the list for future use

**Option 2: Pop (Apply and Remove)**
1. Select a stash from the list
2. Click **↩️ Pop** button (or double-click the stash)
3. The stash changes will be restored and the stash will be removed

### Deleting Stashes

**Delete One Stash:**
1. Select a stash from the list
2. Click **🗑️ Drop** button
3. Confirm the deletion

**Delete All Stashes:**
1. Click **🧹 Clear All** button
2. Confirm to delete all stashes

**Warning**: Deleted stashes cannot be recovered!

## Using Stash Programmatically

### Basic Usage

```python
from clevergit.core.repo import Repo

# Open repository
repo = Repo.open("/path/to/repo")

# Save changes to stash
repo.stash_save("WIP: feature implementation")

# List all stashes
stashes = repo.stash_list()
for stash in stashes:
    print(f"{stash.ref}: {stash.message}")

# Show stash content
diff = repo.stash_show(0)
print(diff)

# Apply stash (keep it)
repo.stash_apply(0)

# Pop stash (apply and remove)
repo.stash_pop(0)

# Drop a specific stash
repo.stash_drop(0)

# Clear all stashes
repo.stash_clear()
```

### Include Untracked Files

```python
# Save with untracked files
repo.stash_save("Save everything", include_untracked=True)
```

### Working with Multiple Stashes

```python
# Create multiple stashes
repo.stash_save("First change")
repo.stash_save("Second change")
repo.stash_save("Third change")

# List shows most recent first
stashes = repo.stash_list()
# stashes[0] is "Third change"
# stashes[1] is "Second change"
# stashes[2] is "First change"

# Apply specific stash
repo.stash_apply(1)  # Apply "Second change"
```

### StashInfo Object

Each stash is represented by a `StashInfo` object with the following properties:

```python
stash = stashes[0]

# Properties
stash.index        # Stash index (0 for most recent)
stash.message      # Stash message
stash.branch       # Branch where stash was created
stash.commit_sha   # SHA of the stash commit
stash.ref          # Git reference (e.g., "stash@{0}")

# Methods
stash.format_oneline()  # Get one-line formatted string
str(stash)              # String representation
```

## Example Workflow

### Scenario: Switch Branches with Uncommitted Changes

```python
from clevergit.core.repo import Repo

repo = Repo.open(".")

# You're working on feature branch with uncommitted changes
print(f"Current branch: {repo.current_branch()}")  # "feature"
print(f"Clean: {repo.is_clean()}")  # False

# Save changes to stash
repo.stash_save("WIP: feature work")

# Now working directory is clean
print(f"Clean: {repo.is_clean()}")  # True

# Switch to main branch
repo.checkout("main")

# Do some work on main...

# Switch back to feature
repo.checkout("feature")

# Restore your work
repo.stash_pop(0)

# Continue working
print(f"Clean: {repo.is_clean()}")  # False (changes restored)
```

### Scenario: Test Changes Without Committing

```python
# Make some experimental changes
# ...

# Save them to stash
repo.stash_save("Experimental changes")

# Test without the changes (clean state)
# Run tests, etc.

# Restore the changes
repo.stash_apply(0)  # Keep stash in case you want to test again

# If changes are good, commit them
# If not, drop the stash
repo.stash_drop(0)
```

## Tips and Best Practices

1. **Use Descriptive Messages**: Always provide meaningful stash messages to identify them later
2. **Preview Before Applying**: Use the preview feature or `stash_show()` to check what will be applied
3. **Regular Cleanup**: Periodically review and clean up old stashes you no longer need
4. **Stash Before Switching Branches**: Stash uncommitted changes before switching branches to avoid conflicts
5. **Use Apply for Experimentation**: Use `apply` instead of `pop` when you're not sure if the stash changes are final
6. **Stash Untracked Files**: Remember to include untracked files if they're part of your work in progress

## Common Issues

### Conflict When Applying Stash

If applying a stash causes conflicts:
1. Resolve the conflicts manually
2. Stage the resolved files with `git add`
3. Continue working (don't commit yet if you want to make more changes)

### Stash Not Showing Expected Files

- Check if files are untracked (use `include_untracked=True`)
- Verify files are not in `.gitignore`

### Can't Switch Branches

If you see "Cannot switch branches with uncommitted changes":
1. Either commit your changes
2. Or stash them using `repo.stash_save()`

## Command-Line Example

You can also use the provided example script:

```bash
python example_stash_usage.py
```

This interactive script demonstrates all stash operations with a simple menu interface.

## Integration with Git

CleverGit's stash functionality uses Git's native stash commands, so:
- Stashes created in CleverGit are visible in other Git clients
- Stashes created with `git stash` are visible in CleverGit
- All standard Git stash features are supported

## See Also

- [Git Stash Documentation](https://git-scm.com/docs/git-stash)
- [CleverGit Branch Management](BRANCH_MANAGEMENT.md)
- [CleverGit Status View](STATUS_VIEW.md)
