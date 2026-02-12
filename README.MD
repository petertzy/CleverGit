# Project Documentation (CleverGit - Git Client, Python Implementation)

[![PyPI version](https://badge.fury.io/py/clevergit.svg)](https://pypi.org/project/clevergit/) [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Available on PyPI**: [clevergit](https://pypi.org/project/clevergit/)

## Quick Start

CleverGit provides **two ways to interact** with your Git repositories:

### 🖥️ **Graphical User Interface (GUI)**

Launch the GUI application for an intuitive, visual Git experience:

```bash
sgg
# or
python -m clevergit.ui.main
```

**Features:**
- Point-and-click repository management
- Visual file status display
- Branch management with drag-and-drop
- Commit history viewer
- Dialog-based operations
- **Enhanced Diff Viewer** - Professional, SmartGit-inspired code difference presentation
  - Softer color scheme for reduced eye strain
  - Word-level highlighting to spot exact changes
  - Improved visual spacing and separation
  - Side-by-side and unified views
- **Command Palette** - Quick search and command execution (`Ctrl+P`)
  - Search files, commits, and branches with fuzzy matching
  - Execute commands without navigating menus
  - Keyboard-driven workflow

👉 **For detailed GUI documentation, see [GUI_USAGE.md](GUI_USAGE.md)**

### 💻 **Command Line Interface (CLI)**

Use powerful command-line commands for scriptable Git operations:

```bash
# View repository status
sg status

# Commit all changes
sg commit all -m "feat: add new feature"

# View commit history
sg log --oneline

# Manage branches
sg branch list
sg branch new feature/auth
sg branch switch main
```

**Features:**
- Fast, efficient terminal-based workflow
- Scriptable operations
- Batch processing support
- Integration with other tools

### 💻 **Python API**

Use CleverGit programmatically in your Python scripts:

```python
from clevergit import Repo

# Open repository
repo = Repo.open(".")

# Check status
status = repo.status()
print(f"Modified files: {len(status.modified)}")

# Create commit
repo.commit_all("fix: resolve issue")

# Branch operations
repo.create_branch("feature/new")
repo.checkout("feature/new")
```

### 📦 Installation

```bash
# Install from PyPI (recommended)
pip install clevergit

# Install from source (development)
git clone https://github.com/petertzy/CleverGit.git
cd CleverGit
pip install -e .

# Verify installation
sgg --version  # GUI version check
sg --version   # CLI version check
```

### 🚀 Publishing to PyPI (Maintainers)

Use this checklist to publish a new release to PyPI.

1. Update version numbers:
  - `pyproject.toml` -> `project.version`
  - `clevergit/__init__.py` -> `__version__`
2. Commit and tag:

```bash
git add pyproject.toml clevergit/__init__.py
git commit -m "chore: bump version to vX.Y.Z"
git tag vX.Y.Z
git push origin main
git push origin vX.Y.Z
```

3. Build the package:

```bash
python -m pip install --upgrade build twine
rm -rf dist build
python -m build
python -m twine check dist/*
```

4. Upload to PyPI:

```bash
python -m twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: your PyPI API token (starts with `pypi-`)

If you do not have a token yet:
1. Enable 2FA for your PyPI account.
2. Create a token at https://pypi.org/manage/account/token/

---

## 1. Project Background & Goals

This project aims to develop an advanced Git client tool **CleverGit** using **Python**, with focus on:

* Provide **more user-friendly, higher-level** Git operation abstractions
* Lower the learning curve for daily Git usage (especially complex commands)
* Support **CLI-first, GUI-extensible** architecture design

Target users:

* Developers familiar with Git basics but don't want to memorize commands frequently
* Users who want to operate Git in Python within scripts / toolchains

---

## 2. Design Principles

1. **High-level semantics, not command concatenation**
   Example:

   * `repo.commit_all("fix login bug")`
   * Instead of `git commit -am "..."`

2. **Readability first**
   Class names and method names should express "user intent" rather than Git details

3. **Modular & Extensible**

   * Decouple CLI / GUI / API
   * Can add TUI / Web UI later

4. **Failure is explainable**

   * Convert Git errors to "human-readable" exception messages

---

## 3. Technology Stack

* Python >= 3.10
* Git calling methods:

  * Preferred: `GitPython`
  * Fallback: `subprocess` (for scenarios GitPython doesn't support)
* CLI framework:

  * `typer` (recommended, type-friendly)
* GUI (future):

  * `PySide6` or `Tkinter`

---

## 4. Core Feature Planning

### 4.1 Repository Management

* Open / Initialize repository
* Detect repository status
* Current branch, HEAD status

```text
✔ Is it a Git repository
✔ Are there uncommitted changes
✔ Is it behind / ahead of remote branch
```

---

### 4.2 Status View

* Modified files
* Untracked files
* Staged files
* Conflicted files

Support:

* Group by file type
* Output as structured objects for UI use

---

### 4.3 Commit

* Commit all changes
* Selective commit (specific files)
* Auto-generate commit message (optional)
* Pre-commit checks (lint / test hooks)

---

### 4.4 Branch Management

* List branches (local / remote)
* Create / Delete / Rename branches
* Switch branches
* Display branch relationships (simple DAG)

---

### 4.5 Merge & Rebase (High-level Wrapper)

* Safe merge (detect conflicts)
* Interactive rebase workflow (step-by-step)
* Conflict file list + hints

---

### 4.6 Remote Repository Operations

* fetch / pull / push
* Show commits to be pushed / pulled
* force push risk warning

---

### 4.7 History (Log)

* Concise log view (like `git log --oneline --graph`)
* Filter by author / time / branch
* Single commit details

---

## 5. Project File Structure (Recommended)

```text
clevergit/
├── README.md
├── pyproject.toml
├── clevergit/
│   ├── __init__.py
│   ├── core/                  # Core Git logic
│   │   ├── repo.py             # Repository object (core entry point)
│   │   ├── status.py           # Status analysis
│   │   ├── commit.py           # Commit logic
│   │   ├── branch.py           # Branch management
│   │   ├── merge.py            # merge / rebase
│   │   ├── remote.py           # fetch / pull / push
│   │   └── log.py              # History records
│   │
│   ├── git/                    # Git adapter layer
│   │   ├── client.py           # GitPython / subprocess wrapper
│   │   └── errors.py           # Git errors → business exceptions
│   │
│   ├── cli/                    # CLI layer
│   │   ├── app.py              # Typer entry point
│   │   ├── repo_cmd.py
│   │   ├── commit_cmd.py
│   │   └── branch_cmd.py
│   │
│   ├── ui/                     # GUI / TUI (reserved)
│   │   └── __init__.py
│   │
│   ├── models/                 # Domain models (DTO)
│   │   ├── file_status.py
│   │   ├── commit_info.py
│   │   └── branch_info.py
│   │
│   └── utils/
│       ├── formatter.py        # Output formatting
│       └── helpers.py
│
└── tests/
    ├── test_repo.py
    ├── test_status.py
    └── test_commit.py
```

---

## 6. Core Object Design Example

### Repo (Core Entry Point)

```python
repo = Repo.open(".")

repo.status()
repo.commit_all("fix: login bug")
repo.create_branch("feature/auth")
repo.checkout("feature/auth")
```

Design goals:

* **One Repo object = One Git repository**
* Most features start from here

---

## 7. CLI Design Example

```bash
sg status
sg commit -m "fix bug"
sg branch new feature/auth
sg branch switch main
sg log --oneline
```

CLI principles:

* Short commands
* Don't require users to understand Git detail parameters

---

## 8. Error Handling Strategy

* Git raw errors → Custom exceptions
* CLI layer catches exceptions → User-friendly hints

Example:

```text
❌ Current branch has uncommitted changes, cannot switch branches
Suggestions:
- Commit changes
- Or use sg stash
```

---

## 9. Future Expansion Directions

* GUI (graphical interface)
* AI assistance:

  * Auto-generate commit messages
  * Conflict resolution suggestions
* Plugin system (hooks)
* Git Flow / Trunk Based workflow support

---

## 10. One-Sentence Project Summary

> Wrap Git's "intent layer" in Python, make Git usable like objects, not remembered like incantations.

---

## 🤝 Contributing

We welcome contributions from everyone! CleverGit is an open-source project, and your help is essential to making it better.

### How You Can Contribute

- 🐛 **Report bugs** - Found an issue? Let us know!
- 💡 **Suggest features** - Have ideas for improvements?
- 📝 **Improve documentation** - Help make the docs clearer
- 🔧 **Submit pull requests** - Fix bugs or add features
- ⭐ **Star the project** - Show your support!
- 🌍 **Translate** - Help make CleverGit accessible to more users

### Getting Started

1. Fork the repository
2. Clone your fork
   ```bash
   git clone https://github.com/YOUR_USERNAME/CleverGit.git
   cd CleverGit
   ```
3. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Make your changes and commit
   ```bash
   git commit -m "feat: add awesome feature"
   ```
5. Push and create a pull request
   ```bash
   git push origin feature/your-feature-name
   ```

### Development Setup

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Check code quality
black .
ruff check .
```

### Questions?

Feel free to open an [issue](https://github.com/petertzy/CleverGit/issues) or start a discussion!

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
