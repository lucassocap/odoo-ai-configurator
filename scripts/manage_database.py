#!/usr/bin/env python3
"""
Database Management Tool
Clean, recreate, or manage Odoo databases
"""
import argparse
import sys
import xmlrpc.client

ODOO_URL = 'http://localhost:8069'
MASTER_PASSWORD = 'admin'

def list_databases():
    """List all databases"""
    try:
        db = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        databases = db.list()
        
        print("📋 Available databases:")
        if databases:
            for db_name in databases:
                print(f"   - {db_name}")
        else:
            print("   (no databases)")
        
        return databases
    except Exception as e:
        print(f"❌ Error listing databases: {e}")
        return []

def drop_database(db_name):
    """Drop a database"""
    try:
        db = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        print(f"🗑️  Dropping database '{db_name}'...")
        db.drop(MASTER_PASSWORD, db_name)
        print(f"✅ Database '{db_name}' dropped successfully")
        return True
    except Exception as e:
        print(f"❌ Error dropping database: {e}")
        return False

def create_database(db_name, demo_data=True):
    """Create a new database"""
    try:
        db = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/db')
        
        print(f"📦 Creating database '{db_name}'...")
        print("   This may take a few minutes...")
        
        result = db.create_database(
            MASTER_PASSWORD,
            db_name,
            demo_data,
            'en_US',
            'admin',
            'admin',
            'us'
        )
        
        if result:
            print(f"✅ Database '{db_name}' created successfully!")
            print(f"\n📋 Connection details:")
            print(f"   URL: {ODOO_URL}")
            print(f"   Database: {db_name}")
            print(f"   Username: admin")
            print(f"   Password: admin")
            return True
        else:
            print(f"❌ Failed to create database")
            return False
    except Exception as e:
        if 'already exists' in str(e):
            print(f"⚠️  Database '{db_name}' already exists")
            return True
        else:
            print(f"❌ Error creating database: {e}")
            return False

def recreate_database(db_name):
    """Drop and recreate a database"""
    print(f"🔄 Recreating database '{db_name}'...")
    
    # Drop if exists
    drop_database(db_name)
    
    # Create new
    return create_database(db_name, demo_data=False)

def main():
    parser = argparse.ArgumentParser(description='Odoo Database Management')
    parser.add_argument('action', choices=['list', 'create', 'drop', 'recreate'],
                       help='Action to perform')
    parser.add_argument('--db', help='Database name')
    parser.add_argument('--demo', action='store_true', help='Include demo data')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_databases()
    
    elif args.action == 'create':
        if not args.db:
            print("❌ Database name required (--db)")
            sys.exit(1)
        create_database(args.db, args.demo)
    
    elif args.action == 'drop':
        if not args.db:
            print("❌ Database name required (--db)")
            sys.exit(1)
        drop_database(args.db)
    
    elif args.action == 'recreate':
        if not args.db:
            print("❌ Database name required (--db)")
            sys.exit(1)
        recreate_database(args.db)

if __name__ == '__main__':
    main()
