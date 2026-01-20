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
        
        # Check 'crm' module
        modules = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', [[('name', '=', 'crm')], ['state']])
        
        if modules:
            state = modules[0]['state']
            print(f"Module 'crm' status: {state}")
            if state != 'installed':
                print("Installing CRM...")
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [[modules[0]['id']]])
                print("✅ CRM Installed.")
        else:
            print("CRM Module record not found (weird).")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
