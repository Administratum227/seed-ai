"""SEED Command Line Interface

Provides a clean, intuitive command-line interface for the SEED framework.
Focuses on common workflows and essential functionality.

Commands:
    launch      Launch the dashboard (default)
    verify      Check installation and dependencies
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.traceback import install

# Set up error handling
install(show_locals=True)
console = Console()

app = typer.Typer(
    help="SEED: Scalable Ecosystem for Evolving Digital Agents",
    add_completion=False
)

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

def main():
    """Main CLI entry point."""
    try:
        if len(sys.argv) == 1:
            # No arguments - launch dashboard
            launch()
        else:
            # Process CLI arguments
            app()
    except KeyboardInterrupt:
        console.print("\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()