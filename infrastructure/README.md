# Odoo AI Configurator - Infrastructure

## Complete Automated Setup

This directory contains everything needed to set up Odoo 18 from scratch.

## Quick Start (One Command)

```bash
cd odoo-ai-configurator
./scripts/complete_setup.sh
```

This will:
1. ✅ Setup Odoo 18 with Docker
2. ✅ Create clean database
3. ✅ Configure Bearings Inc
4. ✅ Install all modules

## Manual Steps

### 1. Setup Infrastructure

```bash
cd infrastructure
./setup.sh
```

This creates:
- Odoo 17 container
- PostgreSQL 15 container
- Persistent volumes

### 2. Manage Databases

```bash
# List databases
python3 scripts/manage_database.py list

# Create new database
python3 scripts/manage_database.py create --db mydb

# Drop database
python3 scripts/manage_database.py drop --db mydb

# Recreate (drop + create)
python3 scripts/manage_database.py recreate --db bearings
```

### 3. Configure Odoo

```bash
python3 scripts/configure_bearings_complete.py
```

## Files

```
infrastructure/
├── docker-compose.yml    # Odoo 17 + PostgreSQL
├── setup.sh             # Automated setup
└── README.md            # This file

scripts/
├── manage_database.py   # Database management
├── complete_setup.sh    # Full automation
├── create_database.py   # Simple DB creation
└── configure_bearings_complete.py  # Full config
```

## Docker Compose

The `docker-compose.yml` includes:
- **Odoo 18** (latest stable)
- **PostgreSQL 15**
- Persistent volumes
- Auto-restart

## Database Management

The `manage_database.py` tool provides:
- List all databases
- Create new databases
- Drop databases
- Recreate (clean start)

## Complete Automation

For AI agents or automated deployment:

```python
# Via MCP
server.handle_request({
    'tool': 'setup_infrastructure',
    'parameters': {
        'action': 'complete_setup'
    }
})
```

Or via bash:
```bash
./scripts/complete_setup.sh
```

## Troubleshooting

### Odoo not starting
```bash
docker logs odoo_web
```

### Database issues
```bash
# Recreate database
python3 scripts/manage_database.py recreate --db bearings
```

### Port already in use
```bash
# Stop existing Odoo
docker stop odoo_web odoo_db
```

## Next Steps

After setup:
1. Access http://localhost:8069
2. Login: admin / admin
3. Import products
4. Configure integrations
