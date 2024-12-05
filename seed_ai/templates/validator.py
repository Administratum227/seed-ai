from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class TemplateValidator:
    """Validates agent templates and their configurations.
    
    Ensures templates meet the required structure, security constraints,
    and operational parameters before agent generation.
    """
    
    def __init__(self):
        self.errors: List[str] = []
    
    def validate_template(self, template_config: Dict[str, Any]) -> bool:
        """Validate a template configuration.
        
        Args:
            template_config: Template configuration dictionary
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        self.errors = []
        
        # Validate basic structure
        if not self._validate_structure(template_config):
            return False
            
        # Validate security settings
        if not self._validate_security(template_config.get('security', {})):
            return False
            
        # Validate resource constraints
        if not self._validate_resources(template_config.get('resources', {})):
            return False
            
        return True
    
    def _validate_structure(self, config: Dict[str, Any]) -> bool:
        """Validate the basic template structure.
        
        Args:
            config: Template configuration
            
        Returns:
            bool: True if structure is valid
        """
        required_sections = {'type', 'mode', 'security', 'resources'}
        missing = required_sections - set(config.keys())
        
        if missing:
            self.errors.append(f'Missing required sections: {missing}')
            return False
            
        if not isinstance(config.get('type'), str):
            self.errors.append('Template type must be a string')
            return False
            
        return True
    
    def _validate_security(self, security: Dict[str, Any]) -> bool:
        """Validate security settings.
        
        Args:
            security: Security configuration section
            
        Returns:
            bool: True if security settings are valid
        """
        required_settings = {'sandbox', 'permissions'}
        missing = required_settings - set(security.keys())
        
        if missing:
            self.errors.append(f'Missing security settings: {missing}')
            return False
            
        valid_permissions = {'minimal', 'standard', 'extended'}
        if security.get('permissions') not in valid_permissions:
            self.errors.append(
                f'Invalid permissions level. Must be one of: {valid_permissions}'
            )
            return False
            
        return True
    
    def _validate_resources(self, resources: Dict[str, Any]) -> bool:
        """Validate resource constraints.
        
        Args:
            resources: Resource configuration section
            
        Returns:
            bool: True if resource constraints are valid
        """
        required_limits = {'max_memory', 'max_cpu'}
        missing = required_limits - set(resources.keys())
        
        if missing:
            self.errors.append(f'Missing resource limits: {missing}')
            return False
            
        try:
            memory = str(resources['max_memory']).upper()
            if not any(memory.endswith(unit) for unit in ['M', 'G']):
                self.errors.append('Memory limit must specify M or G units')
                return False
                
            cpu = float(resources['max_cpu'])
            if not 0 < cpu <= 100:
                self.errors.append('CPU limit must be between 0 and 100')
                return False
                
        except (ValueError, TypeError):
            self.errors.append('Invalid resource limit format')
            return False
            
        return True
    
    def get_errors(self) -> List[str]:
        """Get list of validation errors.
        
        Returns:
            List of error messages from last validation
        """
        return self.errors