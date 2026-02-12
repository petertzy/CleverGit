# Git Flow Workflow Guide

## Overview

CleverGit now supports the Git Flow workflow pattern, a popular branching model for managing feature development, releases, and hotfixes in a structured way.

## What is Git Flow?

Git Flow is a branching model that defines a strict branching structure designed around project releases. It uses two main branches:

- **main** (or master) - Contains production-ready code
- **develop** - Integration branch for features

And three types of supporting branches:

- **feature/** - For developing new features
- **release/** - For preparing new releases
- **hotfix/** - For quick fixes to production

## Getting Started

### 1. Initialize Git Flow

1. Open your repository in CleverGit
2. Navigate to the **Git Flow** tab in the left panel
3. Click **Initialize Git Flow**
4. Configure your branch names and prefixes (defaults are recommended)
5. Click **OK**

The develop branch will be created automatically from your main branch.

### 2. Working with Features

**Starting a Feature:**
1. Go to the **Features** tab in the Git Flow panel
2. Click **Start Feature**
3. Enter a feature name (e.g., "user-authentication")
4. Click **OK**

This creates and checks out a new branch: `feature/user-authentication`

**Finishing a Feature:**
1. Commit all your changes on the feature branch
2. Go to the **Features** tab
3. Click **Finish Feature**
4. Select the feature from the dropdown
5. Click **OK**

This will:
- Merge the feature into develop
- Delete the feature branch
- Switch to the develop branch

### 3. Working with Releases

**Starting a Release:**
1. Go to the **Releases** tab in the Git Flow panel
2. Click **Start Release**
3. Enter a version number (e.g., "1.0.0")
4. Click **OK**

This creates a release branch: `release/1.0.0` from develop

**Finishing a Release:**
1. Make any final release adjustments and commit them
2. Go to the **Releases** tab
3. Click **Finish Release**
4. Select the release from the dropdown
5. Optionally enter a tag message
6. Click **OK**

This will:
- Merge the release into main
- Create a version tag (e.g., "v1.0.0")
- Merge the release back into develop
- Delete the release branch
- Switch to the develop branch

### 4. Working with Hotfixes

**Starting a Hotfix:**
1. Go to the **Hotfixes** tab in the Git Flow panel
2. Click **Start Hotfix**
3. Enter a version number (e.g., "1.0.1")
4. Click **OK**

This creates a hotfix branch: `hotfix/1.0.1` from main

**Finishing a Hotfix:**
1. Fix the issue and commit your changes
2. Go to the **Hotfixes** tab
3. Click **Finish Hotfix**
4. Select the hotfix from the dropdown
5. Optionally enter a tag message
6. Click **OK**

This will:
- Merge the hotfix into main
- Create a version tag (e.g., "v1.0.1")
- Merge the hotfix back into develop
- Delete the hotfix branch
- Switch to the develop branch

## Workflow Visualization

The Git Flow panel includes a visual diagram showing the branching model:

```
main     ──●────────────●────────────●──
             \          /\          /
              \        /  \        /
release        ●──────●    ●──────●
                    /        \
develop   ──●──────●──────────●──────●──
              \    /          /
               \  /          /
feature         ●──────────●
```

## Best Practices

1. **Always work on feature branches** - Never commit directly to develop or main
2. **Keep features small and focused** - Easier to review and merge
3. **Use descriptive branch names** - e.g., "add-login-page" instead of "feature1"
4. **Write meaningful commit messages** - Explain what and why
5. **Test thoroughly before finishing** - Especially for releases and hotfixes
6. **Use semantic versioning** - For release and hotfix versions (e.g., 1.0.0, 1.0.1)

## Important Notes

- **Clean working directory required** - All operations require you to commit or stash changes first
- **Branches are deleted after finishing** - The feature/release/hotfix branches are automatically removed
- **Tags are created for releases and hotfixes** - Version tags are automatically created and prefixed with "v"

## Troubleshooting

**"Git Flow is not initialized"**
- Click the "Initialize Git Flow" button in the Git Flow panel

**"Cannot start feature with uncommitted changes"**
- Commit or stash your current changes before starting a new feature

**"Branch already exists"**
- You already have a feature/release/hotfix with that name
- Choose a different name or finish the existing one first

**"Master branch does not exist"**
- Make sure you have at least one commit in your repository before initializing Git Flow

## Configuration

You can customize Git Flow configuration during initialization:

- **Production branch name** - Default: "main"
- **Development branch name** - Default: "develop"
- **Feature prefix** - Default: "feature/"
- **Release prefix** - Default: "release/"
- **Hotfix prefix** - Default: "hotfix/"
- **Version tag prefix** - Default: "v"

## Additional Resources

- [Original Git Flow Article](https://nvie.com/posts/a-successful-git-branching-model/)
- [Git Flow Cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/)
- [When to Use Git Flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
