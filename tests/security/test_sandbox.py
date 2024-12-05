import pytest
from unittest.mock import patch, MagicMock
from seed_ai.security import Sandbox

@pytest.fixture
def sandbox():
    """Create a sandbox instance with default settings."""
    return Sandbox()

@pytest.fixture
def custom_sandbox():
    """Create a sandbox with custom resource limits."""
    return Sandbox(
        permissions='standard',
        resource_limits={
            'memory': '1G',
            'cpu': 75,
            'fsize': 2048 * 1024,
            'nofile': 128
        }
    )

def test_sandbox_initialization(sandbox):
    """Test basic sandbox initialization."""
    assert sandbox.permissions == 'minimal'
    assert 'memory' in sandbox.resource_limits
    assert 'cpu' in sandbox.resource_limits
    assert not sandbox.enabled

def test_memory_limit_parsing(sandbox):
    """Test memory limit string parsing."""
    assert sandbox._parse_memory_limit('512M') == 512 * 1024 * 1024
    assert sandbox._parse_memory_limit('1G') == 1024 * 1024 * 1024
    
    with pytest.raises(ValueError):
        sandbox._parse_memory_limit('1K')

@patch('resource.setrlimit')
@patch('resource.getrlimit')
def test_sandbox_apply(mock_getrlimit, mock_setrlimit, custom_sandbox):
    """Test applying sandbox restrictions with mocked resource calls."""
    # Mock current resource limits
    mock_getrlimit.return_value = (1000, 1000)
    
    custom_sandbox.apply()
    assert custom_sandbox.enabled
    
    # Verify setrlimit was called with correct values
    mock_setrlimit.assert_called()
    
    custom_sandbox.restore()
    assert not custom_sandbox.enabled

def test_sandbox_context_manager(sandbox):
    """Test sandbox usage as a context manager."""
    assert not sandbox.enabled
    
    with patch('resource.setrlimit'), \
         patch('resource.getrlimit', return_value=(1000, 1000)):
        with sandbox:
            assert sandbox.enabled
            # Perform some operation within sandbox
            pass
        
        assert not sandbox.enabled

def test_input_sanitization(sandbox):
    """Test input sanitization at different permission levels."""
    # Test minimal permissions (most restrictive)
    input_with_commands = 'echo test; rm -rf /'
    sanitized = sandbox.sanitize(input_with_commands)
    assert ';' not in sanitized
    
    # Test with different permission level
    sandbox.permissions = 'standard'
    input_with_spaces = '  test input  '
    assert sandbox.sanitize(input_with_spaces) == 'test input'

@patch('resource.setrlimit')
def test_invalid_permissions(mock_setrlimit):
    """Test sandbox creation with invalid permissions."""
    with pytest.raises(ValueError):
        Sandbox(permissions='invalid_level').apply()