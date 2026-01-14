"""
Base Agent Class
All configuration agents inherit from this
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..connectors.odoo import OdooConnector


class OdooAgent(ABC):
    """Base class for all Odoo configuration agents"""
    
    def __init__(self, connector: OdooConnector):
        self.odoo = connector
        self.name = self.__class__.__name__
        
        # Initialize memory systems
        try:
            from ..memory import LessonsLearned, RAGMemory
            self.lessons = LessonsLearned()
            self.rag = RAGMemory()
            self.memory_enabled = True
        except Exception as e:
            print(f"Warning: Memory systems not available: {e}")
            self.lessons = None
            self.rag = None
            self.memory_enabled = False
        
    @abstractmethod
    def can_handle(self, request: str) -> bool:
        """
        Check if this agent can handle the request
        
        Args:
            request: Natural language configuration request
            
        Returns:
            True if agent can handle this request
        """
        pass
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the configuration
        
        Args:
            params: Configuration parameters
            
        Returns:
            Result dictionary with status and details
        """
        pass
    
    def verify(self) -> bool:
        """
        Verify configuration was successful
        
        Returns:
            True if verification passed
        """
        return True
    
    def rollback(self):
        """Rollback changes if something failed"""
        pass
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        print(f"[{self.name}] {level}: {message}")
    
    # Memory system methods
    
    def record_error(self, error_type: str, error_msg: str, context: str):
        """Record an error in lessons learned"""
        if self.memory_enabled and self.lessons:
            try:
                self.lessons.record_error(
                    agent_name=self.name,
                    error_type=error_type,
                    error_msg=error_msg,
                    context=context
                )
            except Exception as e:
                self.log(f"Failed to record error: {e}", "WARNING")
    
    def record_solution(self, error_type: str, solution: str, context: str = None):
        """Record a successful solution"""
        if self.memory_enabled and self.lessons:
            try:
                self.lessons.record_solution(
                    agent_name=self.name,
                    error_type=error_type,
                    solution=solution,
                    context=context
                )
            except Exception as e:
                self.log(f"Failed to record solution: {e}", "WARNING")
    
    def get_known_solutions(self, error_type: str):
        """Get known solutions for an error type"""
        if self.memory_enabled and self.lessons:
            try:
                return self.lessons.get_solutions(
                    agent_name=self.name,
                    error_type=error_type
                )
            except Exception as e:
                self.log(f"Failed to get solutions: {e}", "WARNING")
        return []
    
    def store_context(self, action: str, params: Dict, result: str, context: str):
        """Store action context in RAG"""
        if self.memory_enabled and self.rag and self.rag.enabled:
            try:
                self.rag.store(
                    action=action,
                    params=params,
                    result=result,
                    context=context,
                    agent_name=self.name
                )
            except Exception as e:
                self.log(f"Failed to store context: {e}", "WARNING")
    
    def search_context(self, query: str, n_results: int = 5):
        """Search for relevant context"""
        if self.memory_enabled and self.rag and self.rag.enabled:
            try:
                return self.rag.search(
                    query=query,
                    n_results=n_results,
                    agent_name=self.name
                )
            except Exception as e:
                self.log(f"Failed to search context: {e}", "WARNING")
        return []
