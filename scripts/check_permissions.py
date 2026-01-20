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
        
        # Check User Groups
        user = models.execute_kw(db, uid, password, 'res.users', 'read', [[uid], ['name', 'groups_id']])
        print(f"User: {user[0]['name']}")
        
        # Check if they have access to CRM menu
        # CRM menu usually requires 'sales_team.group_sale_salesman' or similar
        # Let's list the top menus they can see
        menus = models.execute_kw(db, uid, password, 'ir.ui.menu', 'search_read', [[('parent_id', '=', False)], ['name', 'action']])
        print("Visible Root Menus:")
        for m in menus:
            print(f" - {m['name']} (Action: {m['action']})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
