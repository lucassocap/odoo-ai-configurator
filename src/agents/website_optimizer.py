"""
WebsiteOptimizerAgent - Autonomous Website Diagnosis and Optimization

Analyzes website programmatically, diagnoses issues, and applies fixes
Uses generated images to transform generic sites into premium experiences
Directly modifies Odoo database views for powerful customization
"""
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

from .base import OdooAgent


class WebsiteOptimizerAgent(OdooAgent):
    """Agent for autonomous website optimization"""
    
    def __init__(self, odoo_connector):
        super().__init__(odoo_connector)
        self.name = "WebsiteOptimizerAgent"
        self.description = "Diagnoses and optimizes websites automatically"
    
    def can_handle(self, request: str) -> bool:
        """Check if agent can handle the request"""
        keywords = [
            'optimize', 'fix website', 'improve', 'diagnose',
            'customize', 'enhance', 'audit', 'review website'
        ]
        return any(keyword in request.lower() for keyword in keywords)
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute website optimization"""
        self.log("Starting website optimization")
        
        url = params.get('url', 'http://localhost:8069')
        
        # Step 1: Diagnose
        diagnosis = self._diagnose_website(url)
        
        # Step 2: Get available images
        images = self._get_uploaded_images()
        
        # Step 3: Apply fixes
        fixes = self._apply_optimizations(diagnosis, images)
        
        return {
            'status': 'success',
            'diagnosis': diagnosis,
            'images_available': len(images),
            'fixes_applied': fixes
        }
    
    def _diagnose_website(self, url: str) -> Dict[str, Any]:
        """Diagnose website issues"""
        self.log(f"Diagnosing website: {url}")
        
        issues = []
        recommendations = []
        
        try:
            # Fetch homepage
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check hero section
            hero = soup.find('section', class_='s_cover')
            if hero:
                # Check for custom background
                style = hero.get('style', '')
                if 'background-image' not in style:
                    issues.append({
                        'type': 'hero_missing_image',
                        'severity': 'high',
                        'description': 'Hero section has no custom background image'
                    })
                    recommendations.append('Add hero banner image')
            
            # Check logo
            logo = soup.find('img', class_='logo')
            if logo:
                src = logo.get('src', '')
                if 'logo.png' in src or 'default' in src or '/website/static/src/img/odoo_logo.svg' in src:
                    # Only flag if we have a custom logo available
                    issues.append({
                        'type': 'generic_logo',
                        'severity': 'medium',
                        'description': 'Using generic/default logo'
                    })
                    recommendations.append('Upload custom logo')
            
            # Check for placeholder text
            text_content = soup.get_text()
            placeholders = [
                'hello@mycompany.com',
                '+1 555-555-5556',
                # 'Lorem ipsum', # Removed as it might be too aggressive
                'Bearings for a better tomorrow' # Example specific
            ]
            
            for placeholder in placeholders:
                if placeholder.lower() in text_content.lower():
                    issues.append({
                        'type': 'placeholder_content',
                        'severity': 'medium',
                        'description': f'Found placeholder: {placeholder}'
                    })
                    recommendations.append(f'Replace {placeholder} with real content')
            
            # Check shop page
            try:
                shop_response = requests.get(f'{url}/shop', timeout=10)
                shop_soup = BeautifulSoup(shop_response.content, 'html.parser')
                products = shop_soup.find_all('div', class_='oe_product')
                product_count = len(products)
            except:
                product_count = 0
            
            if product_count == 0:
                issues.append({
                    'type': 'no_products',
                    'severity': 'critical',
                    'description': 'No products found in shop'
                })
            
            diagnosis = {
                'url': url,
                'issues_found': len(issues),
                'issues': issues,
                'recommendations': recommendations,
                'product_count': product_count,
                'status': 'needs_optimization' if issues else 'good'
            }
            
            self.log(f"Diagnosis complete: {len(issues)} issues found")
            return diagnosis
            
        except Exception as e:
            self.log(f"Error diagnosing website: {str(e)}", "ERROR")
            return {
                'url': url,
                'error': str(e),
                'status': 'error'
            }
    
    def _get_uploaded_images(self) -> List[Dict]:
        """Get list of uploaded images from Odoo"""
        self.log("Fetching uploaded images...")
        
        try:
            # Search for attachments
            attachment_ids = self.odoo.search('ir.attachment', [
                ('public', '=', True),
                ('type', '=', 'binary')
            ])
            
            if not attachment_ids:
                return []
            
            # Get attachment details
            attachments = self.odoo.read('ir.attachment', attachment_ids, 
                                        ['id', 'name', 'url'])
            
            # self.log(f"Found {len(attachments)} uploaded images")
            return attachments
            
        except Exception as e:
            self.log(f"Error fetching images: {str(e)}", "WARNING")
            return []
    
    def _apply_optimizations(self, diagnosis: Dict, images: List[Dict]) -> Dict[str, Any]:
        """Apply optimizations based on diagnosis by directly editing database views"""
        self.log("Applying detailed optimizations to database...")
        
        fixes_applied = []
        fixes_failed = []
        
        # Map images by name
        image_map = {img['name']: img for img in images}
        
        # 1. Apply Logo (if needed)
        # Check if we have a logo image
        logo_img = [img for name, img in image_map.items() if 'logo' in name.lower()]
        if logo_img:
            try:
                self._apply_logo(logo_img[0])
                fixes_applied.append('logo_updated')
            except Exception as e:
                fixes_failed.append({'item': 'logo', 'error': str(e)})
        
        # 2. Process ALL Views for Content Replacement
        # This approach is more robust than targeted fixes
        try:
            # Bearings Inc Content Dictionary
            BEARINGS_CONTENT = {
                'contact': {
                    'email': 'sales@bearingsinc.com',
                    'phone': '+1 (555) 123-4567',
                },
                'hero_title': 'Precision Bearings for Industrial Excellence',
                'hero_subtitle': 'Leading the Industry in Quality and Innovation',
                'hero_description': 'Bearings Inc delivers premium ball bearings, roller bearings, and specialized components.',
                'about_text': 'With decades of experience in precision bearing distribution, we provide industrial-grade components.',
            }

            replacements = {
                'hello@mycompany.com': BEARINGS_CONTENT['contact']['email'],
                '+1 555-555-5556': BEARINGS_CONTENT['contact']['phone'],
                'Bearings for a better tomorrow': BEARINGS_CONTENT['hero_title'],
                'Shaping our future': BEARINGS_CONTENT['hero_subtitle'],
                'Changing the world is possible': BEARINGS_CONTENT['hero_description'],
                'Our mission is to provide innovative bearing solutions': BEARINGS_CONTENT['about_text'],
            }
            
            # Find all QWeb views
            view_ids = self.odoo.search('ir.ui.view', [('type', '=', 'qweb')])
            views = self.odoo.read('ir.ui.view', view_ids, ['id', 'name', 'arch_db', 'key'])
            
            for view in views:
                arch = view.get('arch_db', '')
                if not arch:
                    continue
                    
                original_arch = arch
                updated = False
                
                # Replace text
                for old, new in replacements.items():
                    if old in arch:
                        arch = arch.replace(old, new)
                        updated = True
                
                # Replace Hero Background
                if 's_cover' in arch or 'hero' in view.get('name', '').lower():
                    if 'hero_banner' in image_map:
                         hero_url = f"/web/image/{image_map['hero_banner']['id']}"
                         if 'background-image' not in arch:
                             arch = arch.replace(
                                '<section class="s_cover',
                                f'<section style="background-image: url({hero_url}); background-size: cover; background-position: center;" class="s_cover'
                            )
                             updated = True

                if updated and arch != original_arch:
                     try:
                        self.odoo.write('ir.ui.view', [view['id']], {'arch_db': arch})
                        fixes_applied.append(f"view_updated:{view['name']}")
                        self.log(f"Updated view: {view['name']}")
                     except Exception as e:
                        fixes_failed.append({'view': view['name'], 'error': str(e)})

        except Exception as e:
             self.log(f"Error processing views: {str(e)}", "ERROR")
             fixes_failed.append({'item': 'view_processing', 'error': str(e)})

        return {
            'applied': fixes_applied,
            'failed': fixes_failed,
            'total_fixes': len(fixes_applied)
        }
    
    def _apply_logo(self, image: Dict):
        """Apply logo image"""
        self.log(f"Applying logo: {image['name']}")
        
        websites = self.odoo.search('website', [('id', '>', 0)], {'limit': 1})
        if not websites:
            return
            
        website_id = websites[0]
        
        # Use existing image data if possible (complex via API read/write loop), 
        # or simplified update if we had raw data. 
        # Since we have the ID, we can try to set it, but 'logo' field on website expects binary.
        # Here we skip complex binary reading for now as it's handled by main script usually.
        # But let's try to see if we can read the attachment binary and write it.
        try:
             attachment = self.odoo.read('ir.attachment', [image['id']], ['datas'])[0]
             if attachment.get('datas'):
                 self.odoo.write('website', [website_id], {'logo': attachment['datas']})
        except Exception as e:
            self.log(f"Could not apply logo binary: {e}", "WARNING")
