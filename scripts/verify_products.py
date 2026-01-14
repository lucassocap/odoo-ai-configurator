#!/usr/bin/env python3
"""
Verify Products Loaded
Check how many products were successfully loaded
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors.odoo import OdooConnector


def main():
    """Verify products loaded"""
    print("🔍 Verifying Products in Odoo")
    print("=" * 70)
    
    # Connect to Odoo
    odoo = OdooConnector(
        url="http://localhost:8069",
        db="bearings",
        username="admin",
        password="admin"
    )
    
    if not odoo.connect():
        print("❌ Failed to connect to Odoo")
        return
    
    print("✅ Connected to Odoo\n")
    
    
    # Check products (fix for Odoo 18 bug with empty domains)
    print("📦 Checking Products...")
    try:
        products = odoo.search('product.template', [('id', '>', 0)])
    except Exception as e:
        print(f"   Error searching products: {e}")
        products = []
    print(f"   Total products: {len(products)}")
    
    if products:
        # Get product details
        product_data = odoo.read('product.template', products, ['name', 'default_code', 'list_price', 'website_published'])
        
        print("\n📋 Products loaded:")
        for i, product in enumerate(product_data[:20], 1):  # Show first 20
            published = "✅" if product.get('website_published') else "❌"
            print(f"   {i}. {published} {product.get('name')} (SKU: {product.get('default_code')}) - ${product.get('list_price')}")
    
    # Check categories
    print("\n📁 Checking Categories...")
    try:
        categories = odoo.search('product.public.category', [('id', '>', 0)])
    except Exception as e:
        print(f"   Error searching categories: {e}")
        categories = []
    print(f"   Total categories: {len(categories)}")
    
    if categories:
        cat_data = odoo.read('product.public.category', categories, ['name'])
        print("\n📋 Categories:")
        for cat in cat_data:
            print(f"   - {cat.get('name')}")
    
    # Check website
    print("\n🌐 Checking Website...")
    try:
        websites = odoo.search('website', [('id', '>', 0)])
    except Exception as e:
        print(f"   Error searching websites: {e}")
        websites = []
    print(f"   Websites configured: {len(websites)}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary:")
    print(f"   Products: {len(products)}")
    print(f"   Categories: {len(categories)}")
    print(f"   Websites: {len(websites)}")
    
    if len(products) >= 20:
        print("\n✅ SUCCESS: 20+ products loaded!")
    elif len(products) > 0:
        print(f"\n⚠️  WARNING: Only {len(products)} products loaded (expected 20)")
    else:
        print("\n❌ ERROR: No products loaded")


if __name__ == '__main__':
    main()
