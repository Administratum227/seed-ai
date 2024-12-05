from typing import Dict, Any, List, Optional, Callable
import logging
from datetime import datetime
from enum import Enum, auto

class TaskStatus(Enum):
    """Enumeration of possible task states."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

class TaskExecutor:
    """Manages task execution and processing for AI agents.
    
    Handles task queuing, execution, and result management with support
    for asynchronous processing and execution monitoring. Implements
    basic task lifecycle management and error handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            'max_concurrent_tasks': 5,
            'task_timeout': 300,  # 5 minutes
            'retry_attempts': 3
        }
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Initialize task executor logging."""
        self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')
        self.logger.setLevel(logging.INFO)
    
    def register_handler(self, task_type: str, handler: Callable) -> None:
        """Register a handler function for a specific task type.
        
        Args:
            task_type: Type identifier for tasks this handler processes
            handler: Function that implements the task processing
        """
        self.handlers[task_type] = handler
        self.logger.info(f'Registered handler for task type: {task_type}')
    
    def submit_task(self, 
                    task_type: str, 
                    params: Dict[str, Any]) -> str:
        """Submit a new task for execution.
        
        Args:
            task_type: Type of task to execute
            params: Parameters for task execution
            
        Returns:
            Task ID for tracking
            
        Raises:
            ValueError: If task type has no registered handler
        """
        if task_type not in self.handlers:
            raise ValueError(f'No handler registered for task type: {task_type}')
        
        task_id = self._generate_task_id()
        
        self.tasks[task_id] = {
            'type': task_type,
            'params': params,
            'status': TaskStatus.PENDING,
            'submit_time': datetime.now().isoformat(),
            'attempts': 0,
            'result': None,
            'error': None
        }
        
        self.logger.info(f'Submitted task {task_id} of type {task_type}')
        return task_id
    
    def _generate_task_id(self) -> str:
        """Generate a unique task identifier.
        
        Returns:
            Unique task ID string
        """
        import uuid
        return str(uuid.uuid4())
    
    def execute(self, task_id: str) -> Any:
        """Execute a pending task.
        
        Args:
            task_id: ID of task to execute
            
        Returns:
            Task execution result
            
        Raises:
            ValueError: If task ID is invalid
            RuntimeError: If task execution fails
        """
        if task_id not in self.tasks:
            raise ValueError(f'Invalid task ID: {task_id}')
        
        task = self.tasks[task_id]
        if task['status'] != TaskStatus.PENDING:
            return task['result']
        
        try:
            task['status'] = TaskStatus.RUNNING
            handler = self.handlers[task['type']]
            
            # Execute task with retry logic
            while task['attempts'] < self.config['retry_attempts']:
                try:
                    task['attempts'] += 1
                    result = handler(task['params'])
                    
                    task['status'] = TaskStatus.COMPLETED
                    task['result'] = result
                    task['complete_time'] = datetime.now().isoformat()
                    
                    self.logger.info(f'Task {task_id} completed successfully')
                    return result
                    
                except Exception as e:
                    if task['attempts'] >= self.config['retry_attempts']:
                        raise
                    self.logger.warning(
                        f'Task {task_id} attempt {task["attempts"]} failed: {e}'
                    )
            
        except Exception as e:
            task['status'] = TaskStatus.FAILED
            task['error'] = str(e)
            task['complete_time'] = datetime.now().isoformat()
            
            self.logger.error(f'Task {task_id} failed: {e}')
            raise RuntimeError(f'Task execution failed: {e}')
    
    def get_status(self, task_id: str) -> TaskStatus:
        """Get current status of a task.
        
        Args:
            task_id: ID of task to check
            
        Returns:
            Current task status
            
        Raises:
            ValueError: If task ID is invalid
        """
        if task_id not in self.tasks:
            raise ValueError(f'Invalid task ID: {task_id}')
        return self.tasks[task_id]['status']
    
    def cancel_task(self, task_id: str) -> None:
        """Cancel a pending or running task.
        
        Args:
            task_id: ID of task to cancel
            
        Raises:
            ValueError: If task ID is invalid
        """
        if task_id not in self.tasks:
            raise ValueError(f'Invalid task ID: {task_id}')
        
        task = self.tasks[task_id]
        if task['status'] in {TaskStatus.PENDING, TaskStatus.RUNNING}:
            task['status'] = TaskStatus.CANCELLED
            task['complete_time'] = datetime.now().isoformat()
            self.logger.info(f'Task {task_id} cancelled')
    
    def get_results(self, task_id: str) -> Optional[Any]:
        """Get results of a completed task.
        
        Args:
            task_id: ID of task to get results for
            
        Returns:
            Task results if completed, None otherwise
            
        Raises:
            ValueError: If task ID is invalid
        """
        if task_id not in self.tasks:
            raise ValueError(f'Invalid task ID: {task_id}')
        
        task = self.tasks[task_id]
        if task['status'] == TaskStatus.COMPLETED:
            return task['result']
        return None