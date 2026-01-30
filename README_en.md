# CleverGit - Python Git Client

An advanced Python Git client tool that provides more user-friendly, higher-level Git operation abstractions.

## Key Features

- 🎯 **High-Level Semantics** - Use `repo.commit_all()` instead of complex Git commands
- 🔧 **Modular Design** - Clear architecture, easy to extend and maintain  
- 🚀 **CLI First** - Powerful command-line interface for daily Git operations
- 🤖 **AI Friendly** - Code structure suitable for Copilot-assisted development

## Quick Start

### Install Dependencies

```bash
cd /Users/zhenyutao/Downloads/HandyApp/CleverGit
pip install -e .
```

### Basic Usage

```bash
# View repository status
sg status

# Commit all changes
sg commit all -m "feat: add new feature"

# View commit history
sg log --oneline

# Branch management
sg branch list
sg branch new feature/auth
sg branch switch main
```

## Project Structure

```
clevergit/
├── core/          # Core Git logic
├── git/           # Git adapter layer
├── models/        # Data models
├── cli/           # CLI commands
├── utils/         # Utility functions
└── ui/            # GUI/TUI (reserved)
```

## Python API

```python
from clevergit import Repo

# Open repository
repo = Repo.open(".")

# View status
status = repo.status()
print(f"Modified files: {len(status.modified)}")

# Commit changes
repo.commit_all("fix: resolve issue")

# Branch operations
repo.create_branch("feature/new")
repo.checkout("feature/new")
```

## Development

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black clevergit/
ruff check clevergit/
```

## Features

✅ Implemented:
- Repository management (initialize, open)
- Status viewing
- Commit operations
- Branch management
- History records
- Remote operations

🚧 To be implemented:
- GUI interface
- AI-assisted commit message generation
- Conflict resolution wizard
- Git Flow support
