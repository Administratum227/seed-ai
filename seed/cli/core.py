"""
SEED CLI Core
------------
Provides the core terminal interface functionality for the SEED framework.
Focuses on simplicity and immediate usability with a clean TUI dashboard.
"""

from rich.live import Live
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from textual.app import App
from textual.widgets import Header, Footer, Static
from textual.widget import Widget
from typing import Dict, Any, Optional
import asyncio
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DashboardApp(App):
    """
    Terminal-based dashboard for SEED system monitoring and control.
    
    Features:
    - Real-time system metrics
    - Agent status monitoring
    - Task queue visualization
    - Interactive command input
    """
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 2fr;
    }
    
    #sidebar {
        dock: left;
        width: 30%;
        background: $panel;
        height: 100%;
    }
    
    #main {
        dock: right;
        width: 70%;
        background: $surface;
        height: 100%;
    }
    
    .status {
        height: auto;
        margin: 1;
        padding: 1;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        background: $boost;
        color: $text;
    }
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dashboard with optional configuration."""
        super().__init__()
        self.config = config or {}
        self.refresh_interval = 1.0  # seconds
    
    async def on_mount(self) -> None:
        """Set up the dashboard layout when app is mounted."""
        # Create layout
        self.body = Layout()
        self.body.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Add header
        self.header = Header(show_clock=True)
        await self.view.dock(self.header, edge="top")
        
        # Split main area
        self.body["main"].split_row(
            Layout(name="sidebar", ratio=1),
            Layout(name="content", ratio=2)
        )
        
        # Add footer with status
        self.footer = Footer()
        await self.view.dock(self.footer, edge="bottom")
        
        # Start refresh timer
        self.set_interval(self.refresh_interval, self.refresh_display)
    
    async def refresh_display(self) -> None:
        """Update dashboard metrics and display."""
        try:
            metrics = await self.get_system_metrics()
            self.update_metrics_display(metrics)
        except Exception as e:
            logger.error(f"Failed to refresh display: {e}")
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Gather current system metrics."""
        # To be implemented with actual metrics
        return {
            "agents": {
                "total": 0,
                "active": 0
            },
            "tasks": {
                "queued": 0,
                "running": 0,
                "completed": 0
            },
            "system": {
                "cpu": 0.0,
                "memory": 0.0,
                "uptime": 0
            }
        }
    
    def update_metrics_display(self, metrics: Dict[str, Any]) -> None:
        """Update displayed metrics."""
        # Update sidebar metrics
        sidebar = self.body["main"]["sidebar"]
        sidebar.update(
            Panel(
                self.create_metrics_table(metrics),
                title="System Metrics",
                border_style="blue"
            )
        )
        
        # Update main content
        content = self.body["main"]["content"]
        content.update(
            Panel(
                self.create_status_display(metrics),
                title="Status & Activity",
                border_style="green"
            )
        )
    
    def create_metrics_table(self, metrics: Dict[str, Any]) -> Table:
        """Create a table of current metrics."""
        table = Table(show_header=False)
        table.add_column("Metric")
        table.add_column("Value")
        
        # Add metrics rows
        table.add_row("Agents Active", str(metrics["agents"]["active"]))
        table.add_row("Tasks Queued", str(metrics["tasks"]["queued"]))
        table.add_row("CPU Usage", f"{metrics['system']['cpu']:.1f}%")
        table.add_row("Memory Usage", f"{metrics['system']['memory']:.1f}%")
        
        return table
    
    def create_status_display(self, metrics: Dict[str, Any]) -> str:
        """Create status display text."""
        return "\n".join([
            "📊 System Status: Online",
            f"⏰ Uptime: {metrics['system']['uptime']}s",
            f"🤖 Active Agents: {metrics['agents']['active']}",
            f"📋 Running Tasks: {metrics['tasks']['running']}"
        ])
    
    async def on_key(self, event) -> None:
        """Handle keyboard input."""
        if event.key == "q":
            await self.shutdown()
        elif event.key == "r":
            await self.refresh_display()

def launch_dashboard(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Launch the terminal dashboard interface.
    
    Args:
        config: Optional configuration dictionary
    """
    app = DashboardApp(config)
    app.run()