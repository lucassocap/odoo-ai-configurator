"""
Odoo XML-RPC Connector
"""
import xmlrpc.client
from typing import Any, Dict, List, Optional


class OdooConnector:
    """Connect to Odoo via XML-RPC"""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid: Optional[int] = None
        self.models: Optional[xmlrpc.client.ServerProxy] = None
        
    def connect(self) -> bool:
        """Authenticate and connect to Odoo"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.db, self.username, self.password, {})
            
            if not self.uid:
                return False
            
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute Odoo method"""
        if not self.models or not self.uid:
            raise RuntimeError("Not connected to Odoo")
        
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    def search(self, model: str, domain: List, **kwargs) -> List[int]:
        """Search for records"""
        return self.execute(model, 'search', [domain], kwargs)
    
    def read(self, model: str, ids: List[int], fields: List[str] = None) -> List[Dict]:
        """Read records"""
        kwargs = {'fields': fields} if fields else {}
        return self.execute(model, 'read', ids, kwargs)
    
    def create(self, model: str, values: Dict) -> int:
        """Create record"""
        return self.execute(model, 'create', [values])
    
    def write(self, model: str, ids: List[int], values: Dict) -> bool:
        """Update records"""
        return self.execute(model, 'write', [ids, values])
    
    def unlink(self, model: str, ids: List[int]) -> bool:
        """Delete records"""
        return self.execute(model, 'unlink', [ids])
