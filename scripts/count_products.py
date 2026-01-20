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
        
        # Count products
        count = models.execute_kw(db, uid, password, 'product.template', 'search_count', [[]])
        print(f"📊 Current Product Count: {count}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
