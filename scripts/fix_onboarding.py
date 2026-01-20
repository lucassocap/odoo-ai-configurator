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
        
        # 1. Search for 'onboarding' module
        # In newer Odoo versions, 'onboarding' is a standalone module
        modules = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', 
            [[('name', 'in', ['onboarding', 'account', 'sale'])]], 
            {'fields': ['id', 'name', 'state']})
            
        for mod in modules:
            if mod['state'] == 'installed':
                print(f"Upgrading module: {mod['name']}...")
                try:
                    models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_upgrade', [[mod['id']]])
                    print(f"✅ {mod['name']} Upgraded.")
                except Exception as e:
                    print(f"❌ Failed to upgrade {mod['name']}: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
