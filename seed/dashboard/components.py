"""SEED Dashboard Components

Defines the core UI components for the SEED terminal dashboard.
Focuses on clarity, usability, and essential functionality.
"""

from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import reactive
from rich.panel import Panel
from rich.table import Table
from typing import Dict, Any, List

class MetricsPanel(Static):
    """Displays key system metrics and status information.
    
    Features:
    - Real-time metric updates
    - Clear data visualization
    - Status indicators
    """
    
    metrics: Dict[str, Any] = reactive({})
    
    def on_mount(self) -> None:
        """Initialize the metrics display."""
        self.update_metrics({
            'agents': 0,
            'tasks': 0,
            'cpu': 0.0,
            'memory': 0.0
        })
    
    def update_metrics(self, new_metrics: Dict[str, Any]) -> None:
        """Update displayed metrics.
        
        Args:
            new_metrics: Dictionary of updated metric values
        """
        self.metrics = new_metrics
    
    def render(self) -> Panel:
        """Render the metrics panel."""
        table = Table(show_header=False, box=None)
        table.add_column("Metric")
        table.add_column("Value")
        
        # Add metric rows
        table.add_row("🤖 Active Agents", str(self.metrics.get('agents', 0)))
        table.add_row("📋 Tasks Running", str(self.metrics.get('tasks', 0)))
        table.add_row("📊 CPU Usage", f"{self.metrics.get('cpu', 0):.1f}%")
        table.add_row("📒 Memory Usage", f"{self.metrics.get('memory', 0):.1f}%")
        
        return Panel(
            table,
            title="System Metrics",
            border_style="blue"
        )

class AgentList(Static):
    """Displays and manages active agents.
    
    Features:
    - Agent status tracking
    - Basic controls
    - Status indicators
    """
    
    agents: List[Dict[str, Any]] = reactive([])
    
    def on_mount(self) -> None:
        """Initialize the agent list."""
        self.update_agents([])
    
    def update_agents(self, agent_list: List[Dict[str, Any]]) -> None:
        """Update the agent list.
        
        Args:
            agent_list: List of agent status dictionaries
        """
        self.agents = agent_list
    
    def render(self) -> Panel:
        """Render the agent list panel."""
        if not self.agents:
            return Panel(
                "No active agents",
                title="Agents",
                border_style="green"
            )
        
        table = Table(box=None)
        table.add_column("Agent")
        table.add_column("Status")
        table.add_column("Tasks")
        
        for agent in self.agents:
            table.add_row(
                agent['name'],
                agent['status'],
                str(agent.get('tasks', 0))
            )
        
        return Panel(
            table,
            title="Active Agents",
            border_style="green"
        )