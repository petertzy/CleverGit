"""Branch commands."""

import typer
from pathlib import Path
from typing import Optional

app = typer.Typer()


@app.command("create")
def create_branch(
    name: str = typer.Argument(..., help="Branch name"),
    checkout: bool = typer.Option(False, "--checkout", "-c", help="Checkout after creating"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Create a new branch."""
    from clevergit.core.repo import Repo
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        branch = repo.create_branch(name, checkout=checkout)
        
        if checkout:
            typer.secho(f"✓ Created and checked out branch '{name}'", fg=typer.colors.GREEN)
        else:
            typer.secho(f"✓ Created branch '{name}'", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_branch(
    name: str = typer.Argument(..., help="Branch name"),
    force: bool = typer.Option(False, "--force", "-f", help="Force delete"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Delete a branch."""
    from clevergit.core.repo import Repo
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        repo.delete_branch(name, force=force)
        typer.secho(f"✓ Deleted branch '{name}'", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("list")
def list_branches(
    all: bool = typer.Option(False, "--all", "-a", help="Include remote branches"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """List all branches."""
    from clevergit.core.repo import Repo
    from clevergit.utils.formatter import format_branches
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        branches = repo.list_branches(remote=all)
        
        output = format_branches(branches)
        typer.echo(output)
        
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("switch")
def switch_branch(
    name: str = typer.Argument(..., help="Branch name"),
    create: bool = typer.Option(False, "--create", "-c", help="Create if doesn't exist"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Switch to a different branch."""
    from clevergit.core.repo import Repo
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        
        if create:
            repo.create_branch(name, checkout=True)
            typer.secho(f"✓ Created and switched to branch '{name}'", fg=typer.colors.GREEN)
        else:
            repo.checkout(name)
            typer.secho(f"✓ Switched to branch '{name}'", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("merge")
def merge_branch(
    name: str = typer.Argument(..., help="Branch to merge"),
    no_ff: bool = typer.Option(False, "--no-ff", help="Force merge commit"),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Merge commit message"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Merge a branch into current branch."""
    from clevergit.core.repo import Repo
    from clevergit.core import merge as merge_ops
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        merge_ops.merge_branch(repo.path, name, no_ff=no_ff, message=message)
        typer.secho(f"✓ Merged branch '{name}'", fg=typer.colors.GREEN)
        
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
