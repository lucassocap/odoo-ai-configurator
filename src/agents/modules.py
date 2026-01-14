"""
Module Management Agent
"""
from typing import Any, Dict, List

from .base import OdooAgent


class ModuleAgent(OdooAgent):
    """Install and configure Odoo modules"""
    
    KEYWORDS = ['module', 'install', 'activate', 'app']
    
    MODULE_MAP = {
        'website': 'website',
        'ecommerce': 'website_sale',
        'shop': 'website_sale',
        'crm': 'crm',
        'sales': 'sale_management',
        'inventory': 'stock',
        'accounting': 'account',
        'invoicing': 'account_invoicing',
        'manufacturing': 'mrp',
        'pos': 'point_of_sale',
        'project': 'project',
        'hr': 'hr',
        'marketing': 'marketing_automation',
    }
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Install modules
        
        Params:
            modules: List of module names or keywords
        """
        modules = params.get('modules', [])
        
        if isinstance(modules, str):
            modules = [modules]
        
        self.log(f"Installing {len(modules)} modules")
        
        installed = []
        failed = []
        
        for module in modules:
            # Map keyword to actual module name
            module_name = self.MODULE_MAP.get(module.lower(), module)
            
            try:
                # Search for module
                module_ids = self.odoo.search(
                    'ir.module.module',
                    [('name', '=', module_name)]
                )
                
                if not module_ids:
                    self.log(f"Module not found: {module_name}", "WARNING")
                    failed.append(module_name)
                    continue
                
                # Install module
                self.odoo.execute(
                    'ir.module.module',
                    'button_immediate_install',
                    module_ids
                )
                
                installed.append(module_name)
                self.log(f"Installed: {module_name}")
                
            except Exception as e:
                self.log(f"Error installing {module_name}: {str(e)}", "ERROR")
                failed.append(module_name)
        
        return {
            'status': 'success' if installed else 'error',
            'installed': installed,
            'failed': failed,
            'total': len(modules)
        }
