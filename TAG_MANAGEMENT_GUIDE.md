# Tag Management Guide

This guide explains how to use the tag management features in CleverGit.

## Overview

Git tags are used to mark specific points in your repository's history, typically to mark release points (v1.0.0, v2.0.0, etc.). CleverGit supports both lightweight and annotated tags.

## Tag Types

### Lightweight Tags
Lightweight tags are simple pointers to a specific commit. They're like bookmarks.

```python
from clevergit.core.repo import Repo

repo = Repo.open(".")
repo.create_tag("v1.0.0")
```

### Annotated Tags
Annotated tags are stored as full objects in the Git database. They contain:
- Tagger name and email
- Date
- Tag message
- Can be signed and verified with GPG

```python
repo.create_annotated_tag("v1.0.0", "Release version 1.0.0")
```

## Using Tags Programmatically

### Creating Tags

```python
from clevergit.core.repo import Repo

repo = Repo.open("/path/to/repo")

# Create a lightweight tag on HEAD
tag = repo.create_tag("v1.0.0")

# Create an annotated tag on HEAD
tag = repo.create_annotated_tag("v1.0.0", "First stable release")

# Create a tag on a specific commit
tag = repo.create_tag("v0.9.0", commit="abc1234")
```

### Listing Tags

```python
# List all tags
tags = repo.list_tags()

for tag in tags:
    print(f"{tag.name}: {tag.commit_sha}")
    if tag.is_annotated:
        print(f"  Message: {tag.message}")
        print(f"  Tagger: {tag.tagger}")
        print(f"  Date: {tag.date}")
```

### Deleting Tags

```python
# Delete a local tag
repo.delete_tag("v1.0.0")

# Note: This only deletes the local tag.
# To delete from remote, you need to push the deletion separately.
```

### Pushing Tags

```python
# Push a specific tag to remote
repo.push_tag("v1.0.0")

# Push all tags to remote
repo.push_all_tags()

# Push to a specific remote
repo.push_tag("v1.0.0", remote="upstream")
```

## Using the GUI

### Accessing Tag View

1. Open a repository in CleverGit GUI
2. Click the "🏷️ Tags" button in the toolbar
3. The tag panel will appear on the left side

### Creating Tags via GUI

1. Click "New Tag" button
2. Enter tag name
3. (Optional) Check "Create annotated tag" for annotated tags
4. (Optional) Enter tag message for annotated tags
5. Click OK

### Viewing Tag Details

Double-click on any tag to view its details including:
- Tag name
- Commit SHA
- Tag type (lightweight/annotated)
- Tagger information (for annotated tags)
- Tag message (for annotated tags)

### Deleting Tags

1. Select a tag from the list
2. Click "Delete" button
3. Confirm deletion

**Note:** This only deletes the local tag.

### Pushing Tags

#### Push Single Tag
1. Select a tag from the list
2. Click "Push" button

#### Push All Tags
1. Click "Push All" button
2. Confirm to push all local tags to remote

## Tag Naming Rules

Tag names must follow Git's naming rules:

✅ **Valid:**
- `v1.0.0`
- `release-2023-01-15`
- `stable`
- `feature/new-api`

❌ **Invalid:**
- Names with spaces: `v 1.0.0`
- Names starting or ending with dots: `.tag`, `tag.`
- Names with special characters: `tag~1`, `tag^1`, `tag?`, `tag*`
- Names containing `..`: `tag..name`
- Names containing `@{`: `tag@{0}`
- Names starting or ending with `/`: `/tag`, `tag/`

## Best Practices

1. **Use Semantic Versioning**: Follow semver (e.g., v1.2.3) for release tags
2. **Annotated Tags for Releases**: Use annotated tags for releases to include metadata
3. **Lightweight Tags for Bookmarks**: Use lightweight tags for temporary markers
4. **Descriptive Messages**: Write clear, descriptive messages for annotated tags
5. **Push After Creating**: Remember to push tags to share them with others
6. **Tag After Testing**: Create release tags only after thorough testing

## Example Workflow

```python
from clevergit.core.repo import Repo

# Open repository
repo = Repo.open(".")

# Create a release tag
tag = repo.create_annotated_tag(
    "v1.0.0",
    "Release 1.0.0\\n\\nFeatures:\\n- Tag management\\n- UI improvements"
)

# Verify it was created
tags = repo.list_tags()
print(f"Created {len(tags)} tag(s)")

# Push to remote
repo.push_tag("v1.0.0")
print("Tag pushed to remote")
```

## Error Handling

```python
from clevergit.git.errors import TagError

try:
    repo.create_tag("v1.0.0")
except TagError as e:
    print(f"Tag error: {e}")
    # Handle error (tag might already exist, invalid name, etc.)
```

## Common Tag Errors

- **Tag already exists**: You're trying to create a tag that already exists
- **Invalid tag name**: The tag name contains invalid characters
- **No remote configured**: Trying to push without a remote repository
- **Tag does not exist**: Trying to delete a non-existent tag
- **Empty message**: Annotated tags require a non-empty message

## Additional Resources

- [Git Tagging Documentation](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [Semantic Versioning](https://semver.org/)
- CleverGit API Documentation
