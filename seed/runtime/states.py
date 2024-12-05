"""Agent state management and lifecycle states."""

from enum import Enum

class AgentState(Enum):
    """Possible states of an agent during its lifecycle."""
    
    INITIALIZING = "initializing"
    READY = "ready"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"
    
    def is_active(self) -> bool:
        """Check if the state represents an active agent."""
        return self not in (AgentState.ERROR, AgentState.TERMINATED)
    
    def can_execute(self) -> bool:
        """Check if the agent can execute tasks in this state."""
        return self == AgentState.READY
