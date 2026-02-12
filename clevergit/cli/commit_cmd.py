"""Commit commands."""

import typer
from pathlib import Path
from typing import Optional, List

app = typer.Typer()


@app.command("create")
def create_commit(
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
    all: bool = typer.Option(False, "--all", "-a", help="Commit all tracked files"),
    files: Optional[List[str]] = typer.Argument(None, help="Specific files to commit"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Create a new commit."""
    from clevergit.core.repo import Repo
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        
        if all:
            commit = repo.commit_all(message)
        elif files:
            commit = repo.commit_files(files, message)
        else:
            typer.secho(
                "Error: Specify --all or provide file names",
                fg=typer.colors.RED,
                err=True
            )
            raise typer.Exit(1)
        
        typer.secho(f"✓ Created commit {commit.short_sha}", fg=typer.colors.GREEN)
        typer.echo(f"  {commit.subject}")
        
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("amend")
def amend_commit(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="New commit message"),
    no_edit: bool = typer.Option(False, "--no-edit", help="Keep existing message"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Amend the last commit."""
    from clevergit.core.repo import Repo
    from clevergit.git.client import GitClient
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        client = GitClient(repo.path)
        
        cmd = ['commit', '--amend']
        if no_edit:
            cmd.append('--no-edit')
        elif message:
            cmd.extend(['-m', message])
        
        result = client.run_command(cmd)
        
        if result.success:
            typer.secho("✓ Amended commit", fg=typer.colors.GREEN)
        else:
            raise Exception(result.error)
            
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("undo")
def undo_commit(
    soft: bool = typer.Option(True, "--soft", help="Keep changes staged"),
    hard: bool = typer.Option(False, "--hard", help="Discard all changes"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Undo the last commit."""
    from clevergit.core.repo import Repo
    from clevergit.git.client import GitClient
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        client = GitClient(repo.path)
        
        reset_type = '--hard' if hard else '--soft'
        result = client.run_command(['reset', reset_type, 'HEAD~1'])
        
        if result.success:
            typer.secho("✓ Undid last commit", fg=typer.colors.GREEN)
        else:
            raise Exception(result.error)
            
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
