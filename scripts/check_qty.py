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
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        code = '23034-CC/C3W33'
        pids = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[('default_code', '=', code)]], {'fields': ['id', 'name', 'qty_available']})
        
        if pids:
            print(f"Product: {code}")
            print(f"Qty Available: {pids[0]['qty_available']}")
        else:
            print("Product not found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
