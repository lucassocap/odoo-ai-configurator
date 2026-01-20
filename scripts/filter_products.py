import os
import sys
import xmlrpc.client

# Add src to path
sys.path.append(os.getcwd())

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
        
        # 1. Find Zero Price Products
        # Domain: list_price <= 0.01
        print("🔍 Searching for products with Price ~ 0...")
        zero_price_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[('list_price', '<=', 0.01)]])
        
        if zero_price_ids:
            print(f"   Found {len(zero_price_ids)} products with Zero Price. Hiding from Website...")
            # Unpublish
            models.execute_kw(db, uid, password, 'product.template', 'write', [zero_price_ids, {'website_published': False}])
            print("   ✅ Hidden from website.")
        else:
            print("   ✅ No zero-price products found.")

        # 2. Ensure Valid Products are Published
        # Domain: list_price > 0.01
        print("🔍 Searching for valid products (Price > 0)...")
        valid_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[('list_price', '>', 0.01)]])
        
        if valid_ids:
             print(f"   Found {len(valid_ids)} valid products. Ensuring they are Published...")
             models.execute_kw(db, uid, password, 'product.template', 'write', [valid_ids, {'website_published': True}])
             print("   ✅ Valid products published.")

        print(f"\n📊 Summary: Hidden {len(zero_price_ids)} | Visible {len(valid_ids)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
