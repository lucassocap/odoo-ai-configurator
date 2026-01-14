# Odoo Multi-Tenant System on Google Cloud

Complete multi-tenant Odoo deployment system with automated client provisioning and management.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Google Cloud Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Cloud Run    │  │ Cloud Run    │  │ Cloud Run    │      │
│  │ Client A     │  │ Client B     │  │ Client C     │ ...  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         └──────────────────┼──────────────────┘              │
│                            │                                  │
│                   ┌────────▼────────┐                        │
│                   │   Cloud SQL     │                        │
│                   │   PostgreSQL    │                        │
│                   │  (Multi-DB)     │                        │
│                   └─────────────────┘                        │
│                                                               │
│         ┌──────────────────────────────────────┐            │
│         │      Cloud Storage Buckets            │            │
│         │  (One per client for file storage)    │            │
│         └──────────────────────────────────────┘            │
│                                                               │
│         ┌──────────────────────────────────────┐            │
│         │         Cloud Build (CI/CD)           │            │
│         └──────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Features

- ✅ **Complete Isolation**: Each client has dedicated database and storage
- ✅ **Auto-Scaling**: Cloud Run scales from 0 to handle traffic
- ✅ **Fast Deployment**: New clients in < 5 minutes
- ✅ **Cost-Effective**: Pay only for what you use
- ✅ **High Availability**: Built on Google Cloud infrastructure
- ✅ **Automated Backups**: Daily SQL backups with 7-day retention
- ✅ **CI/CD Pipeline**: Automated builds and deployments

## Quick Start

### 1. Prerequisites

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
```

### 2. Setup Infrastructure

```bash
# Make scripts executable
chmod +x *.sh

# Setup Google Cloud infrastructure
./setup_infrastructure.sh
```

This creates:
- Cloud SQL PostgreSQL instance
- Secret Manager for credentials
- Storage buckets
- IAM permissions

### 3. Deploy Base Odoo Image

```bash
./deploy.sh
```

This:
- Builds Docker image from Odoo source
- Pushes to Container Registry
- Deploys base Cloud Run service

### 4. Create Your First Client

```bash
./create_client.sh acme-corp
```

This automatically:
- Creates dedicated PostgreSQL database
- Creates Cloud Storage bucket
- Deploys Cloud Run service
- Returns access URL

## Managing Clients

### Create New Client

```bash
./create_client.sh <client-name>

# Example
./create_client.sh widgets-inc
```

### List All Clients

```bash
ls -1 clients/*.json | xargs -I {} basename {} .json
```

### View Client Details

```bash
cat clients/<client-name>.json
```

### Delete Client

```bash
./delete_client.sh <client-name>
```

⚠️ This permanently deletes all client data!

## Deployment Workflow

### Update Odoo Version

```bash
# Pull latest Odoo
cd odoo-source
git pull origin 17.0

# Rebuild and deploy
cd ..
./deploy.sh
```

### Update Existing Client

```bash
# Clients automatically use latest image on restart
gcloud run services update <client-name>-odoo --region us-central1
```

## Configuration

### Environment Variables

Create `.env` file:

```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export SQL_INSTANCE="odoo-postgres"
```

Source it:
```bash
source .env
```

### Scaling Configuration

Edit `create_client.sh` to adjust:
- `--memory`: RAM per instance (default: 2Gi)
- `--cpu`: vCPUs per instance (default: 2)
- `--min-instances`: Minimum instances (default: 0)
- `--max-instances`: Maximum instances (default: 5)

### Database Configuration

Edit `setup_infrastructure.sh` to adjust:
- `SQL_TIER`: Instance size (default: db-custom-2-7680)
- Backup retention
- Connection limits

## Cost Estimation

### Per Client (Monthly)

- **Cloud Run**: ~$10-50 (depends on traffic)
- **Cloud SQL**: Shared across all clients (~$100-200/month)
- **Cloud Storage**: ~$1-5 per client
- **Networking**: ~$5-20

**Total for 10 clients**: ~$250-400/month
**Total for 100 clients**: ~$1,500-3,000/month

### Cost Optimization

- Cloud Run scales to zero when idle
- Use committed use discounts for SQL
- Enable lifecycle policies for old files
- Use preemptible instances for non-critical workloads

## Monitoring

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read <client-name>-odoo --region us-central1

# SQL logs
gcloud sql operations list --instance odoo-postgres
```

### Metrics

```bash
# Service metrics
gcloud run services describe <client-name>-odoo --region us-central1
```

## Backup & Recovery

### Automated Backups

- SQL: Daily at 3:00 AM UTC (7-day retention)
- Configured in `setup_infrastructure.sh`

### Manual Backup

```bash
gcloud sql backups create \
  --instance odoo-postgres \
  --description "Manual backup $(date +%Y%m%d)"
```

### Restore from Backup

```bash
# List backups
gcloud sql backups list --instance odoo-postgres

# Restore
gcloud sql backups restore BACKUP_ID \
  --backup-instance odoo-postgres \
  --backup-id BACKUP_ID
```

## Security

### Best Practices

- ✅ Passwords stored in Secret Manager
- ✅ No public IPs on SQL instance
- ✅ Cloud Run uses service accounts
- ✅ HTTPS enforced on all services
- ✅ Database-level isolation

### Additional Security

```bash
# Enable VPC Service Controls
gcloud access-context-manager perimeters create odoo-perimeter

# Enable Cloud Armor for DDoS protection
gcloud compute security-policies create odoo-policy
```

## Troubleshooting

### Client Won't Start

```bash
# Check logs
gcloud run services logs read <client-name>-odoo --region us-central1 --limit 50

# Check service status
gcloud run services describe <client-name>-odoo --region us-central1
```

### Database Connection Issues

```bash
# Test SQL connection
gcloud sql connect odoo-postgres --user=odoo

# Check Cloud SQL proxy
gcloud sql instances describe odoo-postgres
```

### Build Failures

```bash
# Check Cloud Build logs
gcloud builds list --limit 5

# View specific build
gcloud builds log BUILD_ID
```

## Advanced Features

### Custom Domains

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service <client-name>-odoo \
  --domain client.yourdomain.com \
  --region us-central1
```

### Load Balancer Setup

```bash
# Create load balancer for multiple regions
gcloud compute url-maps create odoo-lb
gcloud compute target-http-proxies create odoo-proxy
gcloud compute forwarding-rules create odoo-rule
```

### Monitoring Dashboard

```bash
# Create monitoring dashboard
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

## Support

### Common Issues

1. **Out of memory**: Increase `--memory` in create_client.sh
2. **Slow performance**: Increase SQL tier or add read replicas
3. **Connection limits**: Increase max_connections in SQL flags

### Getting Help

- Check logs first
- Review Google Cloud documentation
- Contact support with client name and error logs

## License

This deployment system is provided as-is. Odoo Community Edition is licensed under LGPL v3.

## Credits

- Odoo Community Edition: https://github.com/odoo/odoo
- Google Cloud Platform
