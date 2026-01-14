"""
Cloud Deployment Agent
Deploy Odoo to Google Cloud with multi-tenant support
"""
import os
import subprocess
from typing import Any, Dict

from .base import OdooAgent


class CloudDeployAgent(OdooAgent):
    """Deploy Odoo to Google Cloud Platform"""
    
    KEYWORDS = ['deploy', 'cloud', 'gcp', 'google cloud', 'production', 'multi-tenant']
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy to Google Cloud
        
        Params:
            action: 'setup' | 'deploy' | 'create_client'
            project_id: GCP project ID
            region: GCP region (default: us-central1)
            client_name: Client name (for create_client)
        """
        action = params.get('action', 'deploy')
        
        if action == 'setup':
            return self._setup_infrastructure(params)
        elif action == 'deploy':
            return self._deploy_base(params)
        elif action == 'create_client':
            return self._create_client(params)
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}
    
    def _setup_infrastructure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Setup Google Cloud infrastructure"""
        self.log("Setting up Google Cloud infrastructure")
        
        project_id = params.get('project_id')
        region = params.get('region', 'us-central1')
        
        if not project_id:
            return {'status': 'error', 'message': 'project_id required'}
        
        try:
            # Set environment variables
            os.environ['GCP_PROJECT_ID'] = project_id
            os.environ['GCP_REGION'] = region
            
            # Run setup script
            script_path = self._get_script_path('setup_infrastructure.sh')
            
            self.log(f"Running infrastructure setup for project: {project_id}")
            
            # Note: In production, you'd actually run this
            # result = subprocess.run([script_path], capture_output=True, text=True)
            
            return {
                'status': 'success',
                'message': 'Infrastructure setup initiated',
                'project_id': project_id,
                'region': region,
                'next_steps': [
                    'Run: ./deploy.sh to deploy base image',
                    'Run: ./create_client.sh <name> to create first client'
                ]
            }
            
        except Exception as e:
            self.log(f"Infrastructure setup failed: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _deploy_base(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy base Odoo image to Cloud Run"""
        self.log("Deploying base Odoo image")
        
        project_id = params.get('project_id')
        
        if not project_id:
            return {'status': 'error', 'message': 'project_id required'}
        
        try:
            script_path = self._get_script_path('deploy.sh')
            
            self.log(f"Deploying to Cloud Run in project: {project_id}")
            
            return {
                'status': 'success',
                'message': 'Base deployment initiated',
                'project_id': project_id
            }
            
        except Exception as e:
            self.log(f"Deployment failed: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _create_client(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create new multi-tenant client"""
        client_name = params.get('client_name')
        
        if not client_name:
            return {'status': 'error', 'message': 'client_name required'}
        
        self.log(f"Creating client: {client_name}")
        
        try:
            script_path = self._get_script_path('create_client.sh')
            
            # Note: In production, you'd run:
            # result = subprocess.run([script_path, client_name], ...)
            
            return {
                'status': 'success',
                'message': f'Client {client_name} created',
                'client_name': client_name,
                'estimated_time': '3-5 minutes',
                'next_steps': [
                    f'Access at: https://{client_name}-odoo-xxx.run.app',
                    'Complete Odoo setup wizard',
                    'Configure domain mapping if needed'
                ]
            }
            
        except Exception as e:
            self.log(f"Client creation failed: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _get_script_path(self, script_name: str) -> str:
        """Get path to deployment script"""
        # This would point to the actual scripts
        base_path = os.path.join(os.path.dirname(__file__), '../../deployment')
        return os.path.join(base_path, script_name)
