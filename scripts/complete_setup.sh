#!/bin/bash
# Complete Setup - From Zero to Configured Odoo
# This script does EVERYTHING automatically

set -e

echo "🚀 Complete Odoo Setup - Automated"
echo "===================================="
echo ""

# Step 1: Setup infrastructure
echo "📦 Step 1/4: Setting up Odoo 17 infrastructure..."
cd infrastructure
./setup.sh
cd ..

echo ""
echo "✅ Infrastructure ready!"
echo ""

# Step 2: Create database
echo "📦 Step 2/4: Creating database..."
python3 scripts/manage_database.py recreate --db bearings

echo ""
echo "✅ Database created!"
echo ""

# Step 3: Configure Odoo
echo "📦 Step 3/4: Configuring Bearings Inc..."
python3 scripts/configure_bearings_complete.py

echo ""
echo "✅ Configuration complete!"
echo ""

# Step 4: Summary
echo "======================================"
echo "✅ SETUP COMPLETE!"
echo "======================================"
echo ""
echo "📋 Your Odoo instance is ready:"
echo "   URL: http://localhost:8069"
echo "   Database: bearings"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "🎯 What was configured:"
echo "   ✅ Odoo 17 running"
echo "   ✅ Database created"
echo "   ✅ Company: Bearings Inc"
echo "   ✅ Modules: Website, eCommerce, CRM, Sales"
echo ""
echo "🔗 Next steps:"
echo "   1. Access: http://localhost:8069"
echo "   2. Import products (if needed)"
echo "   3. Configure integrations"
echo ""
