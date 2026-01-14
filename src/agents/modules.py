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
            
            if self._install_module(module_name):
                installed.append(module_name)
            else:
                failed.append(module_name)
        
        return {
            'status': 'success' if installed else 'error',
            'installed': installed,
            'failed': failed,
            'total': len(modules)
        }
    
    def _install_module(self, module_name: str) -> bool:
        """Install a single module by technical name"""
        try:
            self.log(f"Installing module: {module_name}")
            
            # Method 1: Try to install directly by technical name
            try:
                # Search for module by exact technical name
                module_ids = self.odoo.search(
                    'ir.module.module',
                    [('name', '=', module_name)],
                    limit=1
                )
                
                if module_ids:
                    module_id = module_ids[0]
                    
                    # Check current state
                    module_data = self.odoo.read('ir.module.module', [module_id], ['state'])
                    current_state = module_data[0]['state']
                    
                    if current_state == 'installed':
                        self.log(f"Module {module_name} already installed")
                        return True
                    
                    # Install the module
                    self.odoo.execute(
                        'ir.module.module',
                        'button_immediate_install',
                        [module_id]
                    )
                    
                    self.log(f"Installed: {module_name}")
                    return True
                else:
                    self.log(f"Module not found: {module_name}", "WARNING")
                    return False
                    
            except Exception as e:
                # If direct installation fails, try alternative method
                self.log(f"Direct install failed for {module_name}, trying alternative: {str(e)}", "WARNING")
                
                # Method 2: Try to install via upgrade
                try:
                    # Update module list first
                    self.odoo.execute('ir.module.module', 'update_list')
                    
                    # Search again
                    module_ids = self.odoo.search(
                        'ir.module.module',
                        [('name', '=', module_name)],
                        limit=1
                    )
                    
                    if module_ids:
                        self.odoo.execute(
                            'ir.module.module',
                            'button_immediate_install',
                            module_ids
                        )
                        self.log(f"Installed via alternative method: {module_name}")
                        return True
                    else:
                        self.log(f"Module {module_name} not available in this Odoo version", "ERROR")
                        return False
                        
                except Exception as e2:
                    self.log(f"Alternative install also failed for {module_name}: {str(e2)}", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"Error installing {module_name}: {str(e)}", "ERROR")
            return False
