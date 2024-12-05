"""Base capability implementation and type definitions.

Defines the core interfaces and base classes for implementing SEED capabilities.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class CapabilityType(Enum):
    """Types of capabilities an agent can possess."""
    
    COGNITIVE = "cognitive"      # Reasoning, planning, decision making
    INTERACTIVE = "interactive"  # Communication, API calls, user interaction
    SPECIALIZED = "specialized"  # Domain-specific capabilities
    SYSTEM = "system"           # Resource management, state handling

@dataclass
class Capability:
    """Base class for defining agent capabilities.
    
    Attributes:
        name: Unique identifier for the capability
        type: Type of capability
        description: Human-readable description
        version: Semantic version of the capability
        requirements: List of required capabilities or resources
        parameters: Parameter definitions and constraints
    """
    
    name: str
    type: CapabilityType
    description: str
    version: str = "0.1.0"
    requirements: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    async def execute(self, runtime: "AgentRuntime", **kwargs) -> Any:
        """Execute the capability within the given runtime context."""
        raise NotImplementedError(f"Capability {self.name} has no implementation")
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate parameters against capability requirements."""
        for name, schema in self.parameters.items():
            if name not in params and "default" not in schema:
                raise ValueError(f"Missing required parameter: {name}")
        return True