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
