from typing import Dict, Type, Optional
from pathlib import Path
import importlib.util
import logging

from .base import AgentTemplate

logger = logging.getLogger(__name__)

class TemplateLoader:
    """Handles dynamic loading and management of agent templates.
    
    Provides functionality to load templates from the filesystem,
    validate their structure, and maintain a registry of available templates.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = Path(template_dir or '~/.seed/templates').expanduser()
        self.templates: Dict[str, Type[AgentTemplate]] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all template modules from the template directory."""
        if not self.template_dir.exists():
            logger.warning(f'Template directory not found: {self.template_dir}')
            return
        
        for template_file in self.template_dir.glob('*.py'):
            if template_file.name.startswith('_'):
                continue
                
            try:
                spec = importlib.util.spec_from_file_location(
                    template_file.stem,
                    template_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find template class in module
                    for item in dir(module):
                        obj = getattr(module, item)
                        if (isinstance(obj, type) and 
                            issubclass(obj, AgentTemplate) and
                            obj != AgentTemplate):
                            self.templates[template_file.stem] = obj
                            
            except Exception as e:
                logger.error(f'Failed to load template {template_file}: {e}')
    
    def get_template(self, template_name: str) -> Optional[Type[AgentTemplate]]:
        """Get a template class by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            Template class if found, None otherwise
        """
        return self.templates.get(template_name)
    
    def list_templates(self) -> Dict[str, Dict]:
        """List all available templates and their metadata.
        
        Returns:
            Dictionary mapping template names to their metadata
        """
        return {
            name: template().metadata 
            for name, template in self.templates.items()
        }