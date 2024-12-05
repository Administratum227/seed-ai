from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import yaml

class AgentTemplate(ABC):
    """Base class for all agent templates.
    
    Provides the foundational structure and validation for AI agent templates.
    Each template defines the core capabilities and constraints of an agent type.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = self._validate_config(config)
        self.metadata = self._load_metadata()
    
    @abstractmethod
    def generate(self) -> Dict[str, Any]:
        """Generate the agent configuration and initialization code.
        
        Returns:
            Dict containing the generated agent code and configuration.
        """
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate the template configuration and requirements.
        
        Returns:
            bool: True if validation passes, False otherwise.
        """
        pass
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and process the template configuration.
        
        Args:
            config: Raw configuration dictionary
            
        Returns:
            Processed and validated configuration
        """
        required_fields = {'type', 'mode', 'security'}
        if not all(field in config for field in required_fields):
            raise ValueError(f'Missing required fields: {required_fields - set(config.keys())}')
        return config
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load template metadata including version, capabilities, and requirements.
        
        Returns:
            Dictionary containing template metadata
        """
        return {
            'version': self.config.get('version', '1.0.0'),
            'capabilities': self.config.get('capabilities', []),
            'requirements': self.config.get('requirements', {})
        }
    
    def export_config(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Export the template configuration to a file or return as dictionary.
        
        Args:
            path: Optional path to save configuration file
            
        Returns:
            Configuration dictionary
        """
        config = {
            'template': self.metadata,
            'configuration': self.config
        }
        
        if path:
            with open(path, 'w') as f:
                yaml.safe_dump(config, f)
        
        return config