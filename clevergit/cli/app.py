"""Main CLI application entry point."""

import typer
from pathlib import Path
from typing import Optional

from clevergit.cli import repo_cmd, commit_cmd, branch_cmd, remote_cmd

app = typer.Typer(
    name="clevergit",
    help="CleverGit - Smart Git operations made simple",
    no_args_is_help=True
)

# Register subcommands
app.add_typer(repo_cmd.app, name="repo", help="Repository operations")
app.add_typer(commit_cmd.app, name="commit", help="Commit operations")
app.add_typer(branch_cmd.app, name="branch", help="Branch operations")
app.add_typer(remote_cmd.app, name="remote", help="Remote operations")


@app.command()
def version():
    """Show CleverGit version."""
    typer.echo("CleverGit v0.1.0")


@app.command()
def status(
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Show repository status."""
    from clevergit.core.repo import Repo
    from clevergit.utils.formatter import format_status
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        status_list = repo.status()
        
        output = format_status(status_list)
        typer.echo(output)
        
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def log(
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    ),
    max_count: int = typer.Option(
        10,
        "--max",
        "-n",
        help="Maximum number of commits to show"
    ),
    oneline: bool = typer.Option(
        False,
        "--oneline",
        help="Show compact one-line format"
    )
):
    """Show commit history."""
    from clevergit.core.repo import Repo
    from clevergit.utils.formatter import format_log
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        commits = repo.log(max_count=max_count)
        
        output = format_log(commits, oneline=oneline)
        typer.echo(output)
        
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def fetch(
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
    from clevergit.cli.remote_cmd import fetch_remote
    fetch_remote(remote=remote, prune=prune, path=path)


@app.command()
def pull(
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
    from clevergit.cli.remote_cmd import pull_remote
    pull_remote(remote=remote, branch=branch, rebase=rebase, path=path)


@app.command()
def push(
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
    from clevergit.cli.remote_cmd import push_remote
    push_remote(remote=remote, branch=branch, force=force, set_upstream=set_upstream, path=path)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
