import os
import sys
import json
import xmlrpc.client

# Add src to path
sys.path.append(os.getcwd())

def run():
    url = os.getenv("ODOO_URL", "http://localhost:8069")
    username = os.getenv("ODOO_USER", "admin")
    password = os.getenv("ODOO_PASSWORD", "admin")
    db = "bearings"
    
    json_path = "projects/odoo-bearings-config/data/state/enrichment_progress.json"

    print(f"Connecting to {url} (db: {db})...")
    
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object', allow_none=True)
        
        # Load Data
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} records. Calculating stock...")
        
        location_id = 8 # WH/Stock
        
        count = 0
        skipped = 0
        
        for code, record in data.items():
            # 1. Calculate Quantity
            qty = 0
            list_price = record.get('list_price', 0.0)
            sale_total = record.get('sale_total', 0.0)
            
            if list_price > 0:
                qty = int(round(sale_total / list_price))
            elif record.get('standard_cost', 0) > 0:
                 qty = int(round(record.get('cost_total', 0) / record.get('standard_cost', 0)))
            
            if qty <= 0:
                skipped += 1
                continue
                
            # 2. Find Product Variant ID (product.product)
            # We search by default_code (original_code)
            pids = models.execute_kw(db, uid, password, 'product.product', 'search', [[('default_code', '=', code)]])
            
            if not pids:
                print(f"Product not found: {code}")
                continue
                
            pid = pids[0]
            
            # 3. Update Stock
            # Method: Set inventory_quantity and apply
            # First, check if quant exists
            quants = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', 
                [[('product_id', '=', pid), ('location_id', '=', location_id)]], 
                {'fields': ['id']})
            
            if quants:
                quant_id = quants[0]['id']
                models.execute_kw(db, uid, password, 'stock.quant', 'write', [[quant_id], {'inventory_quantity': qty}])
            else:
                quant_id = models.execute_kw(db, uid, password, 'stock.quant', 'create', [{
                    'product_id': pid,
                    'location_id': location_id,
                    'inventory_quantity': qty
                }])
            
            # 4. Apply Inventory (Important feature in Odoo 15+)
            try:
                models.execute_kw(db, uid, password, 'stock.quant', 'action_apply_inventory', [[quant_id]])
                if count % 50 == 0:
                    print(f"Updated {code} -> Qty: {qty} (Total: {count})")
                count += 1
            except Exception as e:
                # Odoo returns None which crashes XML-RPC serializer, but the action succeeds.
                if "cannot marshal None" in str(e):
                     if count % 50 == 0:
                        print(f"Updated {code} (Ignored None Error) -> Qty: {qty} (Total: {count})")
                     count += 1
                else:
                    print(f"Failed to apply {code}: {e}")

        print(f"✅ Stock Update Complete. Updated: {count}, Skipped (Zero/NoData): {skipped}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
