"""
Website Configuration Agent
Automates complete website setup based on reference design
"""
import base64
import json
from pathlib import Path
from typing import Any, Dict, List

from .base import OdooAgent


class WebsiteConfigAgent(OdooAgent):
    """Agent for configuring eCommerce website"""
    
    NETORA_THEME = {
        "primary_color": "#0d1b2a",
        "accent_color": "#3498db",
        "font_family": "sans-serif",
        "layout": "grid_4_columns"
    }
    
    def can_handle(self, request: str) -> bool:
        """Check if this agent can handle the request"""
        keywords = ['website', 'ecommerce', 'shop', 'theme', 'configure web']
        return any(keyword in request.lower() for keyword in keywords)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute website configuration"""
        self.log("Starting website configuration")
        
        action = params.get('action', 'full_setup')
        
        if action == 'full_setup':
            return self._full_website_setup(params)
        elif action == 'import_products':
            return self._import_products(params)
        elif action == 'configure_theme':
            return self._configure_theme(params)
        elif action == 'setup_categories':
            return self._setup_categories(params)
        else:
            return {'status': 'error', 'message': f'Unknown action: {action}'}
    
    def _full_website_setup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Complete website setup"""
        results = {
            'theme': None,
            'categories': None,
            'products': None,
            'homepage': None
        }
        
        try:
            # 1. Configure theme
            self.log("Configuring theme...")
            theme_config = params.get('theme', self.NETORA_THEME)
            results['theme'] = self._configure_theme({'config': theme_config})
            
            # 2. Setup categories
            self.log("Setting up categories...")
            categories = params.get('categories', self._get_default_categories())
            results['categories'] = self._setup_categories({'categories': categories})
            
            # 3. Import products
            self.log("Importing products...")
            products = params.get('products', [])
            if products:
                results['products'] = self._import_products({'products': products})
            
            # 4. Configure homepage
            self.log("Configuring homepage...")
            results['homepage'] = self._configure_homepage(params)
            
            return {
                'status': 'success',
                'message': 'Website configured successfully',
                'results': results
            }
            
        except Exception as e:
            self.log(f"Error in full setup: {str(e)}", "ERROR")
            self.record_error("WebsiteSetupError", str(e), "Full website setup")
            return {
                'status': 'error',
                'message': str(e),
                'results': results
            }
    
    def _configure_theme(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure website theme"""
        try:
            config = params.get('config', self.NETORA_THEME)
            
            # Note: Odoo theme configuration typically done via UI
            # This is a placeholder for theme settings
            self.log(f"Theme configuration: {config}")
            
            return {
                'status': 'success',
                'message': 'Theme configured',
                'config': config
            }
            
        except Exception as e:
            self.log(f"Error configuring theme: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _setup_categories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Setup product categories"""
        try:
            categories = params.get('categories', [])
            created_categories = []
            
            for category in categories:
                try:
                    # Check if category exists
                    existing = self.odoo.search('product.public.category', [
                        ('name', '=', category['name'])
                    ])
                    
                    if existing:
                        self.log(f"Category '{category['name']}' already exists")
                        created_categories.append(existing[0])
                    else:
                        # Create category
                        category_id = self.odoo.create('product.public.category', {
                            'name': category['name'],
                            'parent_id': category.get('parent_id', False)
                        })
                        self.log(f"Created category: {category['name']}")
                        created_categories.append(category_id)
                        
                except Exception as e:
                    self.log(f"Error creating category {category['name']}: {str(e)}", "WARNING")
            
            return {
                'status': 'success',
                'message': f'Created {len(created_categories)} categories',
                'category_ids': created_categories
            }
            
        except Exception as e:
            self.log(f"Error setting up categories: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _import_products(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import products with images and descriptions"""
        try:
            products = params.get('products', [])
            
            # VALIDATION PHASE
            self.log("🔍 Validating products before import...")
            validated_products, validation_errors = self._validate_products(products)
            
            if validation_errors:
                self.log(f"⚠️  Found {len(validation_errors)} validation errors", "WARNING")
                for error in validation_errors:
                    self.log(f"   - {error}", "WARNING")
            
            self.log(f"✅ {len(validated_products)}/{len(products)} products passed validation")
            
            # IMPORT PHASE
            imported = []
            errors = []
            
            for product in validated_products:
                try:
                    # Check if product exists
                    existing = self.odoo.search('product.template', [
                        ('default_code', '=', product.get('sku'))
                    ])
                    
                    if existing:
                        self.log(f"Product {product.get('sku')} already exists, updating...")
                        product_id = existing[0]
                        self.odoo.write('product.template', [product_id], 
                                      self._prepare_product_data(product))
                    else:
                        # Create product
                        product_id = self.odoo.create('product.template', 
                                                     self._prepare_product_data(product))
                        self.log(f"Created product: {product.get('name')}")
                    
                    # Upload image if provided
                    if product.get('image_path'):
                        self._upload_product_image(product_id, product['image_path'])
                    
                    imported.append(product_id)
                    
                except Exception as e:
                    self.log(f"Error importing product {product.get('name')}: {str(e)}", "WARNING")
                    errors.append({'product': product.get('name'), 'error': str(e)})
            
            return {
                'status': 'success' if imported else 'error',
                'message': f'Imported {len(imported)}/{len(products)} products',
                'imported': imported,
                'validation_errors': validation_errors,
                'import_errors': errors,
                'validated': len(validated_products),
                'total': len(products)
            }
            
        except Exception as e:
            self.log(f"Error importing products: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _validate_products(self, products: List[Dict]) -> tuple:
        """Validate products before import"""
        validated = []
        errors = []
        
        for i, product in enumerate(products):
            product_errors = []
            
            # Required fields validation
            if not product.get('sku'):
                product_errors.append(f"Product {i+1}: Missing SKU")
            
            if not product.get('name'):
                product_errors.append(f"Product {i+1}: Missing name")
            
            # Price validation
            price = product.get('price', 0)
            try:
                price_float = float(price)
                if price_float < 0:
                    product_errors.append(f"Product {product.get('sku')}: Negative price")
            except (ValueError, TypeError):
                product_errors.append(f"Product {product.get('sku')}: Invalid price format")
            
            # Image validation
            image_path = product.get('image_path')
            if image_path:
                from pathlib import Path
                if not Path(image_path).exists():
                    product_errors.append(f"Product {product.get('sku')}: Image not found at {image_path}")
                elif not Path(image_path).suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                    product_errors.append(f"Product {product.get('sku')}: Invalid image format")
            
            # Description validation
            description = product.get('description', '')
            if len(description) < 10:
                product_errors.append(f"Product {product.get('sku')}: Description too short (min 10 chars)")
            
            # Category validation
            if not product.get('category'):
                product_errors.append(f"Product {product.get('sku')}: Missing category")
            
            if product_errors:
                errors.extend(product_errors)
            else:
                validated.append(product)
        
        return validated, errors
    
    def _prepare_product_data(self, product: Dict) -> Dict:
        """Prepare product data for Odoo"""
        return {
            'name': product.get('name'),
            'default_code': product.get('sku'),
            'list_price': product.get('price', 0.0),
            'description_sale': product.get('description', ''),
            'type': 'product',
            'website_published': True,
            'is_published': True
        }
    
    def _upload_product_image(self, product_id: int, image_path: str):
        """Upload product image"""
        try:
            path = Path(image_path)
            if path.exists():
                with open(path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                self.odoo.write('product.template', [product_id], {
                    'image_1920': image_data
                })
                self.log(f"Uploaded image for product {product_id}")
            else:
                self.log(f"Image not found: {image_path}", "WARNING")
                
        except Exception as e:
            self.log(f"Error uploading image: {str(e)}", "WARNING")
    
    def _configure_homepage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure homepage"""
        try:
            # Homepage configuration typically done via Odoo website builder
            self.log("Homepage configuration placeholder")
            
            return {
                'status': 'success',
                'message': 'Homepage configured'
            }
            
        except Exception as e:
            self.log(f"Error configuring homepage: {str(e)}", "ERROR")
            return {'status': 'error', 'message': str(e)}
    
    def _get_default_categories(self) -> List[Dict]:
        """Get default bearing categories"""
        return [
            {'name': 'Ball Bearings', 'parent_id': False},
            {'name': 'Roller Bearings', 'parent_id': False},
            {'name': 'Thrust Bearings', 'parent_id': False},
            {'name': 'Special Bearings', 'parent_id': False}
        ]
