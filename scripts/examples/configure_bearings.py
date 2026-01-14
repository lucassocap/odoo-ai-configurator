#!/usr/bin/env python3
"""
Example: Configure Bearings Inc
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from orchestrator import Orchestrator


def main():
    # Initialize
    orchestrator = Orchestrator(
        url="http://localhost:8069",
        db="bearings",
        username="admin",
        password="admin"
    )
    
    # Configure company
    print("1. Configuring company...")
    orchestrator.configure("Setup company", {
        'name': 'Bearings Inc',
        'email': 'info@bearingsinc.com',
        'phone': '+1-555-BEARING',
        'website': 'https://bearingsinc.com',
        'city': 'Chicago',
        'zip': '60601',
    })
    
    # Install modules
    print("\n2. Installing modules...")
    orchestrator.configure("Install modules", {
        'modules': ['website', 'ecommerce', 'crm', 'inventory']
    })
    
    # Import products
    print("\n3. Importing products...")
    orchestrator.configure("Import products", {
        'file': '../../inventory_with_descriptions.csv',
        'auto_publish': True
    })
    
    print("\n✅ Bearings Inc configured successfully!")


if __name__ == '__main__':
    main()
