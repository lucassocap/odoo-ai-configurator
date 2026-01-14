"""
Agents package
"""
from .automation import AutomationAgent
from .base import OdooAgent
from .cloud_deploy import CloudDeployAgent
from .company import CompanyAgent
from .integrations import IntegrationAgent
from .modules import ModuleAgent
from .products import ProductAgent
from .users import UserAgent
from .website import WebsiteAgent

__all__ = [
    'OdooAgent',
    'CompanyAgent',
    'ModuleAgent',
    'ProductAgent',
    'WebsiteAgent',
    'IntegrationAgent',
    'AutomationAgent',
    'UserAgent',
    'CloudDeployAgent',
]
