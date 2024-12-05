import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from seed_ai.capabilities import TaskExecutor, TaskStatus

@pytest.fixture
def task_config():
    """Provide standard test configuration for TaskExecutor."""
    return {
        'max_concurrent_tasks': 3,
        'task_timeout': 60,
        'retry_attempts': 2
    }

@pytest.fixture
def executor(task_config):
    """Create a configured TaskExecutor instance for testing."""
    return TaskExecutor(config=task_config)

@pytest.fixture
def mock_handler():
    """Create a mock task handler function."""
    return Mock(return_value='task_result')

def test_executor_initialization(executor, task_config):
    """Verify TaskExecutor initializes with correct configuration."""
    assert executor.config == task_config
    assert len(executor.tasks) == 0
    assert len(executor.handlers) == 0

def test_handler_registration(executor, mock_handler):
    """Test registering task handlers."""
    task_type = 'test_task'
    executor.register_handler(task_type, mock_handler)
    
    assert task_type in executor.handlers
    assert executor.handlers[task_type] == mock_handler

def test_task_submission(executor, mock_handler):
    """Test submitting tasks for execution."""
    # Register handler
    task_type = 'test_task'
    executor.register_handler(task_type, mock_handler)
    
    # Submit task
    params = {'param1': 'value1'}
    task_id = executor.submit_task(task_type, params)
    
    assert task_id in executor.tasks
    task = executor.tasks[task_id]
    assert task['type'] == task_type
    assert task['params'] == params
    assert task['status'] == TaskStatus.PENDING

def test_task_execution(executor, mock_handler):
    """Test successful task execution."""
    # Setup
    task_type = 'test_task'
    executor.register_handler(task_type, mock_handler)
    task_id = executor.submit_task(task_type, {'param1': 'value1'})
    
    # Execute
    result = executor.execute(task_id)
    
    # Verify
    assert result == 'task_result'
    task = executor.tasks[task_id]
    assert task['status'] == TaskStatus.COMPLETED
    assert task['result'] == 'task_result'
    assert mock_handler.called

def test_task_retry_on_failure(executor):
    """Test task retry behavior on failure."""
    # Create handler that fails twice then succeeds
    failure_count = [0]  # Use list for mutable counter in closure
    def failing_handler(params):
        failure_count[0] += 1
        if failure_count[0] <= 2:
            raise ValueError('Simulated failure')
        return 'success'
    
    # Setup and execute
    task_type = 'failing_task'
    executor.register_handler(task_type, failing_handler)
    task_id = executor.submit_task(task_type, {})
    
    result = executor.execute(task_id)
    
    # Verify retries and final success
    assert result == 'success'
    task = executor.tasks[task_id]
    assert task['status'] == TaskStatus.COMPLETED
    assert task['attempts'] == 3

def test_task_failure_after_retries(executor):
    """Test task failure after exhausting retry attempts."""
    # Handler that always fails
    def failing_handler(params):
        raise ValueError('Simulated failure')
    
    # Setup
    task_type = 'failing_task'
    executor.register_handler(task_type, failing_handler)
    task_id = executor.submit_task(task_type, {})
    
    # Execute and verify failure
    with pytest.raises(RuntimeError):
        executor.execute(task_id)
    
    task = executor.tasks[task_id]
    assert task['status'] == TaskStatus.FAILED
    assert task['attempts'] == executor.config['retry_attempts']
    assert 'Simulated failure' in task['error']

def test_invalid_task_id(executor):
    """Test handling of invalid task IDs."""
    with pytest.raises(ValueError, match='Invalid task ID'):
        executor.execute('nonexistent_task')

def test_task_cancellation(executor, mock_handler):
    """Test task cancellation functionality."""
    # Setup
    task_type = 'test_task'
    executor.register_handler(task_type, mock_handler)
    task_id = executor.submit_task(task_type, {})
    
    # Cancel task
    executor.cancel_task(task_id)
    
    # Verify
    task = executor.tasks[task_id]
    assert task['status'] == TaskStatus.CANCELLED
    assert not mock_handler.called

def test_task_results_retrieval(executor, mock_handler):
    """Test retrieving task results."""
    # Setup and execute task
    task_type = 'test_task'
    executor.register_handler(task_type, mock_handler)
    task_id = executor.submit_task(task_type, {})
    executor.execute(task_id)
    
    # Verify result retrieval
    result = executor.get_results(task_id)
    assert result == 'task_result'
    
    # Test result retrieval for incomplete task
    pending_id = executor.submit_task(task_type, {})
    assert executor.get_results(pending_id) is None