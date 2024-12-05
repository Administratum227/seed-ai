"""SEED Command-Line Interface

Provides a streamlined CLI for the SEED framework with two main modes:
1. Interactive dashboard (default)
2. Command processing
"""

import typer
from rich.console import Console
from pathlib import Path
from typing import Optional

app = typer.Typer(help="SEED Framework CLI")
console = Console()

@app.command()
def launch(port: int = 8501, no_browser: bool = False):
    """Launch the SEED dashboard."""
    from ..dashboard import DashboardApp
    app = DashboardApp()
    console.print("[bold blue]SEED Dashboard[/bold blue]")
    app.run()

@app.command()
def verify():
    """Verify SEED installation."""
    console.print("[bold]Verifying installation...[/bold]")
    # Add verification logic here

def main():
    """CLI entry point."""
    app()