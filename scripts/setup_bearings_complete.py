#!/usr/bin/env python3
"""
Install Required Modules and Configure Website
Complete setup for Bearings Inc
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import Orchestrator


def main():
    """Install modules and configure website"""
    print("🚀 Setting up Bearings Inc Website")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        url="http://localhost:8069",
        db="bearings",
        username="admin",
        password="admin"
    )
    
    # Step 1: Install required modules
    print("\n📦 Installing required modules...")
    modules_to_install = [
        'stock',           # Inventory
        'website',         # Website
        'website_sale'     # eCommerce
    ]
    
    for module in modules_to_install:
        print(f"   Installing {module}...")
        result = orchestrator.configure(f"Install {module} module", {
            'modules': [module]
        })
        print(f"   ✅ {module} installed")
    
    # Step 2: Load products
    print("\n📦 Loading 20 bearing products...")
    products_file = Path(__file__).parent.parent / "data" / "bearing_products.json"
    
    with open(products_file, 'r', encoding='utf-8') as f:
        product_data = json.load(f)
    
    print(f"   Products: {product_data['total']}")
    print(f"   Brands: {', '.join(product_data['brands'])}")
    
    # Step 3: Configure website
    print("\n🎨 Configuring website...")
    result = orchestrator.configure("Configure website", {
        'action': 'full_setup',
        'theme': {
            'primary_color': '#0d1b2a',
            'accent_color': '#3498db',
            'font_family': 'sans-serif',
            'layout': 'grid_4_columns'
        },
        'categories': [
            {'name': 'Ball Bearings', 'parent_id': False},
            {'name': 'Roller Bearings', 'parent_id': False},
            {'name': 'Thrust Bearings', 'parent_id': False},
            {'name': 'Special Bearings', 'parent_id': False}
        ],
        'products': product_data['products']
    })
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("\n🔗 Access your website:")
    print("   URL: http://localhost:8069")
    print("   Database: bearings")
    print("   Username: admin")
    print("   Password: admin")
    print("\n📊 Summary:")
    print(f"   Modules installed: {len(modules_to_install)}")
    print(f"   Products loaded: {product_data['total']}")
    print(f"   Categories: {len(product_data['categories'])}")
    print(f"   Brands: {len(product_data['brands'])}")


if __name__ == '__main__':
    main()
