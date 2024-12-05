from importlib.metadata import version

__version__ = version('seed-ai')

# Initialize package components
from . import core
from . import security
from . import capabilities
from . import templates

__all__ = ['core', 'security', 'capabilities', 'templates']