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
        
        # 1. Fetch Top-Level Menus
        # Just a simple heuristic: remove duplicates by name
        menus = models.execute_kw(db, uid, password, 'website.menu', 'search_read', [[], ['id', 'name', 'url', 'parent_id']])
        
        seen = {}
        to_delete = []
        
        print(f"Scanning {len(menus)} menu items...")
        
        for menu in menus:
            # key = (name, url, parent_id)
            parent = menu['parent_id'][0] if menu['parent_id'] else False
            key = (menu['name'], menu['url'], parent)
            
            if key in seen:
                # Duplicate!
                print(f"   🗑️ Duplicate found: {menu['name']} (ID: {menu['id']}) - Keeping ID {seen[key]}")
                to_delete.append(menu['id'])
            else:
                seen[key] = menu['id']
                
        if to_delete:
            print(f"Deleting {len(to_delete)} duplicate menus...")
            models.execute_kw(db, uid, password, 'website.menu', 'unlink', [to_delete])
            print("✅ Menus Cleaned.")
        else:
            print("✅ No duplicates found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
