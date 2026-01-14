"""
Product Management Agent
"""
import csv
from typing import Any, Dict

from .base import OdooAgent


class ProductAgent(OdooAgent):
    """Manage products and inventory"""
    
    KEYWORDS = ['product', 'inventory', 'catalog', 'item']
    
    def can_handle(self, request: str) -> bool:
        request_lower = request.lower()
        return any(kw in request_lower for kw in self.KEYWORDS)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import or create products
        
        Params:
            file: CSV file path for import
            products: List of product dicts
            auto_publish: Publish to website (default: True)
        """
        if 'file' in params:
            return self._import_from_csv(params)
        elif 'products' in params:
            return self._create_products(params['products'], params.get('auto_publish', True))
        else:
            return {'status': 'error', 'message': 'No products or file specified'}
    
    def _import_from_csv(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import products from CSV"""
        file_path = params['file']
        auto_publish = params.get('auto_publish', True)
        
        self.log(f"Importing products from: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                products = list(reader)
            
            return self._create_products(products, auto_publish)
            
        except Exception as e:
            self.log(f"Error reading CSV: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _create_products(self, products: list, auto_publish: bool) -> Dict[str, Any]:
        """Create products in Odoo"""
        created = []
        failed = []
        
        for product in products:
            try:
                product_data = {
                    'name': product.get('name') or f"{product.get('Brand', '')} {product.get('SKU', '')}".strip(),
                    'default_code': product.get('SKU') or product.get('sku'),
                    'type': 'product',
                    'categ_id': 1,
                    'list_price': float(product.get('Price') or product.get('price') or 0),
                    'standard_price': float(product.get('Cost') or product.get('cost') or 0),
                    'description_sale': product.get('Marketplace_Description', '')[:500],
                    'description': product.get('Technical_Description', '')[:500],
                    'website_published': auto_publish,
                    'sale_ok': True,
                    'purchase_ok': True,
                }
                
                product_id = self.odoo.create('product.template', product_data)
                created.append(product_id)
                
                # Update stock if quantity provided
                qty = product.get('Quantity') or product.get('quantity')
                if qty and float(qty) > 0:
                    self.odoo.create('stock.quant', {
                        'product_id': product_id,
                        'location_id': 8,  # Stock location
                        'quantity': float(qty),
                    })
                
            except Exception as e:
                self.log(f"Error creating product: {str(e)}", "ERROR")
                failed.append(product.get('SKU', 'unknown'))
        
        self.log(f"Created {len(created)} products, {len(failed)} failed")
        
        return {
            'status': 'success' if created else 'error',
            'created': len(created),
            'failed': len(failed),
            'total': len(products)
        }
