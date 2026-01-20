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
        
        # 1. Fetch Homepage View
        # key usually "website.homepage"
        views = models.execute_kw(db, uid, password, 'ir.ui.view', 'search_read', [[('key', '=', 'website.homepage')], ['id', 'arch', 'arch_db']])
        
        if not views:
            # Maybe it's a custom view? Check homepage_url of website
            print("website.homepage view not found. Checking website config...")
            websites = models.execute_kw(db, uid, password, 'website', 'search_read', [[], ['id', 'homepage_id']])
            if websites and websites[0]['homepage_id']:
                vid = websites[0]['homepage_id'][0]
                views = models.execute_kw(db, uid, password, 'ir.ui.view', 'read', [[vid], ['id', 'arch', 'arch_db']])
            
        if views:
            v = views[0]
            print(f"Found Homepage View ID: {v['id']}")
            print("--- ARCH START ---")
            print(v['arch'])
            print("--- ARCH END ---")
        else:
            print("❌ Homepage View NOT Found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
