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
        
        # 1. Check Integration Modules
        target_modules = ['website_crm', 'website_sale_stock', 'website_sale_delivery', 'delivery']
        modules = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', 
            [[('name', 'in', target_modules)]], 
            {'fields': ['name', 'state']})
            
        print("Integration Status:")
        installed = {m['name']: m['state'] for m in modules}
        for tm in target_modules:
            status = installed.get(tm, 'not installed')
            print(f" - {tm}: {status}")
            
            # Install if missing (Auto-fix)
            if status != 'installed':
                print(f"   Installing {tm}...")
                try:
                    models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', 
                        [[models.execute_kw(db, uid, password, 'ir.module.module', 'search', [[('name', '=', tm)]])[0]]])
                    print(f"   ✅ {tm} Installed.")
                except Exception as inst_e:
                    print(f"   ❌ Failed to install {tm}: {inst_e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
