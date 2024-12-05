"""
SEED Command Line Interface
--------------------------
Provides a streamlined CLI for launching and managing AI agents through an interactive dashboard.
Built with Typer for CLI and Textual for TUI dashboard.
"""

import typer
import asyncio
from typing import Optional
from pathlib import Path
import os
import toml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn
import webbrowser
from contextlib import asynccontextmanager

from .dashboard import launch_dashboard
from .core import SeedCore, AgentTemplate
from .config import SeedConfig, DEFAULT_CONFIG

app = typer.Typer(help="SEED: Scalable Ecosystem for Evolving Digital Agents")
console = Console()

def load_config(config_path: Optional[Path] = None) -> SeedConfig:
    """Load SEED configuration from file or create default."""
    if not config_path:
        config_path = Path.home() / ".seed" / "config.toml"
    
    if config_path.exists():
        return SeedConfig(**toml.load(config_path))
    
    # Create default config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = DEFAULT_CONFIG
    with open(config_path, "w") as f:
        toml.dump(config, f)
    return SeedConfig(**config)

@app.command()
def init(
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to config file"
    )
):
    """Initialize SEED environment and create configuration."""
    with console.status("Initializing SEED environment..."):
        config = load_config(config_path)
        
        # Create necessary directories
        config.data_dir.mkdir(parents=True, exist_ok=True)
        config.log_dir.mkdir(parents=True, exist_ok=True)
        
        console.print("✨ SEED environment initialized successfully!")
        console.print(f"Configuration stored at: {config_path or '~/.seed/config.toml'}")

@app.command()
def dashboard(
    port: int = typer.Option(8501, "--port", "-p", help="Port for dashboard"),
    browser: bool = typer.Option(True, "--browser/--no-browser", help="Open in browser")
):
    """Launch the SEED dashboard interface."""
    try:
        # Start dashboard server
        with console.status("Launching SEED dashboard..."):
            url = launch_dashboard(port=port)
            console.print(f"✨ Dashboard running at: {url}")
            
            if browser:
                webbrowser.open(url)
                console.print("📱 Opening dashboard in browser...")
            
            console.print("\n🌱 Press Ctrl+C to stop the dashboard")
            
            try:
                # Keep the dashboard running
                asyncio.get_event_loop().run_forever()
            except KeyboardInterrupt:
                console.print("\n👋 Shutting down SEED dashboard...")
    except Exception as e:
        console.print(f"❌ Error launching dashboard: {str(e)}", style="bold red")
        raise typer.Exit(1)

@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="Name for the new agent"),
    template: Optional[Path] = typer.Option(
        None, "--template", "-t", help="Path to agent template file"
    ),
    capabilities: Optional[str] = typer.Option(
        None, 
        "--capabilities", 
        "-c", 
        help="Comma-separated list of capabilities"
    )
):
    """Create a new AI agent from template or capabilities list."""
    try:
        with console.status(f"Creating agent '{name}'..."):
            core = SeedCore()
            
            # Load template or create from capabilities
            if template and template.exists():
                agent_template = AgentTemplate.from_file(template)
            else:
                caps = capabilities.split(",") if capabilities else ["basic_reasoning"]
                agent_template = AgentTemplate(
                    capabilities=caps,
                    growth_parameters={"max_resources": 1000, "evolution_rate": 0.1}
                )
            
            # Create and initialize agent
            agent = core.plant(agent_template)
            agent.germinate()
            
            console.print(f"✨ Created agent '{name}' [{agent.agent_id}]")
            console.print("📊 Launch dashboard to monitor agent with: seed dashboard")
    except Exception as e:
        console.print(f"❌ Error creating agent: {str(e)}", style="bold red")
        raise typer.Exit(1)

@app.command()
def status():
    """Show status of all running agents."""
    try:
        core = SeedCore()
        agents = core.list_agents()
        
        if not agents:
            console.print("No active agents found.")
            return
        
        console.print("\n🌱 SEED Agents Status")
        console.print("=" * 50)
        
        for agent in agents:
            status = core.monitor_growth(agent.agent_id)
            console.print(f"\nAgent: {agent.agent_id}")
            console.print(f"Status: {status['status'].value}")
            console.print("Resources:")
            for resource, value in status["resources"].items():
                console.print(f"  {resource}: {value:.2f}")
            console.print("Capabilities:")
            for cap, prof in status["capabilities"].items():
                console.print(f"  {cap}: {prof:.2%}")
    except Exception as e:
        console.print(f"❌ Error getting status: {str(e)}", style="bold red")
        raise typer.Exit(1)

def run():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        console.print(f"❌ Unexpected error: {str(e)}", style="bold red")
        raise typer.Exit(1)

if __name__ == "__main__":
    run()