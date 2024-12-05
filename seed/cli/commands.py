"""SEED CLI Command Implementation

Implements the core command-line interface for the SEED framework with a focus
on simplicity, discoverability, and immediate productivity. The CLI follows
a task-oriented design pattern where each command maps to a specific user goal.
"""

import typer
from typing import Optional
from pathlib import Path
import sys
import logging
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn

from ..preflight import run_preflight
from ..dashboard import launch_dashboard
from ..config import load_config
from ..exceptions import SeedError

app = typer.Typer(
    help="SEED: Scalable Ecosystem for Evolving Digital Agents",
    add_completion=False
)
console = Console()

@app.command()
def boot(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Dashboard host"),
    port: int = typer.Option(8501, "--port", "-p", help="Dashboard port"),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
    no_browser: bool = typer.Option(
        False, "--no-browser", help="Don't open browser automatically"
    )
):
    """Boot the SEED environment and launch dashboard.
    
    This command performs essential initialization and launches the web interface:
    1. Runs comprehensive pre-flight system checks
    2. Validates and loads configuration
    3. Initializes core services
    4. Launches the dashboard interface
    """
    try:
        # Show welcome message
        console.print(Panel(
            "[bold blue]SEED AI Framework[/bold blue]\n"
            "Launching environment..."
        ))
        
        # Run pre-flight checks
        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            console=console
        ) as progress:
            task = progress.add_task("Running pre-flight checks...")
            passed, report = run_preflight()
            progress.update(task, completed=True)
        
        if not passed:
            console.print("\n[bold red]Pre-flight checks failed:[/bold red]")
            for error in report["errors"]:
                console.print(f"❌ {error}")
            for warning in report["warnings"]:
                console.print(f"⚠️  {warning}")
            sys.exit(1)
        
        # Load and validate configuration
        config_data = load_config(config) if config else load_config()
        
        # Launch dashboard interface
        console.print(f"\n📊 Launching dashboard at http://{host}:{port}")
        launch_dashboard(
            host=host,
            port=port,
            config=config_data,
            open_browser=not no_browser
        )
        
        console.print(
            "\n✨ [green]Environment ready![/green]\n\n"
            f"Dashboard: http://{host}:{port}\n"
            "Press Ctrl+C to shut down"
        )
        
    except KeyboardInterrupt:
        console.print("\n👋 Shutting down...")
        sys.exit(0)
    except SeedError as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {str(e)}")
        logging.exception("Boot error")
        sys.exit(1)

@app.command()
def verify(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed output"
    )
):
    """Verify SEED installation and configuration.
    
    Runs comprehensive checks to validate:
    - System requirements
    - Installation integrity
    - Configuration validity
    - Service availability
    """
    try:
        console.print("🔍 Verifying SEED installation...\n")
        
        passed, report = run_preflight()
        
        if verbose:
            # Show detailed system information
            console.print("[bold]System Information:[/bold]")
            for key, value in report["system"].items():
                console.print(f"{key}: {value}")
            console.print()
        
        if passed:
            console.print("[bold green]✓ All checks passed![/bold green]")
            if report["warnings"]:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in report["warnings"]:
                    console.print(f"⚠️  {warning}")
        else:
            console.print("[bold red]× Verification failed:[/bold red]")
            for error in report["errors"]:
                console.print(f"❌ {error}")
            for warning in report["warnings"]:
                console.print(f"⚠️  {warning}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[bold red]Verification error:[/bold red] {str(e)}")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    try:
        app()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()