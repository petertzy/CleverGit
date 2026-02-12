"""Remote operations commands."""

import typer
from pathlib import Path
from typing import Optional

app = typer.Typer()


@app.command("fetch")
def fetch_remote(
    remote: str = typer.Argument(
        "origin",
        help="Remote name to fetch from"
    ),
    prune: bool = typer.Option(
        False,
        "--prune",
        "-p",
        help="Remove deleted remote branches"
    ),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Path to repository (default: current directory)"
    )
):
    """Fetch updates from a remote repository."""
    from clevergit.core.repo import Repo
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        repo.fetch(remote=remote, prune=prune)
        typer.secho(
            f"✓ Fetched updates from '{remote}'",
            fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("pull")
def pull_remote(
    remote: str = typer.Argument(
        "origin",
        help="Remote name to pull from"
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="Branch to pull (default: current branch)"
    ),
    rebase: bool = typer.Option(
        False,
        "--rebase",
        "-r",
        help="Use rebase instead of merge"
    ),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Path to repository (default: current directory)"
    )
):
    """Pull updates from a remote repository."""
    from clevergit.core.repo import Repo
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        repo.pull(remote=remote, branch=branch, rebase=rebase)
        typer.secho(
            f"✓ Pulled updates from '{remote}'",
            fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("push")
def push_remote(
    remote: str = typer.Argument(
        "origin",
        help="Remote name to push to"
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="Branch to push (default: current branch)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force push (use with caution!)"
    ),
    set_upstream: bool = typer.Option(
        False,
        "--set-upstream",
        "-u",
        help="Set upstream tracking branch"
    ),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Path to repository (default: current directory)"
    )
):
    """Push commits to a remote repository."""
    from clevergit.core.repo import Repo
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        
        # Show warning for force push
        if force:
            typer.secho(
                "⚠ Warning: Force push can overwrite remote history!",
                fg=typer.colors.YELLOW
            )
            confirm = typer.confirm("Are you sure you want to force push?")
            if not confirm:
                typer.echo("Push cancelled.")
                raise typer.Exit(0)
        
        repo.push(remote=remote, branch=branch, force=force, set_upstream=set_upstream)
        typer.secho(
            f"✓ Pushed commits to '{remote}'",
            fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
