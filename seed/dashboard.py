"""
SEED Interactive Dashboard
------------------------
Provides a rich terminal user interface for monitoring and managing AI agents.
Built with Textual for a responsive TUI experience.
"""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, DataTable, Button, Static
from textual.reactive import reactive
from textual import work
import asyncio
from datetime import datetime
from typing import Dict, Any

from .core import SeedCore, AgentStatus

class AgentCard(Static):
    """Widget displaying individual agent status and controls."""
    
    agent_id = reactive("")
    status = reactive(AgentStatus.SEED)
    resources = reactive({})
    capabilities = reactive({})

    def compose(self) -> ComposeResult:
        """Create child widgets of an agent card."""
        yield Container(
            Static(f"Agent: {self.agent_id}", classes="agent-title"),
            Static(f"Status: {self.status.value}", id="status"),
            Static("Resources:", classes="section-header"),
            DataTable(id="resources"),
            Static("Capabilities:", classes="section-header"),
            DataTable(id="capabilities"),
            Button("Evolve", variant="primary", id="evolve"),
            Button("Terminate", variant="error", id="terminate"),
            classes="agent-card"
        )

    def update_data(self, data: Dict[str, Any]) -> None:
        """Update agent card with new monitoring data."""
        self.status = data["status"]
        self.resources = data["resources"]
        self.capabilities = data["capabilities"]
        
        # Update tables
        self.query_one("#resources").clear()
        for resource, value in self.resources.items():
            self.query_one("#resources").add_row(resource, f"{value:.2f}")
            
        self.query_one("#capabilities").clear()
        for cap, prof in self.capabilities.items():
            self.query_one("#capabilities").add_row(cap, f"{prof:.2%}")

class SeedDashboard(App):
    """Main dashboard application."""
    
    TITLE = "SEED Dashboard"
    CSS = """
    .agent-card {
        width: 100%;
        height: auto;
        border: solid green;
        margin: 1;
        padding: 1;
    }

    .agent-title {
        background: $accent;
        color: $text;
        padding: 1;
        text-align: center;
        font-weight: bold;
    }

    .section-header {
        color: $text;
        text-align: left;
        padding-top: 1;
        padding-bottom: 1;
    }

    DataTable {
        height: auto;
        max-height: 30vh;
    }
    """

    def __init__(self):
        super().__init__()
        self.core = SeedCore()
        self.agent_cards = {}

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Container(id="agents-container")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the dashboard when it's mounted."""
        # Start background monitoring
        self.monitor_agents()

    @work
    async def monitor_agents(self) -> None:
        """Background worker to monitor agent status."""
        while True:
            agents = self.core.list_agents()
            
            # Update existing agents
            for agent in agents:
                status = self.core.monitor_growth(agent.agent_id)
                
                if agent.agent_id not in self.agent_cards:
                    # Create new card for agent
                    card = AgentCard()
                    self.agent_cards[agent.agent_id] = card
                    self.query_one("#agents-container").mount(card)
                
                # Update card data
                self.agent_cards[agent.agent_id].update_data(status)
            
            # Remove cards for terminated agents
            active_ids = {agent.agent_id for agent in agents}
            terminated = set(self.agent_cards.keys()) - active_ids
            for agent_id in terminated:
                self.agent_cards[agent_id].remove()
                del self.agent_cards[agent_id]
            
            await asyncio.sleep(1)  # Update frequency

    async def handle_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button = event.button
        agent_card = button.parent
        agent_id = agent_card.agent_id

        if button.id == "evolve":
            await self.evolve_agent(agent_id)
        elif button.id == "terminate":
            await self.terminate_agent(agent_id)

    async def evolve_agent(self, agent_id: str) -> None:
        """Trigger agent evolution."""
        try:
            success = self.core.evolve_agent(agent_id)
            if success:
                self.notify("Agent evolution successful", severity="information")
            else:
                self.notify("Agent evolution failed", severity="error")
        except Exception as e:
            self.notify(f"Error evolving agent: {str(e)}", severity="error")

    async def terminate_agent(self, agent_id: str) -> None:
        """Terminate an agent."""
        try:
            self.core.terminate_agent(agent_id)
            self.notify(f"Agent {agent_id} terminated", severity="warning")
        except Exception as e:
            self.notify(f"Error terminating agent: {str(e)}", severity="error")

def launch_dashboard(port: int = 8501) -> str:
    """Launch the dashboard and return its URL."""
    app = SeedDashboard()
    app.run()
    return f"http://localhost:{port}"