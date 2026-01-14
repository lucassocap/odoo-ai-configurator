"""
Tests for MCP Protocol
"""
import pytest
from src.mcp.protocol import MCPCapability, MCPProtocol, MCPTool


def test_mcp_protocol_initialization():
    """Test MCP protocol initialization"""
    protocol = MCPProtocol()
    
    assert protocol.VERSION == "1.0"
    assert protocol.PROTOCOL_NAME == "odoo-configurator-mcp"
    assert len(protocol.tools) > 0
    assert len(protocol.capabilities) > 0


def test_mcp_get_schema():
    """Test MCP schema generation"""
    protocol = MCPProtocol()
    schema = protocol.get_schema()
    
    assert 'protocol' in schema
    assert 'version' in schema
    assert 'capabilities' in schema
    assert 'tools' in schema


def test_mcp_list_tools():
    """Test listing MCP tools"""
    protocol = MCPProtocol()
    tools = protocol.list_tools()
    
    assert isinstance(tools, list)
    assert len(tools) > 0
    assert 'name' in tools[0]
    assert 'description' in tools[0]


def test_mcp_get_tool():
    """Test getting specific tool"""
    protocol = MCPProtocol()
    tool = protocol.get_tool('configure_company')
    
    assert tool is not None
    assert tool.name == 'configure_company'
