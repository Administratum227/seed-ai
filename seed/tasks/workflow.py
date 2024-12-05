"""Workflow management for coordinating multiple tasks.

Provides functionality for creating and managing task workflows with dependencies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
import uuid
from .queue import Task, TaskStatus

@dataclass
class Workflow:
    """Defines a sequence of tasks with dependencies."""
    
    workflow_id: str
    name: str
    tasks: List[Task]
    dependencies: Dict[str, List[str]]  # task_id -> [dependent_task_ids]
    status: TaskStatus = TaskStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, name: str, tasks: List[Task]) -> 'Workflow':
        """Create a new workflow instance."""
        return cls(
            workflow_id=str(uuid.uuid4()),
            name=name,
            tasks=tasks,
            dependencies={},
            status=TaskStatus.PENDING,
            results={}
        )
    
    def add_dependency(self, task_id: str, depends_on: str) -> None:
        """Add a dependency between tasks."""
        if task_id not in self.dependencies:
            self.dependencies[task_id] = []
        self.dependencies[task_id].append(depends_on)