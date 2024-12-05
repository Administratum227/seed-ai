"""
Pre-flight System for SEED Framework
----------------------------------
Performs essential checks and validations before framework operations.

This module ensures all necessary conditions are met before launching
any SEED components, providing early warning of potential issues.
"""

import os
import sys
import platform
import socket
import psutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PreflightCheck:
    """Comprehensive system validation and environment checking."""
    
    def __init__(self, required_space_mb: int = 500):
        self.required_space_mb = required_space_mb
        self.seed_home = Path.home() / '.seed'
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def run_all_checks(self) -> bool:
        """
        Run all pre-flight checks.
        
        Returns:
            bool: True if all critical checks pass
        """
        checks = [
            self.check_python_environment,
            self.check_system_resources,
            self.check_directory_structure,
            self.check_permissions,
            self.check_network,
            self.check_dependencies
        ]
        
        passed = True
        for check in checks:
            try:
                if not check():
                    passed = False
            except Exception as e:
                self.errors.append(f"Check failed: {str(e)}")
                passed = False
                logger.error(f"Pre-flight check error: {e}")
        
        return passed
    
    def check_python_environment(self) -> bool:
        """Validate Python version and virtual environment."""
        # Check Python version
        if sys.version_info < (3, 9):
            self.errors.append(
                f"Python 3.9+ required, found {platform.python_version()}"
            )
            return False
        
        # Check virtual environment
        if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
            self.warnings.append("Not running in a virtual environment")
        
        return True
    
    def check_system_resources(self) -> bool:
        """Verify system has sufficient resources."""
        # Check disk space
        free_space_mb = psutil.disk_usage(self.seed_home).free // (1024 * 1024)
        if free_space_mb < self.required_space_mb:
            self.errors.append(
                f"Insufficient disk space. Need {self.required_space_mb}MB, "
                f"have {free_space_mb}MB"
            )
            return False
        
        # Check memory
        memory = psutil.virtual_memory()
        if memory.available < 512 * 1024 * 1024:  # 512MB
            self.warnings.append("Low available memory")
        
        # Check CPU
        cpu_count = psutil.cpu_count()
        if cpu_count < 2:
            self.warnings.append("Single CPU core detected")
        
        return True
    
    def check_directory_structure(self) -> bool:
        """Validate SEED directory structure exists."""
        required_dirs = ['config', 'data', 'cache', 'logs', 'agents']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.seed_home / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.errors.append(
                f"Missing directories: {', '.join(missing_dirs)}"
            )
            return False
        
        return True
    
    def check_permissions(self) -> bool:
        """Verify correct permissions on SEED directories."""
        seed_dirs = [self.seed_home, *self.seed_home.glob("*")]
        
        for path in seed_dirs:
            if not os.access(path, os.R_OK | os.W_OK):
                self.errors.append(
                    f"Insufficient permissions for: {path}"
                )
                return False
        
        return True
    
    def check_network(self) -> bool:
        """Validate network connectivity and DNS."""
        # Check basic connectivity
        try:
            # Try to connect to common services
            for host in ['github.com', 'pypi.org']:
                socket.create_connection((host, 443), timeout=5)
        except (socket.timeout, socket.gaierror, ConnectionRefusedError):
            self.errors.append("Network connectivity check failed")
            return False
        
        return True
    
    def check_dependencies(self) -> bool:
        """Verify required system dependencies."""
        try:
            import anthropic
            import yaml
            import rich
            import typer
        except ImportError as e:
            self.errors.append(f"Missing dependency: {e.name}")
            return False
        
        return True
    
    def get_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive status report.
        
        Returns:
            Dictionary containing:
            - System information
            - Check results
            - Errors and warnings
            - Resource metrics
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "python_version": platform.python_version(),
                "os": platform.system(),
                "platform": platform.platform(),
                "cpu_count": psutil.cpu_count(),
                "memory": dict(psutil.virtual_memory()._asdict()),
                "disk": dict(psutil.disk_usage(self.seed_home)._asdict())
            },
            "checks_passed": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings
        }

# Convenience function for quick checks
def run_preflight() -> Tuple[bool, Dict[str, Any]]:
    """
    Run all pre-flight checks and return results.
    
    Returns:
        Tuple containing:
        - Boolean indicating if all critical checks passed
        - Dictionary with detailed report
    """
    checker = PreflightCheck()
    passed = checker.run_all_checks()
    return passed, checker.get_report()