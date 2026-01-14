#!/bin/bash
set -e

# Check arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <client-name>"
    echo "Example: $0 acme-corp"
    exit 1
fi

CLIENT_NAME=$1
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
SQL_INSTANCE=${SQL_INSTANCE:-"odoo-postgres"}
IMAGE="gcr.io/${PROJECT_ID}/odoo-multitenant:latest"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Creating New Odoo Client: ${CLIENT_NAME} ===${NC}"
echo ""

# Validate client name (alphanumeric and hyphens only)
if ! [[ "$CLIENT_NAME" =~ ^[a-z0-9-]+$ ]]; then
    echo "Error: Client name must contain only lowercase letters, numbers, and hyphens"
    exit 1
fi

# 1. Create database
echo -e "${GREEN}[1/5] Creating PostgreSQL database...${NC}"
gcloud sql databases create ${CLIENT_NAME//-/_} \
    --instance=${SQL_INSTANCE} \
    || echo -e "${YELLOW}Database may already exist${NC}"

# 2. Create Cloud Storage bucket for client files
echo -e "${GREEN}[2/5] Creating Cloud Storage bucket...${NC}"
gsutil mb -p ${PROJECT_ID} -l ${REGION} gs://${PROJECT_ID}-${CLIENT_NAME}-files/ \
    || echo -e "${YELLOW}Bucket may already exist${NC}"

# 3. Deploy Cloud Run service for client
echo -e "${GREEN}[3/5] Deploying Cloud Run service...${NC}"
gcloud run deploy ${CLIENT_NAME}-odoo \
    --image ${IMAGE} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 0 \
    --max-instances 5 \
    --set-env-vars="DB_HOST=/cloudsql/${PROJECT_ID}:${REGION}:${SQL_INSTANCE},DB_NAME=${CLIENT_NAME//-/_},DB_USER=odoo,CLIENT_NAME=${CLIENT_NAME},STORAGE_BUCKET=${PROJECT_ID}-${CLIENT_NAME}-files" \
    --set-secrets="DB_PASSWORD=odoo-db-password:latest" \
    --add-cloudsql-instances=${PROJECT_ID}:${REGION}:${SQL_INSTANCE}

# 4. Get service URL
SERVICE_URL=$(gcloud run services describe ${CLIENT_NAME}-odoo --region ${REGION} --format 'value(status.url)')

# 5. Configure domain mapping (optional)
echo -e "${GREEN}[4/5] Service deployed successfully${NC}"
echo ""
echo -e "${BLUE}Client Details:${NC}"
echo "  Name: ${CLIENT_NAME}"
echo "  Database: ${CLIENT_NAME//-/_}"
echo "  Service URL: ${SERVICE_URL}"
echo "  Storage Bucket: gs://${PROJECT_ID}-${CLIENT_NAME}-files/"
echo ""

# 6. Save client info
echo -e "${GREEN}[5/5] Saving client configuration...${NC}"
mkdir -p clients
cat > clients/${CLIENT_NAME}.json <<EOF
{
  "name": "${CLIENT_NAME}",
  "database": "${CLIENT_NAME//-/_}",
  "service_url": "${SERVICE_URL}",
  "storage_bucket": "${PROJECT_ID}-${CLIENT_NAME}-files",
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "region": "${REGION}"
}
EOF

echo -e "${GREEN}✅ Client ${CLIENT_NAME} created successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Access Odoo at: ${SERVICE_URL}"
echo "2. Complete initial setup wizard"
echo "3. Configure domain mapping if needed"
echo ""
echo "To delete this client, run: ./delete_client.sh ${CLIENT_NAME}"
