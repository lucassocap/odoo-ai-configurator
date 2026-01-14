"""
MCP Protocol Implementation
Model Context Protocol for AI interoperability
"""
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MCPCapability:
    """MCP Capability"""
    name: str
    enabled: bool
    version: str = "1.0"
    
    def to_dict(self) -> dict:
        return asdict(self)


class MCPProtocol:
    """Model Context Protocol implementation"""
    
    VERSION = "1.0"
    PROTOCOL_NAME = "odoo-configurator-mcp"
    
    def __init__(self):
        self.tools: List[MCPTool] = []
        self.capabilities: List[MCPCapability] = []
        self._register_tools()
        self._register_capabilities()
    
    def _register_tools(self):
        """Register available tools"""
        self.tools = [
            MCPTool(
                name="configure_company",
                description="Configure Odoo company details",
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Company name"},
                        "email": {"type": "string", "description": "Email address"},
                        "phone": {"type": "string", "description": "Phone number"},
                        "website": {"type": "string", "description": "Website URL"},
                    },
                    "required": ["name"]
                }
            ),
            MCPTool(
                name="install_modules",
                description="Install Odoo modules",
                parameters={
                    "type": "object",
                    "properties": {
                        "modules": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of module names"
                        }
                    },
                    "required": ["modules"]
                }
            ),
            MCPTool(
                name="import_products",
                description="Import products from CSV or create programmatically",
                parameters={
                    "type": "object",
                    "properties": {
                        "file": {"type": "string", "description": "CSV file path"},
                        "auto_publish": {"type": "boolean", "description": "Publish to website"}
                    }
                }
            ),
            MCPTool(
                name="configure_website",
                description="Configure website and eCommerce",
                parameters={
                    "type": "object",
                    "properties": {
                        "publish": {"type": "boolean"},
                        "ecommerce": {"type": "boolean"},
                    }
                }
            ),
            MCPTool(
                name="configure_integrations",
                description="Configure external integrations",
                parameters={
                    "type": "object",
                    "properties": {
                        "integrations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"},
                                    "credentials": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            ),
        ]
    
    def _register_capabilities(self):
        """Register MCP capabilities"""
        self.capabilities = [
            MCPCapability("company_setup", True),
            MCPCapability("module_management", True),
            MCPCapability("product_import", True),
            MCPCapability("website_config", True),
            MCPCapability("integrations", True),
            MCPCapability("automation", True),
            MCPCapability("user_management", True),
        ]
    
    def get_schema(self) -> dict:
        """Get MCP schema"""
        return {
            "protocol": self.PROTOCOL_NAME,
            "version": self.VERSION,
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "tools": [tool.to_dict() for tool in self.tools]
        }
    
    def list_tools(self) -> List[Dict]:
        """List available tools"""
        return [tool.to_dict() for tool in self.tools]
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get tool by name"""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
