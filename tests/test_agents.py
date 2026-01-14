"""
Tests for Agents
"""
from unittest.mock import Mock

import pytest
from src.agents.company import CompanyAgent
from src.agents.modules import ModuleAgent
from src.agents.products import ProductAgent


def test_company_agent_can_handle():
    """Test CompanyAgent can handle company requests"""
    connector = Mock()
    agent = CompanyAgent(connector)
    
    assert agent.can_handle("configure company") is True
    assert agent.can_handle("setup business") is True
    assert agent.can_handle("install module") is False


def test_module_agent_can_handle():
    """Test ModuleAgent can handle module requests"""
    connector = Mock()
    agent = ModuleAgent(connector)
    
    assert agent.can_handle("install modules") is True
    assert agent.can_handle("activate ecommerce") is True
    assert agent.can_handle("configure company") is False


def test_product_agent_can_handle():
    """Test ProductAgent can handle product requests"""
    connector = Mock()
    agent = ProductAgent(connector)
    
    assert agent.can_handle("import products") is True
    assert agent.can_handle("add inventory") is True
    assert agent.can_handle("configure company") is False
