# Command Palette User Guide

The Command Palette is a powerful quick-access feature that allows you to search and navigate your repository, as well as execute commands without using menus or remembering keyboard shortcuts.

## Opening the Command Palette

There are two ways to open the Command Palette:

1. **Keyboard Shortcut**: Press `Ctrl+P` (default)
2. **Menu**: View → Command Palette

## Features

### 1. File Search

Search for any file in your repository using fuzzy matching:

- Type part of the filename to find it quickly
- Results show with 📄 icon
- Press Enter to select a file
- Example: typing "main" will find "main.py", "MainWindow.java", etc.

### 2. Commit Search

Search through recent commits:

- Search by commit message, author, or SHA
- Results show with 📝 icon  
- Shows first 100 commits by default
- Example: typing "fix bug" will find commits with those words

### 3. Branch Search

Find and switch branches:

- Search for any branch in your repository
- Results show with 🌿 icon
- Current branch is marked with ✓
- Press Enter to checkout the selected branch
- Example: typing "feat" will find "feature/new-ui", "feat/api", etc.

### 4. Quick Commands

Execute common Git operations without navigating menus:

- Results show with ⚡ icon
- Type command name to filter
- Available commands:
  - `refresh` - Refresh the current view
  - `commit` - Open commit dialog
  - `pull` - Pull from remote
  - `push` - Push to remote
  - `fetch` - Fetch from remote
  - `checkout` - Checkout a branch
  - `merge` - Merge branches
  - `stash` - Toggle stash view
  - `tag` - Toggle tags view
  - `diff` - View diff
  - `blame` - Show blame for file

## Fuzzy Search

The Command Palette uses intelligent fuzzy matching to find what you're looking for:

### How It Works

1. **Exact Match**: Typing the exact text gives the highest score
2. **Contains Match**: Text containing your search ranks high
3. **Character Match**: Characters in order (even scattered) will match
4. **Case Insensitive**: Search is not case-sensitive

### Examples

Searching for "main":
- ✅ "main.py" (exact match in filename)
- ✅ "src/main.py" (contains match)
- ✅ "MainWindow.java" (case-insensitive)

Searching for "mp":
- ✅ "main.py" (m...p scattered match)
- ✅ "MyProject.java" (M...P scattered match)

Searching for "scb":
- ✅ "src/components/Button.tsx" (s...c...b path abbreviation)

## Keyboard Navigation

Once the Command Palette is open:

- `↑` / `↓` - Navigate through results
- `Enter` - Select the highlighted item
- `Esc` - Close the palette
- Type to filter results in real-time

## Tips and Tricks

1. **Speed Navigation**: Use keyboard shortcuts to open the palette and quickly navigate to files
2. **Path Searching**: For nested files, type parts of the path (e.g., "src/app" for files in that directory)
3. **Commit Messages**: Search commits by key words from their messages
4. **Branch Prefixes**: Find feature branches by typing "feat" or "feature"
5. **Quick Actions**: Type single letters to find commands (e.g., "p" for push/pull)

## Performance

- File search is limited to 500 files for performance
- Commit search shows the most recent 100 commits
- Results are limited to the top 50 matches
- Search operates in real-time with minimal lag

## Customization

### Changing the Keyboard Shortcut

You can customize the Command Palette shortcut:

1. Open Help → Keyboard Shortcuts (or press `F1`)
2. Go to the "Customize" tab
3. Find "Open command palette" in the Search category
4. Click "Edit" and enter your preferred shortcut
5. Click "Save"

### Extending with Custom Commands

The Command Palette can be extended programmatically (for developers):

```python
# Register a custom command
palette.register_command("my_command", callback_function)
```

## Troubleshooting

### No Results Found

If you're not seeing expected results:

- Check that you have a repository open
- Ensure the file/commit/branch exists
- Try a broader search term
- Check spelling and case

### Slow Search

If search feels slow:

- The palette loads all items on first open
- Large repositories (>500 files) may take a moment to index
- Subsequent searches are fast (items are cached)

### Command Not Working

If a command doesn't execute:

- Ensure you have a repository open (some commands require this)
- Check that the command name is correct
- See the main window for error messages

## Future Enhancements

Planned features for the Command Palette:

- Search in file contents (grep integration)
- Recent items/Most used commands
- Command history
- Bookmark favorite files/commits
- Tag search
- Custom search filters
