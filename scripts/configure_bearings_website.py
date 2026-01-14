#!/usr/bin/env python3
"""
Configure Bearings Website
Complete website setup based on Netora design
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import Orchestrator


def load_products(products_file):
    """Load selected products"""
    with open(products_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def configure_website():
    """Configure complete website"""
    print("🌐 Configuring Bearings Inc Website")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        url="http://localhost:8069",
        db="bearings",
        username="admin",
        password="admin"
    )
    
    # Load products
    products_file = Path(__file__).parent.parent / "data" / "bearing_products.json"
    product_data = load_products(products_file)
    
    print(f"\n📦 Loaded {product_data['total']} products")
    print(f"   Categories: {', '.join(product_data['categories'])}")
    print(f"   Brands: {', '.join(product_data['brands'])}")
    
    # Configure website
    print("\n🎨 Configuring website...")
    
    config = {
        'action': 'full_setup',
        'theme': {
            'primary_color': '#0d1b2a',  # Netora dark blue
            'accent_color': '#3498db',   # Light blue
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
    }
    
    result = orchestrator.configure("Configure website", config)
    
    print("\n" + "=" * 70)
    print("✅ Website Configuration Complete!")
    print("\n🔗 Access your website at: http://localhost:8069")
    print("   Database: bearings")
    print("   Username: admin")
    print("   Password: admin")
    
    return result


if __name__ == '__main__':
    configure_website()
