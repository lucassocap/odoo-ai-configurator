#!/usr/bin/env python3
"""
Odoo AI Configurator CLI
"""
import sys
from pathlib import Path

import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from orchestrator import Orchestrator


def main():
    print("🤖 Odoo AI Configurator")
    print("=" * 50)
    print()
    
    # Check for config file argument
    if len(sys.argv) > 1 and sys.argv[1].endswith('.yaml'):
        config_file = sys.argv[1]
        print(f"Loading configuration from: {config_file}\n")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize orchestrator
        orchestrator = Orchestrator(
            url="http://localhost:8069",
            db="bearings",
            username="admin",
            password="admin"
        )
        
        # Execute configuration
        result = orchestrator.configure_from_dict(config)
        
        print("\n✅ Configuration complete!")
        print(f"Sections configured: {result['sections']}")
        
        for section_result in result['results']:
            section = section_result['section']
            status = section_result['result']['status']
            print(f"  {section}: {status}")
        
    else:
        # Interactive mode
        print("What would you like to configure?")
        print("Examples:")
        print("  - Setup company")
        print("  - Install eCommerce modules")
        print("  - Import products from CSV")
        print()
        
        request = input("> ")
        
        if not request:
            print("No request provided")
            return
        
        # Initialize orchestrator
        orchestrator = Orchestrator(
            url="http://localhost:8069",
            db="bearings",
            username="admin",
            password="admin"
        )
        
        # Execute
        result = orchestrator.configure(request)
        
        print(f"\n✅ Executed {result['agents_executed']} agents")


if __name__ == '__main__':
    main()
