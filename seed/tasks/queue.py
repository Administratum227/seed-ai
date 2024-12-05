"""Task queue implementation for SEED.

Provides a priority-based task queue with persistence and status tracking.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
import uuid
import heapq

class TaskPriority(Enum):
    """Task execution priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class TaskStatus(Enum):
    """Possible states of a task during its lifecycle."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass(order=True)
class Task:
    """Represents a single unit of work to be executed by an agent."""
    
    priority: TaskPriority
    created_at: datetime
    task_id: str = field(compare=False)
    capability: str = field(compare=False)
    parameters: Dict[str, Any] = field(compare=False, default_factory=dict)
    status: TaskStatus = field(compare=False, default=TaskStatus.PENDING)
    result: Optional[Any] = field(compare=False, default=None)
    error: Optional[str] = field(compare=False, default=None)
    
    @classmethod
    def create(cls, capability: str, parameters: Dict[str, Any],
              priority: TaskPriority = TaskPriority.NORMAL) -> 'Task':
        """Create a new task instance."""
        return cls(
            task_id=str(uuid.uuid4()),
            capability=capability,
            parameters=parameters,
            priority=priority,
            created_at=datetime.now()
        )

class TaskQueue:
    """Priority queue for managing tasks."""
    
    def __init__(self):
        self._queue = []
        self._task_map = {}
        self._lock = asyncio.Lock()
    
    async def push(self, task: Task) -> None:
        """Add a task to the queue."""
        async with self._lock:
            heapq.heappush(self._queue, task)
            self._task_map[task.task_id] = task
    
    async def pop(self) -> Optional[Task]:
        """Get the highest priority task."""
        async with self._lock:
            if not self._queue:
                return None
            task = heapq.heappop(self._queue)
            return task