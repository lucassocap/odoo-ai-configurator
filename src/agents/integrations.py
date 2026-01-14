"""
Integration Configuration Agent
"""
from typing import Any, Dict

from .base import OdooAgent


class IntegrationAgent(OdooAgent):
    """Configure external integrations"""
    
    KEYWORDS = ['integration', 'api', 'connect', 'sync', 'marketplace', 'payment', 'shipping']
    
    INTEGRATION_TYPES = {
        'payment': ['stripe', 'paypal', 'square'],
        'shipping': ['ups', 'fedex', 'dhl', 'usps'],
        'marketplace': ['amazon', 'ebay', 'bestbuy'],
        'email': ['gmail', 'outlook', 'sendgrid'],
    }
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure integrations
        
        Params:
            integrations: List of integration configs
                - name: Integration name
                - type: Integration type (payment, shipping, etc.)
                - credentials: Dict of credentials
        """
        integrations = params.get('integrations', [])
        
        if isinstance(integrations, dict):
            integrations = [integrations]
        
        self.log(f"Configuring {len(integrations)} integrations")
        
        configured = []
        failed = []
        
        for integration in integrations:
            name = integration.get('name', '').lower()
            int_type = integration.get('type', '')
            
            try:
                if int_type == 'payment':
                    self._configure_payment(name, integration.get('credentials', {}))
                elif int_type == 'shipping':
                    self._configure_shipping(name, integration.get('credentials', {}))
                elif int_type == 'marketplace':
                    self._configure_marketplace(name, integration.get('credentials', {}))
                
                configured.append(name)
                self.log(f"Configured: {name}")
                
            except Exception as e:
                self.log(f"Error configuring {name}: {str(e)}", "ERROR")
                failed.append(name)
        
        return {
            'status': 'success' if configured else 'error',
            'configured': configured,
            'failed': failed
        }
    
    def _configure_payment(self, name: str, credentials: dict):
        """Configure payment provider"""
        self.log(f"Configuring payment: {name}")
        # Payment provider configuration logic
    
    def _configure_shipping(self, name: str, credentials: dict):
        """Configure shipping carrier"""
        self.log(f"Configuring shipping: {name}")
        # Shipping carrier configuration logic
    
    def _configure_marketplace(self, name: str, credentials: dict):
        """Configure marketplace integration"""
        self.log(f"Configuring marketplace: {name}")
        # Marketplace integration logic
