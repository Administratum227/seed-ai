import pytest
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables and configurations."""
    os.environ['SEED_ENV'] = 'test'
    os.environ['SEED_CONFIG_PATH'] = os.path.join(os.path.dirname(__file__), 'test_config.yaml')
    
    yield
    
    # Cleanup after tests
    if 'SEED_ENV' in os.environ:
        del os.environ['SEED_ENV']
    if 'SEED_CONFIG_PATH' in os.environ:
        del os.environ['SEED_CONFIG_PATH']