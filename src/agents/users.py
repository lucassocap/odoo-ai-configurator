"""
User Management Agent
"""
from typing import Any, Dict

from .base import OdooAgent


class UserAgent(OdooAgent):
    """Manage users and permissions"""
    
    KEYWORDS = ['user', 'permission', 'access', 'role', 'group']
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage users
        
        Params:
            users: List of user configs
                - name: User name
                - login: Login email
                - groups: List of group names
        """
        users = params.get('users', [])
        
        if isinstance(users, dict):
            users = [users]
        
        self.log(f"Creating {len(users)} users")
        
        created = []
        failed = []
        
        for user in users:
            try:
                user_id = self._create_user(user)
                created.append(user_id)
                self.log(f"Created user: {user.get('login')}")
                
            except Exception as e:
                self.log(f"Error creating user: {str(e)}", "ERROR")
                failed.append(user.get('login'))
        
        return {
            'status': 'success' if created else 'error',
            'created': len(created),
            'failed': len(failed)
        }
    
    def _create_user(self, config: dict) -> int:
        """Create user"""
        user_data = {
            'name': config.get('name'),
            'login': config.get('login'),
            'email': config.get('email', config.get('login')),
        }
        
        user_id = self.odoo.create('res.users', user_data)
        
        # Assign groups
        if 'groups' in config:
            self._assign_groups(user_id, config['groups'])
        
        return user_id
    
    def _assign_groups(self, user_id: int, groups: list):
        """Assign user to groups"""
        for group_name in groups:
            # Find group and assign
            pass
