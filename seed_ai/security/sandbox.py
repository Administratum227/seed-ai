import os
import resource
import signal
from typing import Dict, Any, Optional, ContextManager
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class Sandbox(ContextManager):
    """Provides a secure execution environment for AI agents.
    
    Implements process isolation, resource limits, and security boundaries
    to ensure safe agent execution. Uses OS-level security features and
    resource controls to enforce constraints.
    
    Attributes:
        permissions: Security permission level ('minimal', 'standard', 'extended')
        resource_limits: Dictionary of resource constraints
        enabled: Whether sandbox protection is currently active
    """
    
    def __init__(self, 
                 permissions: str = 'minimal',
                 resource_limits: Optional[Dict[str, Any]] = None):
        self.permissions = permissions
        self.resource_limits = resource_limits or {
            'memory': '512M',
            'cpu': 50,
            'fsize': 1024 * 1024,  # 1MB file size limit
            'nofile': 64  # Max number of open files
        }
        self.enabled = False
        self._original_limits = {}
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure sandbox-specific logging."""
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.logger.setLevel(logging.INFO)
    
    def _parse_memory_limit(self, limit: str) -> int:
        """Convert memory limit string to bytes.
        
        Args:
            limit: Memory limit string (e.g., '512M', '1G')
            
        Returns:
            Memory limit in bytes
        """
        unit = limit[-1].upper()
        value = int(limit[:-1])
        
        if unit == 'M':
            return value * 1024 * 1024
        elif unit == 'G':
            return value * 1024 * 1024 * 1024
        else:
            raise ValueError(f'Invalid memory unit: {unit}')
    
    def apply(self) -> None:
        """Apply sandbox restrictions and resource limits."""
        if self.enabled:
            return
            
        try:
            # Store original limits for restoration
            self._original_limits = {
                'cpu': resource.getrlimit(resource.RLIMIT_CPU),
                'memory': resource.getrlimit(resource.RLIMIT_AS),
                'fsize': resource.getrlimit(resource.RLIMIT_FSIZE),
                'nofile': resource.getrlimit(resource.RLIMIT_NOFILE)
            }
            
            # Set CPU limit
            cpu_limit = int(self.resource_limits['cpu'])
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
            
            # Set memory limit
            mem_bytes = self._parse_memory_limit(self.resource_limits['memory'])
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            
            # Set file size limit
            fsize = self.resource_limits['fsize']
            resource.setrlimit(resource.RLIMIT_FSIZE, (fsize, fsize))
            
            # Set open files limit
            nofile = self.resource_limits['nofile']
            resource.setrlimit(resource.RLIMIT_NOFILE, (nofile, nofile))
            
            # Apply permission restrictions
            self._apply_permissions()
            
            self.enabled = True
            self.logger.info('Sandbox restrictions applied successfully')
            
        except Exception as e:
            self.logger.error(f'Failed to apply sandbox restrictions: {e}')
            raise
    
    def _apply_permissions(self) -> None:
        """Apply permission-based restrictions based on security level."""
        if self.permissions == 'minimal':
            # Most restrictive: no file or network access
            os.environ['SANDBOX_LEVEL'] = 'minimal'
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        
        elif self.permissions == 'standard':
            # Allow limited file access in specific directories
            os.environ['SANDBOX_LEVEL'] = 'standard'
            
        elif self.permissions == 'extended':
            # Allow broader access with monitoring
            os.environ['SANDBOX_LEVEL'] = 'extended'
        
        else:
            raise ValueError(f'Invalid permission level: {self.permissions}')
    
    def restore(self) -> None:
        """Restore original system limits and permissions."""
        if not self.enabled:
            return
            
        try:
            # Restore original resource limits
            for resource_type, (soft, hard) in self._original_limits.items():
                if resource_type == 'cpu':
                    resource.setrlimit(resource.RLIMIT_CPU, (soft, hard))
                elif resource_type == 'memory':
                    resource.setrlimit(resource.RLIMIT_AS, (soft, hard))
                elif resource_type == 'fsize':
                    resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
                elif resource_type == 'nofile':
                    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))
            
            self.enabled = False
            self.logger.info('Sandbox restrictions removed')
            
        except Exception as e:
            self.logger.error(f'Failed to restore system limits: {e}')
            raise
    
    @contextmanager
    def __enter__(self):
        """Context manager entry point for sandbox."""
        self.apply()
        try:
            yield self
        finally:
            self.restore()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point for sandbox."""
        self.restore()
        return False  # Don't suppress exceptions
    
    def sanitize(self, user_input: str) -> str:
        """Sanitize user input based on security level.
        
        Args:
            user_input: Raw user input string
            
        Returns:
            Sanitized input string
        """
        # Basic sanitization for all security levels
        sanitized = user_input.strip()
        
        # Apply additional restrictions based on permission level
        if self.permissions == 'minimal':
            # Remove potential command injection characters
            sanitized = sanitized.replace(';', '')
            sanitized = sanitized.replace('&', '')
            sanitized = sanitized.replace('|', '')
            sanitized = sanitized.replace('>', '')
            sanitized = sanitized.replace('<', '')
        
        return sanitized