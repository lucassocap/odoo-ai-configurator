#!/usr/bin/env python3
"""
Example: Deploy Odoo to Google Cloud with Multi-Tenant Support
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from orchestrator import Orchestrator


def main():
    print("🚀 Deploying Odoo to Google Cloud")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        url="http://localhost:8069",
        db="bearings",
        username="admin",
        password="admin"
    )
    
    # Step 1: Setup Google Cloud Infrastructure
    print("\n1. Setting up Google Cloud infrastructure...")
    result = orchestrator.configure("Deploy to cloud", {
        'action': 'setup',
        'project_id': 'my-odoo-project',
        'region': 'us-central1'
    })
    
    print(f"   Status: {result['results'][0]['result']['status']}")
    
    # Step 2: Deploy base Odoo image
    print("\n2. Deploying base Odoo image...")
    result = orchestrator.configure("Deploy to production", {
        'action': 'deploy',
        'project_id': 'my-odoo-project'
    })
    
    print(f"   Status: {result['results'][0]['result']['status']}")
    
    # Step 3: Create first client
    print("\n3. Creating first client...")
    result = orchestrator.configure("Create multi-tenant client", {
        'action': 'create_client',
        'client_name': 'bearings-inc',
        'project_id': 'my-odoo-project'
    })
    
    print(f"   Status: {result['results'][0]['result']['status']}")
    print(f"   Client: {result['results'][0]['result'].get('client_name')}")
    
    print("\n" + "=" * 60)
    print("✅ Cloud deployment complete!")
    print("\nNext steps:")
    print("1. Access your Odoo instance at the provided URL")
    print("2. Complete initial setup wizard")
    print("3. Create additional clients as needed")


if __name__ == '__main__':
    main()
