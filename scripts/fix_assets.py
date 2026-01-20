import os
import sys
import xmlrpc.client

# Add src to path
sys.path.append(os.getcwd())

from src.connectors.odoo import OdooConnector

def run():
    url = os.getenv("ODOO_URL", "http://localhost:8069")
    username = os.getenv("ODOO_USER", "admin")
    password = os.getenv("ODOO_PASSWORD", "admin")
    db = "bearings"

    print(f"Connecting to {url} (db: {db}) to fix assets...")
    
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        if not uid:
            print("❌ Auth failed")
            return
            
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # 1. Find Asset Attachments
        # These are the compiled JS/CSS bundles
        domain = [
            ('name', 'ilike', 'web.assets_%'),
            ('type', '=', 'binary') # Only file-based assets
        ]
        
        asset_ids = models.execute_kw(db, uid, password, 'ir.attachment', 'search', [domain])
        
        if not asset_ids:
            print("No asset attachments found to delete. Typically this means they are already gone or filtered.")
            # Depending on permissions, maybe nothing found?
        else:
            print(f"Found {len(asset_ids)} asset attachments. Deleting to force regeneration...")
            models.execute_kw(db, uid, password, 'ir.attachment', 'unlink', [asset_ids])
            print("✅ Assets deleted.")
            
        print("\n✨ NOTE: Please refresh your browser (F5). The first load might take 5-10 seconds while Odoo rebuilds the cache.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
