"""SEED Dashboard Core

Provides the base terminal dashboard interface using Textual library.
"""

from textual.app import App
from textual.widgets import Header, Footer
from textual.containers import Container
from rich.panel import Panel
from rich.table import Table
from typing import Dict, Any, Optional

class DashboardApp(App):
    """Terminal-based dashboard for SEED.
    
    Features:
    - System metrics display
    - Agent status monitoring
    - Simple navigation
    """
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
    }
    
    #sidebar {
        width: 30%;
        background: $panel;
        height: 100%;
    }
    
    #main {
        width: 70%;
        background: $surface;
        height: 100%;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.title = "SEED Dashboard"
    
    def compose(self):
        """Create child widgets."""
        yield Header()
        with Container():
            yield self._create_sidebar()
            yield self._create_main_view()
        yield Footer()
    
    def _create_sidebar(self):
        """Create sidebar with metrics."""
        return Panel(
            Table(
                title="System Metrics",
                show_header=False,
                box=None
            ),
            title="Overview"
        )
    
    def _create_main_view(self):
        """Create main content area."""
        return Panel(
            "Welcome to SEED",
            title="Dashboard"
        )