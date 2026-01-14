#!/bin/bash
set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
IMAGE="gcr.io/${PROJECT_ID}/odoo-multitenant:latest"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Odoo Multi-Tenant Deployment ===${NC}"
echo ""

# Check if gcloud is configured
if ! gcloud config get-value project &>/dev/null; then
    echo "Error: gcloud not configured. Run: gcloud init"
    exit 1
fi

# Build and push image
echo -e "${GREEN}Building and pushing Docker image...${NC}"
gcloud builds submit --config cloudbuild.yaml .

# Deploy to Cloud Run (base service)
echo -e "${GREEN}Deploying base Odoo service...${NC}"
gcloud run deploy odoo-base \
    --image ${IMAGE} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars="DB_HOST=\${DB_HOST},DB_USER=\${DB_USER},DB_PASSWORD=\${DB_PASSWORD}" \
    --set-secrets="DB_PASSWORD=odoo-db-password:latest"

echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Base service URL:"
gcloud run services describe odoo-base --region ${REGION} --format 'value(status.url)'
