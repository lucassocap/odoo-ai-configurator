#!/bin/bash
set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <client-name>"
    exit 1
fi

CLIENT_NAME=$1
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
SQL_INSTANCE=${SQL_INSTANCE:-"odoo-postgres"}

echo "⚠️  WARNING: This will delete all data for client: ${CLIENT_NAME}"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

echo "Deleting client ${CLIENT_NAME}..."

# Delete Cloud Run service
echo "[1/3] Deleting Cloud Run service..."
gcloud run services delete ${CLIENT_NAME}-odoo --region ${REGION} --quiet || true

# Delete database
echo "[2/3] Deleting database..."
gcloud sql databases delete ${CLIENT_NAME//-/_} --instance=${SQL_INSTANCE} --quiet || true

# Delete storage bucket
echo "[3/3] Deleting storage bucket..."
gsutil -m rm -r gs://${PROJECT_ID}-${CLIENT_NAME}-files/ || true

# Remove client config
rm -f clients/${CLIENT_NAME}.json

echo "✅ Client ${CLIENT_NAME} deleted successfully"
