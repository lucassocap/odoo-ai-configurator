"""
Audit Agent
Verifies Odoo state against configuration
"""
from typing import Any, Dict, List

from .base import OdooAgent


class AuditAgent(OdooAgent):
    """
    Agent responsible for auditing the Odoo instance state
    against the desired configuration.
    """
    
    def can_handle(self, request: str) -> bool:
        """Check if request is for auditing/verification"""
        keywords = ['audit', 'verify', 'check', 'status', 'validate']
        return any(k in request.lower() for k in keywords)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute audit
        
        Args:
            params: Dict containing:
                - modules: List[str] of expected modules
                - company: Dict of expected company info (optional)
                
        Returns:
            Audit results dictionary
        """
        results = {
            'status': 'success',
            'modules': {},
            'discrepancies': []
        }
        
        # 1. Audit Modules
        if 'modules' in params:
            module_report = self.verify_modules(params['modules'])
            results['modules'] = module_report
            if module_report['missing']:
                results['status'] = 'warning'
                results['discrepancies'].append(f"Missing modules: {', '.join(module_report['missing'])}")
                
                # Record error in memory for other agents to see
                self.record_error(
                    error_type="missing_modules",
                    error_msg=f"Modules missing: {module_report['missing']}",
                    context=str(params)
                )

        # Store this audit in RAG context
        self.store_context(
            action="audit",
            params=params,
            result=str(results),
            context="Project state verification"
        )
        
        return results
    
    def verify_modules(self, expected_modules: List[str]) -> Dict[str, List[str]]:
        """
        Verify if modules are installed
        """
        installed = []
        missing = []
        
        for module in expected_modules:
            # Use search method directly as OdooConnector doesn't have is_module_installed
            domain = [('name', '=', module), ('state', '=', 'installed')]
            # We need to catch potential connection errors here?
            # The base agent has self.odoo
            try:
                ids = self.odoo.search('ir.module.module', domain)
                if ids:
                    installed.append(module)
                else:
                    missing.append(module)
            except Exception as e:
                self.log(f"Error checking module {module}: {e}", "ERROR")
                missing.append(module)
                
        return {
            'installed': installed,
            'missing': missing,
            'total_checked': len(expected_modules)
        }
