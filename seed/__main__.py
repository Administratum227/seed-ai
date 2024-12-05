"""
SEED Framework Entry Point
-------------------------
Provides the main entry point for the SEED framework, enabling simple
single-command execution through `python -m seed` or the `seed` command.
"""

import sys
import logging
from rich.console import Console
from rich.traceback import install

from .cli.core import launch_dashboard
from .cli.commands import cli

# Configure rich error handling
install(show_locals=True)
console = Console()

def main():
    """
    Main entry point for SEED framework.
    
    If no arguments are provided, launches the terminal dashboard.
    Otherwise, processes command line arguments through the CLI.
    """
    try:
        if len(sys.argv) == 1:
            # No arguments - launch dashboard
            launch_dashboard()
        else:
            # Process CLI arguments
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