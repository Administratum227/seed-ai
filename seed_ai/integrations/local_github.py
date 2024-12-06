import os
import json
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from datetime import datetime, timedelta

class LocalGitHubIntegration:
    """Manages secure local file access and GitHub integration.
    
    Provides authenticated access to local files and GitHub repositories
    with proper credential management and access controls.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser('~/.seed/config/github.json')
        self.credentials: Dict[str, Any] = {}
        self.session_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self._setup_logging()
        self._load_config()
    
    def _setup_logging(self) -> None:
        """Initialize secure logging configuration."""
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.logger.setLevel(logging.INFO)
    
    def _load_config(self) -> None:
        """Load GitHub configuration and credentials."""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.credentials = json.load(f)
            except Exception as e:
                self.logger.error(f'Failed to load config: {e}')
                raise
    
    def authenticate(self) -> bool:
        """Perform GitHub authentication using local credentials.
        
        Returns:
            bool: True if authentication successful
        """
        if self.is_authenticated():
            return True
            
        try:
            # Check for existing GitHub CLI auth
            result = subprocess.run(
                ['gh', 'auth', 'status'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.session_token = self._extract_token(result.stdout)
                self.token_expiry = datetime.now() + timedelta(hours=1)
                return True
            
            # Attempt authentication
            result = subprocess.run(
                ['gh', 'auth', 'login', '--web'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.session_token = self._extract_token(result.stdout)
                self.token_expiry = datetime.now() + timedelta(hours=1)
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f'Authentication failed: {e}')
            return False
    
    def _extract_token(self, auth_output: str) -> str:
        """Extract authentication token from GitHub CLI output.
        
        Args:
            auth_output: Output from GitHub CLI auth command
            
        Returns:
            Extracted authentication token
        """
        # Implementation will depend on GitHub CLI output format
        # This is a placeholder for the actual token extraction logic
        return 'placeholder_token'
    
    def is_authenticated(self) -> bool:
        """Check if current session is authenticated and valid.
        
        Returns:
            bool: True if session is valid
        """
        if not self.session_token or not self.token_expiry:
            return False
            
        return datetime.now() < self.token_expiry
    
    def get_local_files(self, path: str) -> List[Dict[str, Any]]:
        """Get information about local files with access control.
        
        Args:
            path: Local directory path to scan
            
        Returns:
            List of file information dictionaries
        
        Raises:
            PermissionError: If access is denied
        """
        if not self.is_authenticated():
            raise PermissionError('Authentication required')
            
        try:
            base_path = Path(path).resolve()
            files = []
            
            for item in base_path.iterdir():
                if self._is_accessible(item):
                    files.append({
                        'name': item.name,
                        'path': str(item),
                        'type': 'dir' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None,
                        'modified': datetime.fromtimestamp(
                            item.stat().st_mtime
                        ).isoformat()
                    })
            
            return files
            
        except Exception as e:
            self.logger.error(f'Failed to scan directory {path}: {e}')
            raise
    
    def _is_accessible(self, path: Path) -> bool:
        """Check if a file or directory is accessible.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is accessible
        """
        try:
            # Check basic access permissions
            return os.access(path, os.R_OK)
        except Exception:
            return False
    
    def read_file(self, path: str) -> str:
        """Read contents of a local file with access control.
        
        Args:
            path: Path to file
            
        Returns:
            File contents as string
            
        Raises:
            PermissionError: If access is denied
            FileNotFoundError: If file doesn't exist
        """
        if not self.is_authenticated():
            raise PermissionError('Authentication required')
            
        file_path = Path(path).resolve()
        
        if not self._is_accessible(file_path):
            raise PermissionError(f'Access denied to {path}')
            
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f'Failed to read file {path}: {e}')
            raise