"""
Odoo AI Configurator
AI-powered universal Odoo configuration system
"""

__version__ = "0.1.0"

from .agents.base import OdooAgent
from .orchestrator import Orchestrator

__all__ = ["Orchestrator", "OdooAgent"]
