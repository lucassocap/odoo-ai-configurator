"""
Module Management Agent
"""
from typing import Any, Dict, List

from .base import OdooAgent


class ModuleAgent(OdooAgent):
    """Install and configure Odoo modules"""
    
    KEYWORDS = ['module', 'install', 'activate', 'app']
    
    MODULE_MAP = {
        # Website & eCommerce
        'website': 'website',
        'ecommerce': 'website_sale',
        'shop': 'website_sale',
        'online store': 'website_sale',
        'blog': 'website_blog',
        'forum': 'website_forum',
        'slides': 'website_slides',
        'events': 'website_event',
        'livechat': 'im_livechat',
        
        # Sales & CRM
        'crm': 'crm',
        'sales': 'sale_management',
        'quotations': 'sale_management',
        'subscriptions': 'sale_subscription',
        'rental': 'sale_renting',
        'coupons': 'sale_coupon',
        'loyalty': 'loyalty',
        
        # Inventory & Manufacturing
        'inventory': 'stock',
        'warehouse': 'stock',
        'manufacturing': 'mrp',
        'mrp': 'mrp',
        'plm': 'mrp_plm',
        'quality': 'quality_control',
        'maintenance': 'maintenance',
        'barcode': 'stock_barcode',
        
        # Accounting & Finance
        'accounting': 'account',
        'invoicing': 'account_invoicing',
        'expenses': 'hr_expense',
        'assets': 'account_asset',
        'budget': 'account_budget',
        
        # Point of Sale
        'pos': 'point_of_sale',
        'point of sale': 'point_of_sale',
        'restaurant': 'pos_restaurant',
        
        # Human Resources
        'hr': 'hr',
        'employees': 'hr',
        'recruitment': 'hr_recruitment',
        'appraisals': 'hr_appraisal',
        'attendance': 'hr_attendance',
        'timesheet': 'hr_timesheet',
        'payroll': 'hr_payroll',
        'fleet': 'fleet',
        
        # Project Management
        'project': 'project',
        'tasks': 'project',
        'timesheet': 'hr_timesheet',
        'helpdesk': 'helpdesk',
        
        # Marketing
        'marketing': 'marketing_automation',
        'email marketing': 'mass_mailing',
        'sms marketing': 'mass_mailing_sms',
        'social marketing': 'social_media',
        'surveys': 'survey',
        
        # Productivity
        'calendar': 'calendar',
        'contacts': 'contacts',
        'documents': 'documents',
        'sign': 'sign',
        'approvals': 'approvals',
        'voip': 'voip',
        
        # Services
        'field service': 'industry_fsm',
        'appointments': 'appointment',
        
        # Purchase
        'purchase': 'purchase',
        'purchase agreements': 'purchase_requisition',
        
        # Other
        'iot': 'iot',
        'studio': 'web_studio',
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
