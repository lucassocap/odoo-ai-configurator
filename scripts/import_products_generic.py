#!/usr/bin/env python3
"""
Odoo Product Import Tool - Generic
Standalone script to import products from JSON file
"""
import argparse
import base64
import json
import sys
import xmlrpc.client
from pathlib import Path


def connect_odoo(url, db, username, password):
    """Connect to Odoo"""
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            raise Exception("Authentication failed")
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        return uid, models
    except Exception as e:
        print(f"Connection Error: {e}")
        raise


def import_products(url, db, username, password, products_file):
    """Import products to Odoo"""
    print("🚀 Odoo Product Import")
    print("=" * 70)
    
    # Connect
    print("\n🔌 Connecting to Odoo...")
    try:
        uid, models = connect_odoo(url, db, username, password)
        print(f"✅ Connected as user ID: {uid}")
    except Exception as e:
        return 0, [str(e)]
    
    # Load products
    print(f"\n📦 Loading products from {products_file}...")
    try:
        with open(products_file, 'r') as f:
            data = json.load(f)
        
        # Support both list directly or key 'products'
        products = data.get('products', data) if isinstance(data, dict) else data
        
        if not isinstance(products, list):
            raise ValueError("JSON must contain a list of products")
            
        print(f"✅ Loaded {len(products)} products")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return 0, [str(e)]
    
    # Import products
    print("\n📥 Importing products...")
    imported = 0
    errors = []
    
    for i, product in enumerate(products, 1):
        try:
            name = product.get('name', 'Unknown Product')
            print(f"\n[{i}/{len(products)}] {name}")
            
            # Prepare product data (generic mapping)
            product_data = {
                'name': name,
                'default_code': product.get('sku', product.get('default_code')),
                'list_price': float(product.get('price', product.get('list_price', 0))),
                'description_sale': product.get('description', product.get('description_sale', '')),
                'type': product.get('type', 'product'),
                'website_published': product.get('website_published', True),
            }
            
            # Clean None values
            product_data = {k: v for k, v in product_data.items() if v is not None}
            
            # Create product
            product_id = models.execute_kw(
                db, uid, password,
                'product.template', 'create',
                [product_data]
            )
            
            print(f"   ✅ Created product ID: {product_id}")
            
            # Upload image if exists
            image_path_str = product.get('image_path')
            if image_path_str:
                image_path = Path(image_path_str)
                if image_path.exists():
                    with open(image_path, 'rb') as img:
                        image_data = base64.b64encode(img.read()).decode('utf-8')
                    
                    models.execute_kw(
                        db, uid, password,
                        'product.template', 'write',
                        [[product_id], {'image_1920': image_data}]
                    )
                    print(f"   📷 Image uploaded")
                else:
                    print(f"   ⚠️ Image not found: {image_path}")
            
            imported += 1
            
        except Exception as e:
            error_msg = f"{product.get('name', 'Unknown')}: {str(e)}"
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
    
    return imported, errors


def main():
    parser = argparse.ArgumentParser(description='Import products to Odoo from JSON')
    parser.add_argument('--url', default='http://localhost:8069', help='Odoo URL')
    parser.add_argument('--db', required=True, help='Database name')
    parser.add_argument('--user', default='admin', help='Username')
    parser.add_argument('--password', default='admin', help='Password')
    parser.add_argument('file', help='JSON file containing products')
    
    args = parser.parse_args()
    
    try:
        imported, errors = import_products(args.url, args.db, args.user, args.password, args.file)
        
        if imported > 0:
            print("\n✅ Import completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Import failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
