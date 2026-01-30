# Project Documentation (CleverGit - Git Client, Python Implementation)

## 1. Project Background & Goals

This project aims to develop an advanced Git client tool **CleverGit** using **Python**, with focus on:

* Provide **more user-friendly, higher-level** Git operation abstractions
* Lower the learning curve for daily Git usage (especially complex commands)
* Support **CLI-first, GUI-extensible** architecture design
* Clear code structure, convenient for future enhancement with **GitHub Copilot / AI** assistance

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

  * `typer` (recommended, type-friendly, Copilot-compatible)
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

## 9. Copilot Collaboration Suggestions

* For each module:

  * Write **clear docstrings** first
  * Specify input / output types clearly
* Break into small functions, avoid "giant methods"
* Use clear business semantics in TODOs, not technical details

---

## 10. Future Expansion Directions

* GUI (graphical interface)
* AI assistance:

  * Auto-generate commit messages
  * Conflict resolution suggestions
* Plugin system (hooks)
* Git Flow / Trunk Based workflow support

---

## 11. One-Sentence Project Summary

> Wrap Git's "intent layer" in Python, make Git usable like objects, not remembered like incantations.
