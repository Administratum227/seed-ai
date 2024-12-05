"""SEED Command Line Interface

Provides a clean, intuitive command-line interface for the SEED framework.
Focuses on common workflows and essential functionality.

Commands:
    launch      Launch the dashboard (default)
    verify      Check installation and dependencies
    configure   Update framework settings
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

app = typer.Typer(
    help="SEED: Scalable Ecosystem for Evolving Digital Agents",
    add_completion=False
)
console = Console()

@app.command()
def launch(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-h",
        help="Dashboard host address"
    ),
    port: int = typer.Option(
        8501,
        "--port",
        "-p",
        help="Dashboard port number"
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Custom config file path"
    )
):
    """Launch the SEED dashboard interface."""
    from ..dashboard import launch_dashboard
    console.print("[bold blue]Launching SEED Dashboard...[/bold blue]")
    launch_dashboard(host=host, port=port)

@app.command()
def verify(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output"
    )
):
    """Verify SEED installation and configuration."""
    from ..core.preflight import run_checks
    console.print("[bold]Verifying SEED installation...[/bold]")
    
    passed, report = run_checks()
    if passed:
        console.print("[bold green]✓ All checks passed![/bold green]")
    else:
        console.print("[bold red]Verification failed:[/bold red]")
        for error in report["errors"]:
            console.print(f"[red]✗ {error}[/red]")
        for warning in report["warnings"]:
            console.print(f"[yellow]⚠ {warning}[/yellow]")

def cli():
    """CLI entry point."""
    app()