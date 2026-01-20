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
        
        # Search for 'WH/Stock' or usage='internal'
        locs = models.execute_kw(db, uid, password, 'stock.location', 'search_read', 
            [[('usage', '=', 'internal')]], 
            {'fields': ['id', 'name', 'complete_name']})
            
        print(f"Found {len(locs)} Internal Locations:")
        for loc in locs:
            print(f" - ID: {loc['id']} | Name: {loc['name']} | Complete: {loc['complete_name']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
