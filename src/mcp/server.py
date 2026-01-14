"""
MCP Server
Exposes Odoo configurator via MCP protocol
"""
from typing import Any, Dict

from ..orchestrator import Orchestrator
from .protocol import MCPProtocol


class MCPServer:
    """MCP Server for Odoo Configurator"""
    
    def __init__(self, odoo_url: str, db: str = "odoo", username: str = "admin", password: str = "admin"):
        self.protocol = MCPProtocol()
        self.orchestrator = Orchestrator(odoo_url, db, username, password)
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP request
        
        Args:
            request: MCP request dict with 'tool' and 'parameters'
            
        Returns:
            MCP response dict
        """
        tool_name = request.get('tool')
        params = request.get('parameters', {})
        
        # Map MCP tool to agent execution
        tool_map = {
            'configure_company': ('company', params),
            'install_modules': ('modules', params),
            'import_products': ('products', params),
            'configure_website': ('website', params),
            'configure_integrations': ('integrations', params),
        }
        
        if tool_name not in tool_map:
            return {
                'status': 'error',
                'message': f'Unknown tool: {tool_name}'
            }
        
        request_type, agent_params = tool_map[tool_name]
        result = self.orchestrator.configure(request_type, agent_params)
        
        return {
            'status': 'success',
            'result': result
        }
    
    def get_schema(self) -> dict:
        """Get MCP schema"""
        return self.protocol.get_schema()
    
    def list_tools(self) -> list:
        """List available tools"""
        return self.protocol.list_tools()
