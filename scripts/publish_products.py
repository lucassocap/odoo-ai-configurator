import os
import sys
import xmlrpc.client

# Add src to path
sys.path.append(os.getcwd())

from src.connectors.odoo import OdooConnector

def run():
    url = os.getenv("ODOO_URL", "http://localhost:8069")
    username = os.getenv("ODOO_USER", "admin")
    password = os.getenv("ODOO_PASSWORD", "admin")
    db = "bearings"

    print(f"Connecting to {url} (db: {db})...")
    
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        if not uid:
            print("❌ Auth failed")
            return
            
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # 1. Search All Products
        ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[]])
        print(f"Found {len(ids)} products.")
        
        # 2. Update to Published
        if ids:
            print("Publishing all products (is_published=True, website_published=True)...")
            models.execute_kw(db, uid, password, 'product.template', 'write', [ids, {'is_published': True, 'website_published': True}])
            print("✅ All products published.")
            
        # 3. Check Image Count
        # Count how many have image_1920 set
        has_img_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[('image_1920', '!=', False)]])
        print(f"📊 Products with Images: {len(has_img_ids)} / {len(ids)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
