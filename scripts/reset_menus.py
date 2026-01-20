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
        
        # 1. Get Active Website's Root Menu
        websites = models.execute_kw(db, uid, password, 'website', 'search_read', [[], ['id', 'name', 'menu_id']])
        if not websites:
            print("No website found!")
            return

        website = websites[0]

        if not website['menu_id']:
            print("   ⚠️ Website has no Root Menu! Creating one...")
            root_menu_id = models.execute_kw(db, uid, password, 'website.menu', 'create', [{
                'name': 'Main Menu',
                'website_id': website['id']
            }])
            # Assign to website
            models.execute_kw(db, uid, password, 'website', 'write', [[website['id']], {'menu_id': root_menu_id}])
            print(f"   ✅ Created and Assigned Root Menu ID: {root_menu_id}")
        else:
            root_menu_id = website['menu_id'][0]
            
        print(f"Targeting Website '{website['name']}' -> Root Menu ID: {root_menu_id}")
        
        # 2. DELETE all children of this root
        child_ids = models.execute_kw(db, uid, password, 'website.menu', 'search', [[('parent_id', '=', root_menu_id)]])
        if child_ids:
            print(f"   🗑️ Wiping {len(child_ids)} existing menu items...")
            models.execute_kw(db, uid, password, 'website.menu', 'unlink', [child_ids])
            print("   ✅ Cleaned.")
        
        # 3. CREATE Standard Items
        items = [
            {'name': 'Home', 'url': '/', 'sequence': 10},
            {'name': 'Shop', 'url': '/shop', 'sequence': 20},
            {'name': 'Blog', 'url': '/blog', 'sequence': 25},
            {'name': 'Products', 'url': '/shop', 'sequence': 30},
            {'name': 'About Us', 'url': '/about-us', 'sequence': 40},
            {'name': 'Contact Us', 'url': '/contactus', 'sequence': 50},
        ]
        
        print("   🔨 Rebuilding Menu Items...")
        for item in items:
            item['parent_id'] = root_menu_id
            item['website_id'] = website['id']
            models.execute_kw(db, uid, password, 'website.menu', 'create', [item])
            print(f"      + Created '{item['name']}' -> {item['url']}")
            
        print("\n✨ Menu Reset Complete. Please refresh browser.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
