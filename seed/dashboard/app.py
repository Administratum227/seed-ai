"""SEED Dashboard Application

Implements the main terminal dashboard interface using Textual.
Focuses on providing essential monitoring and control capabilities
with a clean, intuitive interface.
"""

from textual.app import App
from textual.widgets import Header, Footer
from textual.containers import Container
from rich.console import Console
from typing import Optional, Dict, Any
import asyncio

from .components import MetricsPanel, AgentList

class Dashboard(App):
    """Main dashboard application.
    
    Features:
    - Real-time metrics display
    - Agent management
    - System monitoring
    - Simple navigation
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh")
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dashboard with optional configuration.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__()
        self.config = config or {}
        self.console = Console()
    
    def compose(self):
        """Create and compose the interface layout."""
        yield Header(show_clock=True)
        
        with Container():
            yield MetricsPanel(id="metrics")
            yield AgentList(id="agents")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Handle application mounting."""
        # Start background tasks
        self.set_interval(1.0, self.update_metrics)
    
    async def update_metrics(self) -> None:
        """Update displayed metrics."""
        try:
            # Get current metrics
            metrics = await self._gather_metrics()
            
            # Update panels
            self.query_one(MetricsPanel).update_metrics(metrics)
            self.query_one(AgentList).update_agents(
                await self._get_agent_status()
            )
            
        except Exception as e:
            self.console.print(f"[red]Error updating metrics:[/red] {str(e)}")
    
    async def _gather_metrics(self) -> Dict[str, Any]:
        """Gather current system metrics."""
        # TODO: Implement actual metric gathering
        return {
            'agents': 0,
            'tasks': 0,
            'cpu': 0.0,
            'memory': 0.0
        }
    
    async def _get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents."""
        # TODO: Implement agent status gathering
        return []
    
    async def action_quit(self) -> None:
        """Handle quit action."""
        self.console.print("\n[yellow]Shutting down...[/yellow]")
        await self.shutdown()
    
    async def action_refresh(self) -> None:
        """Handle manual refresh action."""
        await self.update_metrics()

def launch_dashboard(
    host: str = "127.0.0.1",
    port: int = 8501,
    config: Optional[Dict[str, Any]] = None
) -> None:
    """Launch the dashboard application.
    
    Args:
        host: Interface host address
        port: Port number
        config: Optional configuration
    """
    app = Dashboard(config)
    app.run()