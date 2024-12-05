"""Agent discovery and network topology management.

Implements agent discovery, capability sharing, and network maintenance."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Set, Optional
import asyncio
import logging

@dataclass
class NetworkNode:
    """Information about a node in the network."""
    agent_id: str
    host: str
    port: int
    capabilities: Set[str] = field(default_factory=set)
    last_seen: datetime = field(default_factory=datetime.now)
    status: str = "active"

class DiscoveryService:
    """Manages agent discovery and network topology.
    
    Features:
    - Periodic discovery broadcasts
    - Node health monitoring
    - Capability registration
    - Network topology tracking
    """
    
    def __init__(self, broadcast_interval: int = 60):
        self.nodes: Dict[str, NetworkNode] = {}
        self.broadcast_interval = broadcast_interval
        self.logger = logging.getLogger("seed.network.discovery")
        self._tasks: Set[asyncio.Task] = set()
    
    async def start(self) -> None:
        """Start discovery service."""
        self._tasks.add(
            asyncio.create_task(self._discovery_loop())
        )
        self._tasks.add(
            asyncio.create_task(self._health_check_loop())
        )
    
    async def stop(self) -> None:
        """Stop discovery service."""
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
    
    async def register_node(
        self,
        agent_id: str,
        host: str,
        port: int,
        capabilities: Set[str]
    ) -> None:
        """Register a new node in the network.
        
        Args:
            agent_id: ID of the agent
            host: Node hostname/IP
            port: Node port
            capabilities: Set of node capabilities
        """
        self.nodes[agent_id] = NetworkNode(
            agent_id=agent_id,
            host=host,
            port=port,
            capabilities=capabilities
        )
        self.logger.info(f"Registered node {agent_id}")
    
    async def _discovery_loop(self) -> None:
        """Periodic discovery broadcast loop."""
        while True:
            try:
                await self._broadcast_discovery()
                await asyncio.sleep(self.broadcast_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Discovery error: {e}")
                await asyncio.sleep(5)
    
    async def _health_check_loop(self) -> None:
        """Monitor node health status."""
        while True:
            try:
                await self._check_nodes_health()
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(5)