import pytest
from datetime import datetime
from seed_ai.capabilities.conversation import Conversation

@pytest.fixture
def mock_config():
    """Provide a standardized test configuration."""
    return {
        'max_history': 5,
        'max_response_length': 500,
        'keep_timestamps': True,
        'response_format': 'text'
    }

@pytest.fixture
def mock_timestamp():
    """Provide a consistent timestamp for testing."""
    return datetime(2024, 12, 5, 12, 0, 0).isoformat()

@pytest.fixture
def conversation(mock_config):
    """Create a properly configured conversation instance."""
    return Conversation(config=mock_config)