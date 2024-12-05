"""SEED Framework Entry Point

Provides the main entry point for the SEED framework, enabling both interactive
dashboard mode and command-line operation.

Usage:
    python -m seed          # Launch dashboard
    python -m seed [cmd]    # Execute command
"""

import sys
import logging
from rich.console import Console
from rich.traceback import install

# Enable rich error formatting
install(show_locals=True)
console = Console()

def main():
    """Primary entry point for SEED framework."""
    try:
        if len(sys.argv) == 1:
            # No arguments - launch interactive dashboard
            from seed.dashboard import launch_dashboard
            console.print("[bold blue]SEED Framework Dashboard[/bold blue]")
            launch_dashboard()
        else:
            # Process command line arguments
            from seed.cli import cli
            cli()
    except KeyboardInterrupt:
        console.print("\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logging.exception("Startup error")
        sys.exit(1)

if __name__ == "__main__":
    main()