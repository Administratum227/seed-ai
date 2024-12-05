from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Conversation:
    """Manages dialogue and response generation for AI agents.
    
    Handles conversation history, message tracking, and response generation
    with configurable constraints and validation.
    """
    
    VALID_ROLES = {'user', 'assistant', 'system'}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            'max_history': 10,
            'max_response_length': 1000,
            'keep_timestamps': True,
            'response_format': 'text'
        }
        self.history: List[Dict[str, Any]] = []
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Initialize conversation-specific logging."""
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.logger.setLevel(logging.INFO)
    
    def add_message(self, message: str, role: str) -> None:
        """Add a validated message to the conversation history.
        
        Args:
            message: The message content
            role: Role of the message sender
            
        Raises:
            ValueError: If message is empty or role is invalid
        """
        # Validate message
        if not message or not message.strip():
            raise ValueError('Message cannot be empty')
            
        # Validate role
        if role not in self.VALID_ROLES:
            raise ValueError(f'Invalid role. Must be one of: {self.VALID_ROLES}')
        
        # Create message entry
        entry = {
            'content': message.strip(),
            'role': role
        }
        
        if self.config['keep_timestamps']:
            entry['timestamp'] = datetime.now().isoformat()
        
        self.history.append(entry)
        
        # Trim history if needed
        if len(self.history) > self.config['max_history']:
            self.history = self.history[-self.config['max_history']:]
            
        self.logger.debug(
            f'Added message from {role} (history size: {len(self.history)})'
        )
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response based on user input and conversation history.
        
        Args:
            user_input: The user's input message
            
        Returns:
            Generated response string
        """
        # Add user input to history
        self.add_message(user_input, 'user')
        
        # Generate response
        response = self._process_input(user_input)
        
        # Validate response length
        if len(response) > self.config['max_response_length']:
            response = response[:self.config['max_response_length']] + '...'
        
        # Add response to history
        self.add_message(response, 'assistant')
        
        return response
    
    def _process_input(self, user_input: str) -> str:
        """Process user input and generate appropriate response.
        
        This is a placeholder method that should be overridden with
        actual NLP/ML processing logic.
        
        Args:
            user_input: The user's input message
            
        Returns:
            Generated response string
        """
        return f'Processed response to: {user_input}'
    
    def get_context(self, message_count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get recent conversation context.
        
        Args:
            message_count: Optional number of recent messages to include
            
        Returns:
            List of recent conversation entries
        """
        if message_count is None:
            return self.history.copy()
        return self.history[-message_count:]
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.history.clear()
        self.logger.info('Conversation history cleared')