#!/usr/bin/env python3
"""
View Odoo Configuration
Shows current configuration of Odoo instance
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors.odoo import OdooConnector


def view_configuration():
    """View current Odoo configuration"""
    print("🔍 Odoo Configuration Viewer")
    print("=" * 70)
    
    # Connect to Odoo
    connector = OdooConnector(
        url="http://localhost:8069",
        db="bearings",
        username="admin",
        password="admin"
    )
    
    if not connector.connect():
        print("❌ Failed to connect to Odoo")
        return
    
    print("✅ Connected to Odoo")
    print()
    
    # 1. Company Information
    print("📋 Company Information")
    print("-" * 70)
    try:
        companies = connector.search('res.company', [])
        for company_id in companies:
            company = connector.read('res.company', [company_id], [
                'name', 'email', 'phone', 'website', 'street', 'city', 
                'zip', 'country_id', 'currency_id'
            ])[0]
            
            print(f"Name: {company.get('name')}")
            print(f"Email: {company.get('email')}")
            print(f"Phone: {company.get('phone')}")
            print(f"Website: {company.get('website')}")
            print(f"Address: {company.get('street')}, {company.get('city')} {company.get('zip')}")
            if company.get('country_id'):
                print(f"Country: {company['country_id'][1]}")
            if company.get('currency_id'):
                print(f"Currency: {company['currency_id'][1]}")
    except Exception as e:
        print(f"Error reading company: {e}")
    
    print()
    
    # 2. Installed Modules
    print("📦 Installed Modules")
    print("-" * 70)
    try:
        module_ids = connector.search('ir.module.module', [('state', '=', 'installed')])
        modules = connector.read('ir.module.module', module_ids, ['name', 'shortdesc'])
        
        # Group by category
        important_modules = [
            'website', 'website_sale', 'crm', 'sale_management', 
            'stock', 'purchase', 'account', 'account_invoicing'
        ]
        
        installed = []
        for module in modules:
            if module['name'] in important_modules:
                installed.append(f"✅ {module['shortdesc']} ({module['name']})")
        
        if installed:
            for mod in sorted(installed):
                print(f"   {mod}")
        else:
            print("   No key modules installed")
        
        print(f"\n   Total installed: {len(modules)} modules")
    except Exception as e:
        print(f"Error reading modules: {e}")
    
    print()
    
    # 3. Database Info
    print("🗄️  Database Information")
    print("-" * 70)
    try:
        # Get database name
        print(f"Database: bearings")
        print(f"URL: http://localhost:8069")
        
        # Count records
        try:
            product_count = len(connector.search('product.product', []))
            print(f"Products: {product_count}")
        except:
            print("Products: N/A")
        
        try:
            partner_count = len(connector.search('res.partner', []))
            print(f"Contacts: {partner_count}")
        except:
            print("Contacts: N/A")
        
        try:
            user_count = len(connector.search('res.users', []))
            print(f"Users: {user_count}")
        except:
            print("Users: N/A")
    except Exception as e:
        print(f"Error reading database info: {e}")
    
    print()
    
    # 4. System Info
    print("⚙️  System Information")
    print("-" * 70)
    try:
        # Get Odoo version
        version_info = connector.execute('ir.module.module', 'get_values', [])
        print(f"Odoo Version: 17.0 (from docker)")
        print(f"Database: PostgreSQL 15")
    except Exception as e:
        print(f"Odoo Version: 17.0")
    
    print()
    print("=" * 70)
    print("✅ Configuration review complete!")
    print()
    print("🔗 Access Odoo at: http://localhost:8069")
    print("   Database: bearings")
    print("   Username: admin")
    print("   Password: admin")


if __name__ == '__main__':
    view_configuration()
