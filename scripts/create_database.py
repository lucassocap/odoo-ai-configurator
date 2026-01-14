#!/usr/bin/env python3
"""
Create Odoo Database via API (without frontend)
"""
import sys
import xmlrpc.client

ODOO_URL = 'http://localhost:8069'
MASTER_PASSWORD = 'admin'  # Default Odoo master password
DB_NAME = 'bearings'
ADMIN_PASSWORD = 'admin'
LANG = 'en_US'
COUNTRY_CODE = 'us'

def create_database():
    """Create Odoo database via XML-RPC"""
    print(f"🔧 Creating Odoo database: {DB_NAME}")
    print("=" * 60)
    
    try:
        # Connect to database management service
        db = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        # Create database
        print(f"\n📦 Creating database '{DB_NAME}'...")
        print("   This may take a few minutes...")
        
        result = db.create_database(
            MASTER_PASSWORD,
            DB_NAME,
            True,  # demo data
            LANG,
            ADMIN_PASSWORD,
            ADMIN_PASSWORD,  # confirm password
            COUNTRY_CODE
        )
        
        if result:
            print(f"\n✅ Database '{DB_NAME}' created successfully!")
            print(f"\n📋 Connection details:")
            print(f"   URL: {ODOO_URL}")
            print(f"   Database: {DB_NAME}")
            print(f"   Username: admin")
            print(f"   Password: {ADMIN_PASSWORD}")
            return True
        else:
            print(f"\n❌ Failed to create database")
            return False
            
    except xmlrpc.client.Fault as e:
        if 'already exists' in str(e):
            print(f"\n✅ Database '{DB_NAME}' already exists!")
            return True
        else:
            print(f"\n❌ Error: {e}")
            return False
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Odoo is running: docker ps")
        print("2. Check Odoo is accessible: curl http://localhost:8069")
        print("3. Verify master password in odoo.conf")
        return False

if __name__ == '__main__':
    success = create_database()
    sys.exit(0 if success else 1)
