"""Tag management module."""

from typing import List, Optional
from clevergit.git.client import GitClient
from clevergit.git.errors import TagError
from clevergit.models.tag_info import TagInfo


def create_tag(client: GitClient, name: str, commit: Optional[str] = None) -> TagInfo:
    """
    Create a lightweight tag.
    
    Args:
        client: Git client instance
        name: Tag name
        commit: Optional commit SHA/ref to tag (defaults to HEAD)
        
    Returns:
        TagInfo object for the created tag
    """
    if not name or not name.strip():
        raise TagError("Tag name cannot be empty")
    
    if not _is_valid_tag_name(name):
        raise TagError(f"Invalid tag name: {name}")
    
    # Check if tag already exists
    existing_tags = [t["name"] for t in client.list_tags()]
    if name in existing_tags:
        raise TagError(f"Tag already exists: {name}")
    
    client.create_tag(name, commit)
    
    # Get the created tag info
    tags = client.list_tags()
    for tag_dict in tags:
        if tag_dict["name"] == name:
            return TagInfo(
                name=tag_dict["name"],
                commit_sha=tag_dict["commit_sha"],
                is_annotated=tag_dict["is_annotated"],
                message=tag_dict.get("message"),
                tagger=tag_dict.get("tagger"),
                date=tag_dict.get("date"),
            )
    
    # Fallback if tag not found in list
    return TagInfo(name=name, commit_sha=commit or "HEAD", is_annotated=False)


def create_annotated_tag(
    client: GitClient, name: str, message: str, commit: Optional[str] = None
) -> TagInfo:
    """
    Create an annotated tag.
    
    Args:
        client: Git client instance
        name: Tag name
        message: Tag message
        commit: Optional commit SHA/ref to tag (defaults to HEAD)
        
    Returns:
        TagInfo object for the created tag
    """
    if not name or not name.strip():
        raise TagError("Tag name cannot be empty")
    
    if not _is_valid_tag_name(name):
        raise TagError(f"Invalid tag name: {name}")
    
    if not message or not message.strip():
        raise TagError("Tag message cannot be empty for annotated tags")
    
    # Check if tag already exists
    existing_tags = [t["name"] for t in client.list_tags()]
    if name in existing_tags:
        raise TagError(f"Tag already exists: {name}")
    
    client.create_annotated_tag(name, message, commit)
    
    # Get the created tag info
    tags = client.list_tags()
    for tag_dict in tags:
        if tag_dict["name"] == name:
            return TagInfo(
                name=tag_dict["name"],
                commit_sha=tag_dict["commit_sha"],
                is_annotated=tag_dict["is_annotated"],
                message=tag_dict.get("message"),
                tagger=tag_dict.get("tagger"),
                date=tag_dict.get("date"),
            )
    
    # Fallback if tag not found in list
    return TagInfo(
        name=name, commit_sha=commit or "HEAD", is_annotated=True, message=message
    )


def delete_tag(client: GitClient, name: str) -> None:
    """
    Delete a tag.
    
    Args:
        client: Git client instance
        name: Tag name to delete
    """
    if not name or not name.strip():
        raise TagError("Tag name cannot be empty")
    
    # Check if tag exists
    existing_tags = [t["name"] for t in client.list_tags()]
    if name not in existing_tags:
        raise TagError(f"Tag does not exist: {name}")
    
    client.delete_tag(name)


def list_tags(client: GitClient) -> List[TagInfo]:
    """
    List all tags.
    
    Args:
        client: Git client instance
        
    Returns:
        List of TagInfo objects
    """
    tags = []
    
    for tag_dict in client.list_tags():
        tags.append(
            TagInfo(
                name=tag_dict["name"],
                commit_sha=tag_dict["commit_sha"],
                is_annotated=tag_dict["is_annotated"],
                message=tag_dict.get("message"),
                tagger=tag_dict.get("tagger"),
                date=tag_dict.get("date"),
            )
        )
    
    return tags


def push_tag(client: GitClient, name: str, remote: str = "origin") -> None:
    """
    Push a specific tag to remote.
    
    Args:
        client: Git client instance
        name: Tag name to push
        remote: Remote name (defaults to "origin")
    """
    if not name or not name.strip():
        raise TagError("Tag name cannot be empty")
    
    # Check if tag exists
    existing_tags = [t["name"] for t in client.list_tags()]
    if name not in existing_tags:
        raise TagError(f"Tag does not exist: {name}")
    
    client.push_tag(name, remote)


def push_all_tags(client: GitClient, remote: str = "origin") -> None:
    """
    Push all tags to remote.
    
    Args:
        client: Git client instance
        remote: Remote name (defaults to "origin")
    """
    client.push_all_tags(remote)


def _is_valid_tag_name(name: str) -> bool:
    """Validate tag name according to Git rules."""
    if not name:
        return False
    
    # Git tag names have similar rules to branch names
    invalid_chars = [' ', '~', '^', ':', '?', '*', '[', ']', '\\', '\n', '\r', '\t', '\x7f']
    if any(char in name for char in invalid_chars):
        return False
    
    # Check for @{ sequence which has special meaning in Git
    if '@{' in name:
        return False
    
    if name.startswith('.') or name.endswith('.'):
        return False
    
    if name.endswith('.lock'):
        return False
    
    if '..' in name:
        return False
    
    if name.startswith('/') or name.endswith('/'):
        return False
    
    return True
