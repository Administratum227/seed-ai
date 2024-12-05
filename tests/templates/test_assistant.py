import pytest
from seed_ai.templates import AssistantTemplate

@pytest.fixture
def valid_config():
    """Provides a baseline valid configuration for testing."""
    return {
        'type': 'assistant',
        'mode': 'standard',
        'security': {
            'sandbox': True,
            'permissions': 'minimal'
        },
        'resources': {
            'max_memory': '512M',
            'max_cpu': 50
        },
        'capabilities': {
            'conversation': True,
            'task_execution': True,
            'file_access': False
        }
    }

def test_template_initialization(valid_config):
    """Test basic template initialization with valid configuration."""
    template = AssistantTemplate(valid_config)
    assert template.config['type'] == 'assistant'
    assert template.config['mode'] == 'standard'
    assert template.metadata['version'] == '1.0.0'

def test_template_validation(valid_config):
    """Test template validation with valid configuration."""
    template = AssistantTemplate(valid_config)
    assert template.validate() is True

def test_invalid_type():
    """Test validation fails with incorrect template type."""
    invalid_config = {
        'type': 'invalid',
        'mode': 'standard',
        'security': {'sandbox': True, 'permissions': 'minimal'},
        'resources': {'max_memory': '512M', 'max_cpu': 50}
    }
    template = AssistantTemplate(invalid_config)
    assert template.validate() is False