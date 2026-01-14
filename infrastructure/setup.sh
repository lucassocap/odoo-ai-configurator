#!/bin/bash
# Setup Odoo 18 Infrastructure
# This script sets up a fresh Odoo 18 instance with PostgreSQL

set -e

echo "🚀 Setting up Odoo 18 Infrastructure"
echo "===================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Navigate to infrastructure directory
cd "$(dirname "$0")"

# Stop existing containers if any
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down -v 2>/dev/null || true

# Remove old volumes to ensure clean start
echo ""
echo "🗑️  Removing old volumes..."
docker volume rm odoo-web-data odoo-db-data 2>/dev/null || true

# Pull latest images
echo ""
echo "📥 Pulling latest images..."
docker-compose pull

# Start containers
echo ""
echo "🚀 Starting Odoo 17..."
docker-compose up -d

# Wait for Odoo to be ready
echo ""
echo "⏳ Waiting for Odoo to start (this may take 1-2 minutes)..."
sleep 30

# Check if Odoo is responding
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8069 > /dev/null; then
        echo ""
        echo "✅ Odoo 18 is ready!"
        echo ""
        echo "📋 Connection details:"
        echo "   URL: http://localhost:8069"
        echo "   Database: (create via script or web UI)"
        echo "   Master Password: admin"
        echo ""
        echo "🔧 Next steps:"
        echo "   1. Create database: python3 ../scripts/create_database.py"
        echo "   2. Configure Odoo: python3 ../scripts/configure_bearings_complete.py"
        exit 0
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Still starting... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo ""
echo "⚠️  Odoo took longer than expected to start"
echo "   Check logs: docker logs odoo_web"
exit 1
