"""Repository commands."""

import typer
from pathlib import Path
from typing import Optional

app = typer.Typer()


@app.command("init")
def init_repo(
    path: Optional[Path] = typer.Argument(
        None,
        help="Path where to initialize repository (default: current directory)"
    ),
    bare: bool = typer.Option(
        False,
        "--bare",
        help="Create a bare repository"
    )
):
    """Initialize a new Git repository."""
    from clevergit.core.repo import Repo
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.init(repo_path, bare=bare)
        typer.secho(
            f"✓ Initialized repository at {repo.path}",
            fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("clone")
def clone_repo(
    url: str = typer.Argument(..., help="Repository URL to clone"),
    path: Optional[Path] = typer.Argument(
        None,
        help="Destination path (default: repository name)"
    )
):
    """Clone a remote repository."""
    from clevergit.git.client import GitClient
    
    try:
        # Use current directory if path not specified
        dest_path = path or Path.cwd()
        
        client = GitClient(dest_path.parent if path else dest_path)
        result = client.run_command(['clone', url, str(dest_path)])
        
        if result.success:
            typer.secho(f"✓ Cloned repository to {dest_path}", fg=typer.colors.GREEN)
        else:
            raise Exception(result.error)
            
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command("remote")
def manage_remote(
    action: str = typer.Argument(..., help="Action: add, remove, list, show"),
    name: Optional[str] = typer.Argument(None, help="Remote name"),
    url: Optional[str] = typer.Argument(None, help="Remote URL"),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to repository (default: current directory)"
    )
):
    """Manage remote repositories."""
    from clevergit.core.repo import Repo
    from clevergit.core import remote
    
    repo_path = path or Path.cwd()
    
    try:
        repo = Repo.open(repo_path)
        
        if action == "add":
            if not name or not url:
                typer.secho("Error: 'add' requires name and url", fg=typer.colors.RED, err=True)
                raise typer.Exit(1)
            remote.add_remote(repo.path, name, url)
            typer.secho(f"✓ Added remote '{name}'", fg=typer.colors.GREEN)
            
        elif action == "remove":
            if not name:
                typer.secho("Error: 'remove' requires name", fg=typer.colors.RED, err=True)
                raise typer.Exit(1)
            remote.remove_remote(repo.path, name)
            typer.secho(f"✓ Removed remote '{name}'", fg=typer.colors.GREEN)
            
        elif action == "list":
            remotes = remote.list_remotes(repo.path, verbose=True)
            for name, url in remotes.items():
                typer.echo(f"{name}\t{url}")
                
        elif action == "show":
            if not name:
                name = "origin"
            info = remote.show_remote(repo.path, name)
            typer.echo(info['details'])
            
        else:
            typer.secho(f"Error: Unknown action '{action}'", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)
            
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
