# Blame Feature User Guide

## What is Git Blame?

Git blame shows you who last modified each line of a file and when. This is useful for:
- Understanding who wrote specific code
- Finding when a particular line was changed
- Tracking down the author of a bug or feature
- Understanding the history of a file

## How to Use the Blame Feature

### Step 1: Open a Repository

1. Click **📁 Open Repository** button or press `Ctrl+O`
2. Select your Git repository folder

### Step 2: Select a File

1. Look at the **File Status** panel on the right side
2. Click on any file in the list

### Step 3: Open Blame View

You have three ways to open the blame view:

**Option 1: Toolbar Button**
- Click the **👤 Blame** button in the toolbar

**Option 2: Keyboard Shortcut**
- Press `Ctrl+B`

**Option 3: Menu**
- Click **Edit** → **Blame File**

### Step 4: View Blame Information

The blame window will show a table with the following columns:
- **Line**: Line number in the file
- **Commit**: Short commit SHA (7 characters)
- **Author**: Person who last modified this line
- **Date**: When the line was last modified
- **Content**: The actual line content

### Step 5: View Commit Details

To see the full details of a commit:
1. Click on any row in the blame table
2. A diff viewer window will open showing:
   - Complete commit message
   - All files changed in that commit
   - Line-by-line differences

### Step 6: Refresh Blame Data

If the file has changed since you opened the blame view:
1. Click the **🔄 Refresh** button in the blame window
2. The blame data will be updated with the latest information

## Tips and Tricks

### Multiple Blame Windows
- You can open multiple blame windows for different files
- Each window operates independently
- Use this to compare changes across files

### Understanding the Display
- Hover over a commit SHA to see the full commit message
- Hover over an author name to see their email address
- The content column uses a monospace font for better readability

### Common Use Cases

**Finding Who Wrote Code:**
```
1. Open blame for the file
2. Find the line of interest
3. Look at the Author column
```

**Finding When Code Changed:**
```
1. Open blame for the file
2. Find the line of interest
3. Look at the Date column
```

**Understanding a Change:**
```
1. Open blame for the file
2. Click on the line of interest
3. Review the full commit in the diff viewer
```

## Limitations

- Blame only works on tracked files (files that have been committed)
- Untracked files or newly created files cannot be blamed
- Very large files may take a moment to process

## Troubleshooting

**Problem:** Blame button is disabled
- **Solution:** Make sure you have selected a file in the status view

**Problem:** "No blame data available"
- **Solution:** The file may be untracked. Commit the file first.

**Problem:** Blame window shows outdated information
- **Solution:** Click the Refresh button to update the data

**Problem:** Cannot see commit details
- **Solution:** Make sure you're clicking on a row, not just hovering

## Example Workflow

Here's a typical workflow for investigating a bug:

1. **Open Repository**: Open your project repository
2. **Find the File**: Locate the file with the bug in the status view
3. **Open Blame**: Press `Ctrl+B` to open blame
4. **Find the Line**: Scroll to the line with the bug
5. **Check Author**: See who last modified this line
6. **View Commit**: Click the row to see the full commit
7. **Understand Context**: Review what else changed in that commit
8. **Contact Author**: Now you know who to talk to about the bug!

## Keyboard Shortcuts

- `Ctrl+B` - Open blame for selected file
- `Ctrl+D` - Open diff viewer
- `F5` - Refresh repository view

## Visual Guide

```
┌─────────────────────────────────────────────────────────────┐
│ Blame: src/main.py                     [🔄 Refresh]         │
├─────┬──────────┬────────────┬────────────┬─────────────────┤
│Line │ Commit   │ Author     │ Date       │ Content         │
├─────┼──────────┼────────────┼────────────┼─────────────────┤
│  1  │ abc123d  │ John Doe   │ 2024-01-15 │ # Main file     │
│  2  │ def456e  │ Jane Smith │ 2024-02-20 │ import sys      │
│  3  │ abc123d  │ John Doe   │ 2024-01-15 │                 │
│  4  │ ghi789f  │ Bob Jones  │ 2024-03-10 │ def main():     │
└─────┴──────────┴────────────┴────────────┴─────────────────┘
         Click any row to view commit details
```

## Advanced Features

### Blame at Different Points in History
Currently, blame shows the state at HEAD (the current commit). Future versions may support:
- Blaming at a specific commit
- Showing historical blame
- Comparing blame across branches

### Integration with Other Features
The blame feature integrates with:
- **Diff Viewer**: Click commits to see full diffs
- **Status View**: Select files to blame
- **Commit History**: Navigate from blame to log view

## Best Practices

1. **Use blame for investigation, not blame**: The name "blame" is unfortunate - use it to understand code, not to point fingers!

2. **Consider the context**: A person's name on a line doesn't mean they're responsible for bugs - maybe they were just reformatting code.

3. **Check the full commit**: Always click through to see the full commit context before drawing conclusions.

4. **Combine with git log**: Use blame together with the commit history to understand the full story.

## Getting Help

If you encounter issues with the blame feature:
1. Check this guide for common problems
2. Verify your Git installation is up to date (Git 2.0+)
3. Make sure the file has been committed to the repository
4. Try refreshing the repository view (F5)

## Related Features

- **Commit History**: View all commits in the log view
- **Diff Viewer**: See detailed changes between commits
- **File Status**: Monitor which files have changed
- **Branch View**: Understand which branch you're working on

---

Enjoy using the blame feature to understand your codebase better!
