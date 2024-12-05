"""Runtime Environment Management

Manages the core runtime environment for SEED, handling:
- System resource management
- Environment initialization
- Component lifecycle
- Error handling and recovery
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import asyncio

from .config import Config
from .events import EventBus, Event
from .exceptions import SeedError

class Runtime:
    """Core runtime environment for SEED framework.
    
    Handles initialization, resource management, and component lifecycle.
    Provides a centralized system for managing the framework's operation.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the runtime environment.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config = Config(config_path)
        self.event_bus = EventBus()
        self.logger = logging.getLogger("seed.runtime")
        self._components: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the runtime environment.
        
        Sets up logging, creates necessary directories, and starts core services.
        """
        if self._initialized:
            return
            
        try:
            # Configure logging
            self._setup_logging()
            
            # Create directory structure
            self._create_directories()
            
            # Initialize components
            await self._init_components()
            
            self._initialized = True
            self.logger.info("Runtime initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Runtime initialization failed: {e}")
            raise SeedError(f"Initialization failed: {str(e)}")
    
    def _setup_logging(self) -> None:
        """Configure logging system."""
        log_path = Path(self.config.get("runtime.log_path")).expanduser()
        log_path.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=self.config.get("runtime.log_level", "INFO"),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_path / "seed.log")
            ]
        )
    
    def _create_directories(self) -> None:
        """Create required directory structure."""
        dirs = [
            self.config.get("runtime.storage_path"),
            self.config.get("runtime.cache_path"),
            self.config.get("runtime.log_path")
        ]
        
        for dir_path in dirs:
            Path(dir_path).expanduser().mkdir(parents=True, exist_ok=True)
    
    async def _init_components(self) -> None:
        """Initialize framework components."""
        # Add initialization of core components here
        pass
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the runtime environment."""
        if not self._initialized:
            return
            
        try:
            # Shutdown components in reverse dependency order
            for component in reversed(self._components.values()):
                if hasattr(component, 'shutdown'):
                    await component.shutdown()
            
            self._initialized = False
            self.logger.info("Runtime shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise SeedError(f"Shutdown failed: {str(e)}")
    
    def register_component(self, name: str, component: Any) -> None:
        """Register a component with the runtime.
        
        Args:
            name: Unique identifier for the component
            component: Component instance to register
        """
        if name in self._components:
            raise SeedError(f"Component {name} already registered")
        
        self._components[name] = component
        self.logger.debug(f"Registered component: {name}")
    
    def get_component(self, name: str) -> Any:
        """Get a registered component by name.
        
        Args:
            name: Component identifier
            
        Returns:
            The requested component
            
        Raises:
            SeedError: If component not found
        """
        if name not in self._components:
            raise SeedError(f"Component {name} not found")
        return self._components[name]
