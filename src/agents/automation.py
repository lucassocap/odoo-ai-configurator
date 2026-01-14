"""
Automation Configuration Agent
"""
from typing import Any, Dict

from .base import OdooAgent


class AutomationAgent(OdooAgent):
    """Configure automated actions and workflows"""
    
    KEYWORDS = ['automation', 'workflow', 'action', 'trigger', 'cron', 'scheduled']
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure automations
        
        Params:
            automations: List of automation configs
                - name: Automation name
                - trigger: Trigger type (on_create, on_write, scheduled)
                - model: Model name
                - action: Action to perform
        """
        automations = params.get('automations', [])
        
        if isinstance(automations, dict):
            automations = [automations]
        
        self.log(f"Configuring {len(automations)} automations")
        
        created = []
        failed = []
        
        for automation in automations:
            try:
                auto_id = self._create_automation(automation)
                created.append(auto_id)
                self.log(f"Created automation: {automation.get('name')}")
                
            except Exception as e:
                self.log(f"Error creating automation: {str(e)}", "ERROR")
                failed.append(automation.get('name'))
        
        return {
            'status': 'success' if created else 'error',
            'created': len(created),
            'failed': len(failed)
        }
    
    def _create_automation(self, config: dict) -> int:
        """Create automated action"""
        # Get model ID
        model_ids = self.odoo.search('ir.model', [('model', '=', config.get('model'))])
        
        if not model_ids:
            raise ValueError(f"Model not found: {config.get('model')}")
        
        automation_data = {
            'name': config.get('name'),
            'model_id': model_ids[0],
            'trigger': config.get('trigger', 'on_create'),
            'state': 'code',
            'code': config.get('action', '# Add action code here'),
        }
        
        return self.odoo.create('base.automation', automation_data)
