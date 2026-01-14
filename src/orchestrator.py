"""
AI Orchestrator
Coordinates agents to fulfill configuration requests
"""
from typing import Any, Dict, List

from .agents.automation import AutomationAgent
from .agents.cloud_deploy import CloudDeployAgent
from .agents.company import CompanyAgent
from .agents.image_generator import ImageGeneratorAgent
from .agents.integrations import IntegrationAgent
from .agents.modules import ModuleAgent
from .agents.products import ProductAgent
from .agents.users import UserAgent
from .agents.website import WebsiteAgent
from .agents.website_config import WebsiteConfigAgent
from .connectors.odoo import OdooConnector


class Orchestrator:
    """Main orchestrator for AI-driven Odoo configuration"""
    
    def __init__(self, url: str, db: str = 'odoo', username: str = 'admin', password: str = 'admin'):
        self.connector = OdooConnector(url, db, username, password)
        self.agents = []
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all available agents"""
        if not self.connector.connect():
            raise RuntimeError("Failed to connect to Odoo")
        
        self.agents = [
            CompanyAgent(self.connector),
            ModuleAgent(self.connector),
            ProductAgent(self.connector),
            WebsiteAgent(self.connector),
            WebsiteConfigAgent(self.connector),
            IntegrationAgent(self.connector),
            AutomationAgent(self.connector),
            UserAgent(self.connector),
            CloudDeployAgent(self.connector),
            ImageGeneratorAgent(self.connector),
        ]
    
    def configure(self, request: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Configure Odoo based on natural language request
        
        Args:
            request: Natural language configuration request
            params: Optional parameters
            
        Returns:
            Configuration results
        """
        print(f"🤖 Processing request: {request}\n")
        
        # Find capable agents
        capable_agents = [agent for agent in self.agents if agent.can_handle(request)]
        
        if not capable_agents:
            return {
                'status': 'error',
                'message': 'No agent found to handle this request'
            }
        
        results = []
        
        for agent in capable_agents:
            print(f"📋 Executing {agent.name}...")
            result = agent.execute(params or {})
            results.append({
                'agent': agent.name,
                'result': result
            })
        
        return {
            'status': 'success',
            'agents_executed': len(results),
            'results': results
        }
    
    def configure_from_dict(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure from dictionary
        
        Args:
            config: Configuration dictionary with sections
            
        Returns:
            Configuration results
        """
        results = []
        
        # Company configuration
        if 'company' in config:
            agent = CompanyAgent(self.connector)
            result = agent.execute(config['company'])
            results.append({'section': 'company', 'result': result})
        
        # Modules
        if 'modules' in config:
            agent = ModuleAgent(self.connector)
            result = agent.execute({'modules': config['modules']})
            results.append({'section': 'modules', 'result': result})
        
        # Products
        if 'products' in config:
            agent = ProductAgent(self.connector)
            result = agent.execute(config['products'])
            results.append({'section': 'products', 'result': result})
        
        return {
            'status': 'success',
            'sections': len(results),
            'results': results
        }
