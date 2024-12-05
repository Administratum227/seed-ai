"""Runtime configuration management."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

@dataclass
class RuntimeConfig:
    """Configuration for the agent runtime environment.
    
    Attributes:
        max_concurrent_tasks: Maximum number of tasks that can run simultaneously
        task_timeout_seconds: Default timeout for task execution
        state_save_interval: Interval between state persistence in seconds
        capability_cache_size: Maximum number of capabilities to cache
        log_level: Logging level for runtime operations
        state_dir: Directory for persisting agent states
        capability_paths: List of paths to search for capability plugins
        resource_limits: Resource usage limits for the agent
    """
    
    max_concurrent_tasks: int = 5
    task_timeout_seconds: float = 30.0
    state_save_interval: float = 60.0
    capability_cache_size: int = 100
    log_level: str = "INFO"
    state_dir: Path = field(default_factory=lambda: Path.home() / ".seed" / "states")
    capability_paths: list[Path] = field(default_factory=list)
    resource_limits: Dict[str, Any] = field(default_factory=lambda: {
        "memory_mb": 1024,
        "cpu_percent": 50,
        "disk_mb": 100
    })
    
    def __post_init__(self):
        """Validate and prepare configuration after initialization."""
        # Convert string paths to Path objects
        if isinstance(self.state_dir, str):
            self.state_dir = Path(self.state_dir)
        
        self.capability_paths = [
            Path(p) if isinstance(p, str) else p
            for p in self.capability_paths
        ]
        
        # Ensure required directories exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
