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
        
        # Fetch all menus
        menus = models.execute_kw(db, uid, password, 'website.menu', 'search_read', [[], ['id', 'name', 'url', 'parent_id', 'website_id']])
        
        # Organize by Parent
        tree = {}
        for m in menus:
            pid = m['parent_id'][0] if m['parent_id'] else 0
            if pid not in tree:
                tree[pid] = []
            tree[pid].append(m)
            
        def print_tree(pid, level=0):
            items = tree.get(pid, [])
            for item in items:
                indent = "  " * level
                print(f"{indent}📂 {item['name']} (ID: {item['id']}) -> {item['url']}")
                print_tree(item['id'], level + 1)

        print("\n🌳 Menu Tree Structure:")
        print_tree(0)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
