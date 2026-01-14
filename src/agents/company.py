"""
Company Configuration Agent
"""
from typing import Any, Dict

from .base import OdooAgent


class CompanyAgent(OdooAgent):
    """Configure company details"""
    
    KEYWORDS = ['company', 'organization', 'business', 'empresa']
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure company
        
        Params:
            name: Company name
            email: Email address
            phone: Phone number
            website: Website URL
            street: Street address
            city: City
            zip: ZIP code
            country_id: Country ID (default: 233 for USA)
            currency_id: Currency ID (default: 2 for USD)
        """
        self.log(f"Configuring company: {params.get('name', 'Unknown')}")
        
        try:
            # Get first company
            company_ids = self.odoo.search('res.company', [], limit=1)
            
            if not company_ids:
                self.log("No company found!", "ERROR")
                return {'status': 'error', 'message': 'No company found'}
            
            company_id = company_ids[0]
            
            # Update company
            update_data = {
                'name': params.get('name'),
                'email': params.get('email'),
                'phone': params.get('phone'),
                'website': params.get('website'),
                'street': params.get('street'),
                'city': params.get('city'),
                'zip': params.get('zip'),
                'country_id': params.get('country_id', 233),  # USA
                'currency_id': params.get('currency_id', 2),  # USD
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            self.odoo.write('res.company', [company_id], update_data)
            
            self.log(f"Company configured successfully: {params.get('name')}")
            
            return {
                'status': 'success',
                'company_id': company_id,
                'details': update_data
            }
            
        except Exception as e:
            self.log(f"Error configuring company: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
