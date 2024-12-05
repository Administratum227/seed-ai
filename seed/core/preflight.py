"""SEED Preflight System

Provides comprehensive system checks and validation for the SEED framework.
Ensures all requirements are met before launching components.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Tuple, List
import logging
from importlib import import_module

def run_checks() -> Tuple[bool, Dict[str, Any]]:
    """Run all pre-flight checks.
    
    Returns:
        Tuple containing:
        - Boolean indicating if all critical checks passed
        - Dictionary with detailed report
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        errors.append(
            f"Python 3.9+ required, found {platform.python_version()}"
        )
    
    # Check required packages
    required_packages = [
        "textual",
        "rich",
        "typer",
        "yaml"
    ]
    
    for package in required_packages:
        try:
            import_module(package)
        except ImportError:
            errors.append(f"Required package not found: {package}")
    
    # Check directory structure
    seed_home = Path.home() / ".seed"
    required_dirs = [
        "config",
        "data",
        "cache",
        "logs",
        "agents"
    ]
    
    for dir_name in required_dirs:
        dir_path = seed_home / dir_name
        if not dir_path.exists():
            errors.append(f"Required directory missing: {dir_name}")
        elif not dir_path.is_dir():
            errors.append(f"Path exists but is not a directory: {dir_name}")
        elif not os.access(dir_path, os.W_OK):
            warnings.append(f"Directory not writable: {dir_name}")
    
    # Prepare report
    report = {
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "architecture": platform.machine()
        },
        "errors": errors,
        "warnings": warnings
    }
    
    return len(errors) == 0, report