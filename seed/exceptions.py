"""Custom exceptions for the SEED framework."""

class SeedError(Exception):
    """Base exception class for all SEED-related errors."""
    pass

class RuntimeError(SeedError):
    """Errors related to the agent runtime environment."""
    pass

class CapabilityError(SeedError):
    """Errors related to capability loading or execution."""
    pass

class StateError(SeedError):
    """Errors related to agent state management."""
    pass
