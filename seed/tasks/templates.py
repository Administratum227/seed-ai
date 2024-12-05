"""Task templates for common operations.

Provides predefined templates for creating tasks and workflows that can be easily
reused and customized for common agent operations.
"""

from typing import Dict, Any, List
from .queue import TaskPriority

class TaskTemplates:
    """Predefined task templates for common operations."""
    
    @staticmethod
    def web_search(query: str, max_results: int = 10) -> Dict[str, Any]:
        """Create a web search task.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Task configuration dictionary
        """
        return {
            "capability": "web_search",
            "parameters": {
                "query": query,
                "max_results": max_results
            },
            "priority": TaskPriority.NORMAL
        }
    
    @staticmethod
    def analyze_text(
        text: str,
        analysis_type: str = "sentiment"
    ) -> Dict[str, Any]:
        """Create a text analysis task.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Task configuration dictionary
        """
        return {
            "capability": "text_analysis",
            "parameters": {
                "text": text,
                "analysis_type": analysis_type
            },
            "priority": TaskPriority.NORMAL
        }
    
    @staticmethod
    def research_workflow(topic: str, depth: int = 2) -> List[Dict[str, Any]]:
        """Create a research workflow template.
        
        Creates a multi-step research workflow that includes:
        1. Web search for initial information gathering
        2. Content extraction from search results
        3. Text analysis and summarization
        4. Optional deeper research based on initial findings
        
        Args:
            topic: Research topic
            depth: Depth of research (1-3)
            
        Returns:
            List of task configurations forming the workflow
        """
        workflow = [
            {
                "capability": "web_search",
                "parameters": {
                    "query": topic,
                    "max_results": 5 * depth
                },
                "priority": "HIGH"
            },
            {
                "capability": "content_extraction",
                "parameters": {
                    "max_length": 1000 * depth
                },
                "dependencies": ["web_search"]
            },
            {
                "capability": "text_analysis",
                "parameters": {
                    "analysis_type": "summary",
                    "max_length": 500 * depth
                },
                "dependencies": ["content_extraction"]
            }
        ]
        
        if depth >= 2:
            workflow.extend([
                {
                    "capability": "topic_extraction",
                    "parameters": {
                        "max_topics": 3
                    },
                    "dependencies": ["text_analysis"]
                },
                {
                    "capability": "web_search",
                    "parameters": {
                        "query_template": "{topic} detailed analysis",
                        "max_results": 3
                    },
                    "dependencies": ["topic_extraction"]
                }
            ])
        
        if depth >= 3:
            workflow.append({
                "capability": "research_synthesis",
                "parameters": {
                    "format": "detailed_report",
                    "include_citations": True
                },
                "dependencies": ["web_search", "text_analysis"]
            })
        
        return workflow
    
    @staticmethod
    def agent_collaboration(
        task: str,
        num_agents: int = 2
    ) -> List[Dict[str, Any]]:
        """Create a collaborative multi-agent workflow.
        
        Sets up a workflow where multiple agents work together on a task,
        sharing information and coordinating their efforts.
        
        Args:
            task: Description of the collaborative task
            num_agents: Number of agents to involve
            
        Returns:
            List of task configurations for the collaborative workflow
        """
        return [
            {
                "capability": "task_decomposition",
                "parameters": {
                    "task": task,
                    "num_subtasks": num_agents
                },
                "priority": "HIGH"
            },
            {
                "capability": "task_assignment",
                "parameters": {
                    "assignment_strategy": "capability_based",
                    "num_agents": num_agents
                },
                "dependencies": ["task_decomposition"]
            },
            {
                "capability": "result_aggregation",
                "parameters": {
                    "aggregation_method": "consensus"
                },
                "dependencies": ["task_assignment"]
            },
            {
                "capability": "quality_check",
                "parameters": {
                    "criteria": ["completeness", "consistency"]
                },
                "dependencies": ["result_aggregation"]
            }
        ]
    
    @staticmethod
    def continuous_learning(
        capability: str,
        training_data: str
    ) -> Dict[str, Any]:
        """Create a learning task for capability improvement.
        
        Args:
            capability: Name of the capability to improve
            training_data: Source or description of training data
            
        Returns:
            Task configuration for continuous learning
        """
        return {
            "capability": "capability_enhancement",
            "parameters": {
                "target_capability": capability,
                "training_data": training_data,
                "learning_method": "incremental",
                "validation_split": 0.2
            },
            "priority": TaskPriority.LOW
        }
