"""
Tests for Odoo Connector
"""
from unittest.mock import Mock, patch

import pytest
from src.connectors.odoo import OdooConnector


def test_connector_initialization():
    """Test connector initialization"""
    connector = OdooConnector(
        url="http://localhost:8069",
        db="test",
        username="admin",
        password="admin"
    )
    
    assert connector.url == "http://localhost:8069"
    assert connector.db == "test"
    assert connector.username == "admin"


@patch('xmlrpc.client.ServerProxy')
def test_connector_connect(mock_proxy):
    """Test connection to Odoo"""
    mock_common = Mock()
    mock_common.authenticate.return_value = 1
    mock_proxy.return_value = mock_common
    
    connector = OdooConnector("http://localhost:8069", "test", "admin", "admin")
    result = connector.connect()
    
    assert result is True
    assert connector.uid == 1


def test_connector_execute_without_connection():
    """Test execute without connection raises error"""
    connector = OdooConnector("http://localhost:8069", "test", "admin", "admin")
    
    with pytest.raises(RuntimeError):
        connector.execute('res.partner', 'search', [])
