# Data Directory

This directory is intended to store data files used for Odoo configuration and seeding.

## Supported Formats
- **JSON**: For structured product imports, partner data, etc.
- **CSV**: For bulk import of standard Odoo models.
- **XML**: For standard Odoo data files (if needed by agents).

## Usage
Agents (like `ProductAgent` or `CompanyAgent`) can look in this directory for default data or user-provided files to populate the Odoo instance during setup.

**Note**: Client-specific data should NOT be committed here. Use this folder only for:
1. Example datasets (e.g., `examples/`)
2. Framework-level seed data
3. Temporary file storage during execution
