#!/bin/bash
set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"your-project-id"}
REGION=${GCP_REGION:-"us-central1"}
SQL_INSTANCE_NAME="odoo-postgres"
SQL_TIER="db-custom-2-7680"  # 2 vCPUs, 7.5GB RAM

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Setting Up Google Cloud Infrastructure ===${NC}"
echo ""

# Enable required APIs
echo -e "${GREEN}[1/7] Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    dns.googleapis.com \
    storage.googleapis.com

# Create Cloud SQL instance
echo -e "${GREEN}[2/7] Creating Cloud SQL PostgreSQL instance...${NC}"
gcloud sql instances create ${SQL_INSTANCE_NAME} \
    --database-version=POSTGRES_14 \
    --tier=${SQL_TIER} \
    --region=${REGION} \
    --network=default \
    --no-assign-ip \
    --database-flags=max_connections=200 \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --retained-backups-count=7 \
    || echo -e "${YELLOW}SQL instance may already exist${NC}"

# Set root password
echo -e "${GREEN}[3/7] Setting database password...${NC}"
DB_PASSWORD=$(openssl rand -base64 32)
gcloud sql users set-password postgres \
    --instance=${SQL_INSTANCE_NAME} \
    --password=${DB_PASSWORD}

# Create odoo user
echo -e "${GREEN}[4/7] Creating Odoo database user...${NC}"
gcloud sql users create odoo \
    --instance=${SQL_INSTANCE_NAME} \
    --password=${DB_PASSWORD} \
    || echo -e "${YELLOW}User may already exist${NC}"

# Store password in Secret Manager
echo -e "${GREEN}[5/7] Storing credentials in Secret Manager...${NC}"
echo -n ${DB_PASSWORD} | gcloud secrets create odoo-db-password \
    --data-file=- \
    --replication-policy="automatic" \
    || gcloud secrets versions add odoo-db-password --data-file=- <<< ${DB_PASSWORD}

# Create main storage bucket
echo -e "${GREEN}[6/7] Creating main storage bucket...${NC}"
gsutil mb -p ${PROJECT_ID} -l ${REGION} gs://${PROJECT_ID}-odoo-main/ \
    || echo -e "${YELLOW}Bucket may already exist${NC}"

# Set up IAM permissions
echo -e "${GREEN}[7/7] Configuring IAM permissions...${NC}"
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding odoo-db-password \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

echo ""
echo -e "${GREEN}✅ Infrastructure setup complete!${NC}"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo "  Project ID: ${PROJECT_ID}"
echo "  Region: ${REGION}"
echo "  SQL Instance: ${SQL_INSTANCE_NAME}"
echo "  Database User: odoo"
echo "  Secret: odoo-db-password"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run: ./deploy.sh to deploy base Odoo image"
echo "2. Run: ./create_client.sh <client-name> to create first client"
echo ""
echo -e "${YELLOW}Save these for your .env file:${NC}"
echo "export GCP_PROJECT_ID=\"${PROJECT_ID}\""
echo "export GCP_REGION=\"${REGION}\""
echo "export SQL_INSTANCE=\"${SQL_INSTANCE_NAME}\""
