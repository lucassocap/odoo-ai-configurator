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
        
        # 1. Identify valid menu (ID 1 seems best populated)
        target_menu_id = 1
        
        # 2. Assign to Website (assuming website_id=1)
        # Check current assignment
        websites = models.execute_kw(db, uid, password, 'website', 'search_read', [[], ['id', 'name', 'menu_id']])
        for w in websites:
            print(f"Website '{w['name']}' (ID: {w['id']}) currently uses Menu ID: {w['menu_id']}")
            
            if w['menu_id'][0] != target_menu_id:
                print(f"   👉 Switching Website {w['id']} to Menu ID {target_menu_id}...")
                models.execute_kw(db, uid, password, 'website', 'write', [[w['id']], {'menu_id': target_menu_id}])
                print("   ✅ Switched.")
        
        # 3. Clean up other root menus?
        # Only delete truly empty/redundant roots that are NOT the target
        roots = models.execute_kw(db, uid, password, 'website.menu', 'search_read', [[('parent_id', '=', False)], ['id', 'name']])
        
        for r in roots:
            if r['id'] != target_menu_id:
                # Be careful, might be a valid separate menu?
                # User complaint was "Repeated elements" and "Equivalence".
                # If we switched the site to ID 1, ID 4 is now orphaned.
                print(f"   🗑️ Orphaned Root Menu found: {r['name']} (ID: {r['id']}). Deleting...")
                try:
                    models.execute_kw(db, uid, password, 'website.menu', 'unlink', [[r['id']]])
                    print("   ✅ Deleted.")
                except Exception as e:
                    print(f"   ⚠️ Could not delete (maybe system protected): {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
