FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create odoo user
RUN useradd -ms /bin/bash odoo

# Set working directory
WORKDIR /opt/odoo

# Copy Odoo source
COPY odoo-source /opt/odoo

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set permissions
RUN chown -R odoo:odoo /opt/odoo

# Switch to odoo user
USER odoo

# Expose port
EXPOSE 8069

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8069/web/health || exit 1

# Start Odoo
CMD ["python3", "odoo-bin", "--db_host=${DB_HOST}", "--db_port=5432", "--db_user=${DB_USER}", "--db_password=${DB_PASSWORD}"]
