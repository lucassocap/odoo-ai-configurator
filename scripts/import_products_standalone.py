#!/usr/bin/env python3
"""
Bearings Inc - Product Import Script
Standalone script to import 20 bearing products
"""
import base64
import json
import xmlrpc.client
from pathlib import Path


def connect_odoo(url, db, username, password):
    """Connect to Odoo"""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        raise Exception("Authentication failed")
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    return uid, models


def import_products(url, db, username, password, products_file):
    """Import products to Odoo"""
    print("🚀 Bearings Inc - Product Import")
    print("=" * 70)
    
    # Connect
    print("\n🔌 Connecting to Odoo...")
    uid, models = connect_odoo(url, db, username, password)
    print(f"✅ Connected as user ID: {uid}")
    
    # Load products
    print(f"\n📦 Loading products from {products_file}...")
    with open(products_file, 'r') as f:
        data = json.load(f)
    
    products = data['products']
    print(f"✅ Loaded {len(products)} products")
    
    # Import products
    print("\n📥 Importing products...")
    imported = 0
    errors = []
    
    for i, product in enumerate(products, 1):
        try:
            print(f"\n[{i}/{len(products)}] {product['name']}")
            
            # Prepare product data
            product_data = {
                'name': product['name'],
                'default_code': product['sku'],
                'list_price': float(product['price']),
                'description_sale': product['description'],
                'type': 'product',
                'website_published': True,
            }
            
            # Create product
            product_id = models.execute_kw(
                db, uid, password,
                'product.template', 'create',
                [product_data]
            )
            
            print(f"   ✅ Created product ID: {product_id}")
            
            # Upload image if exists
            image_path = Path(product['image_path'])
            if image_path.exists():
                with open(image_path, 'rb') as img:
                    image_data = base64.b64encode(img.read()).decode('utf-8')
                
                models.execute_kw(
                    db, uid, password,
                    'product.template', 'write',
                    [[product_id], {'image_1920': image_data}]
                )
                print(f"   📷 Image uploaded")
            
            imported += 1
            
        except Exception as e:
            error_msg = f"{product['name']}: {str(e)}"
            errors.append(error_msg)
            print(f"   ❌ Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Import Summary:")
    print(f"   ✅ Successfully imported: {imported}/{len(products)}")
    print(f"   ❌ Errors: {len(errors)}")
    
    if errors:
        print("\n⚠️  Errors:")
        for error in errors[:5]:  # Show first 5
            print(f"   - {error}")
    
    print("\n🔗 Access your website:")
    print(f"   URL: {url}")
    print(f"   Database: {db}")
    print(f"   Username: {username}")
    
    return imported, errors


def main():
    # Configuration
    URL = "http://localhost:8069"
    DB = "bearings"
    USERNAME = "admin"
    PASSWORD = "admin"
    PRODUCTS_FILE = "data/bearing_products.json"
    
    try:
        imported, errors = import_products(URL, DB, USERNAME, PASSWORD, PRODUCTS_FILE)
        
        if imported > 0:
            print("\n✅ Import completed successfully!")
            exit(0)
        else:
            print("\n❌ Import failed!")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()
