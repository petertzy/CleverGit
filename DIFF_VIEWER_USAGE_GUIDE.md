# Diff Viewer Integration Guide

## How to Access the Diff Viewer

The diff viewer is now fully integrated into CleverGit's main interface. Here are **three ways** to use it:

### 1. View All Working Tree Changes (Toolbar Button)

**Location:** Top toolbar, next to the Push button

**Button:** `📊 View Diff`

**Action:** Click this button to see all changes in your working tree compared to HEAD

**Shortcut:** `Ctrl+D` (or Edit → View Diff menu)

```
┌─────────────────────────────────────────────────────────────┐
│ ⬇️ Clone  📁 Open  🔄 Refresh  ✅ Commit  ⬇️ Pull  ⬆️ Push  📊 View Diff │
└─────────────────────────────────────────────────────────────┘
                                                          ↑
                                                   NEW BUTTON!
```

### 2. View Diff for Specific File (Click in Status View)

**Location:** Right panel, "File Status" section

**Action:** Click on any file name under Modified/Staged/Untracked to see its diff

**Example:**
```
File Status
├─ Modified Files
│  ├─ example.py          ← Click here!
│  └─ test.txt            ← Or here!
├─ Staged Files
│  └─ config.yaml         ← Or here!
└─ Untracked Files
   └─ new_feature.py      ← Or here!
```

When you click a file, a new window opens showing only that file's changes.

### 3. View Diff for Specific Commit (Click in Commit History)

**Location:** Right panel, "Commit History" section

**Action:** Click on any commit in the table to see what changed in that commit

**Example:**
```
Commit History
┌─────────┬─────────┬─────────────┬──────────────────┐
│ Commit  │ Author  │ Date        │ Message          │
├─────────┼─────────┼─────────────┼──────────────────┤
│ abc1234 │ John    │ 2024-02-04  │ Add feature X    │ ← Click here!
│ def5678 │ Jane    │ 2024-02-03  │ Fix bug Y        │ ← Or here!
│ ghi9012 │ John    │ 2024-02-02  │ Initial commit   │ ← Or here!
└─────────┴─────────┴─────────────┴──────────────────┘
```

When you click a commit, a new window opens showing all changes in that commit.

## What You'll See in the Diff Viewer

When the diff viewer window opens, you'll see:

### Top Controls
```
┌──────────────────────────────────────────────────────────┐
│ View: [Unified ▼] | ← Previous | Next → | Line Numbers: ON | Collapse Unchanged │
└──────────────────────────────────────────────────────────┘
```

### Statistics Bar
```
Files changed: 2 | +15 | -8
```
- Green numbers = lines added
- Red numbers = lines deleted

### Diff Content

**Unified View (default):**
Shows traditional diff format with syntax highlighting:
- 🟢 Green background = added lines
- 🔴 Red background = deleted lines
- ⚪ White background = context (unchanged) lines
- 🔵 Blue text = section headers

**Side-by-Side View:**
Switch using the dropdown to see before/after comparison:
- Left panel = "Before" (old version)
- Right panel = "After" (new version)
- Synchronized scrolling

### Navigation
- **Next/Previous buttons** jump between changed sections (hunks)
- **Collapse Unchanged** hides long sections of unchanged code
- **Line Numbers toggle** shows/hides line numbers

## Quick Start Example

1. Open a repository in CleverGit
2. Make some changes to a file (don't commit yet)
3. Click the **📊 View Diff** button in the toolbar
4. See all your changes highlighted!

OR

1. Open a repository in CleverGit
2. Look at "File Status" section
3. Click on any modified file
4. See just that file's changes!

OR

1. Open a repository in CleverGit
2. Look at "Commit History" section
3. Click on any commit row
4. See what changed in that commit!

## Features at a Glance

✅ **Unified diff view** - Traditional diff format
✅ **Side-by-side view** - Before/after comparison
✅ **Syntax highlighting** - Color-coded changes
✅ **Statistics** - See files changed and line counts
✅ **Navigation** - Jump between changes quickly
✅ **Collapse unchanged** - Focus on what matters
✅ **Line numbers** - Track exact locations
✅ **Multiple access points** - Button, menu, clicks

## Keyboard Shortcuts

- `Ctrl+D` - Open diff viewer (working tree changes)
- Click on files/commits for specific diffs
- Use Previous/Next buttons to navigate changes

---

**Note:** The diff viewer opens in a separate window, so you can have multiple diff views open at once if needed!
