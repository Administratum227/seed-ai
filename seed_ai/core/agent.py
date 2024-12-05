from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class Agent(ABC):
    """Base class for all AI agents in the SEED framework.
    
    Provides core functionality and interface requirements for agent
    implementations. All specific agent types should inherit from this class.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.state: Dict[str, Any] = {}
        self._initialize_logging()
    
    def _initialize_logging(self) -> None:
        """Set up agent-specific logging configuration."""
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.logger.setLevel(self.config.get('logging', {}).get('level', 'INFO'))
    
    @abstractmethod
    def process_input(self, user_input: str) -> str:
        """Process user input and generate appropriate response.
        
        Args:
            user_input: The input string from the user
            
        Returns:
            The agent's response as a string
        """
        pass
    
    def save_state(self) -> Dict[str, Any]:
        """Save current agent state for persistence.
        
        Returns:
            Dictionary containing agent state data
        """
        return self.state.copy()
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """Load previously saved agent state.
        
        Args:
            state: Dictionary containing agent state data
        """
        self.state.update(state)
    
    def reset(self) -> None:
        """Reset agent to initial state."""
        self.state.clear()
        self.logger.info('Agent state reset')
