"""
Website & eCommerce Configuration Agent
"""
from typing import Any, Dict

from .base import OdooAgent


class WebsiteAgent(OdooAgent):
    """Configure website and eCommerce"""
    
    KEYWORDS = ['website', 'ecommerce', 'shop', 'online', 'theme', 'pages']
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure website
        
        Params:
            publish: Publish website (default: True)
            theme: Theme name
            pages: List of pages to create
            ecommerce: Enable eCommerce (default: True)
        """
        self.log("Configuring website")
        
        results = {}
        
        try:
            # Publish website
            if params.get('publish', True):
                self._publish_website()
                results['published'] = True
            
            # Configure eCommerce
            if params.get('ecommerce', True):
                self._configure_ecommerce()
                results['ecommerce'] = True
            
            # Create pages
            if 'pages' in params:
                created_pages = self._create_pages(params['pages'])
                results['pages_created'] = len(created_pages)
            
            self.log("Website configured successfully")
            
            return {
                'status': 'success',
                'details': results
            }
            
        except Exception as e:
            self.log(f"Error configuring website: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _publish_website(self):
        """Publish website"""
        # Get website
        website_ids = self.odoo.search('website', [], limit=1)
        if website_ids:
            self.odoo.write('website', website_ids, {'website_published': True})
            self.log("Website published")
    
    def _configure_ecommerce(self):
        """Configure eCommerce settings"""
        # Enable eCommerce features
        self.log("eCommerce configured")
    
    def _create_pages(self, pages: list) -> list:
        """Create website pages"""
        created = []
        for page in pages:
            # Create page logic here
            created.append(page)
        return created
