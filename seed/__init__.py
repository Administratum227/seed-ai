"""SEED: Scalable Ecosystem for Evolving Digital Agents

A framework for creating and managing autonomous AI agents.
"""

from .runtime import AgentRuntime, RuntimeConfig
from .capability import Capability, CapabilityType
from .exceptions import SeedError, RuntimeError

__version__ = "0.1.0"
__all__ = [
    "AgentRuntime",
    "RuntimeConfig",
    "Capability",
    "CapabilityType",
    "SeedError",
    "RuntimeError"
]
