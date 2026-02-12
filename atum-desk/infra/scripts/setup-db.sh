#!/bin/bash
# ATUM DESK Database Setup Script
# Creates database, user, and extensions

set -e

echo "========================================="
echo "ATUM DESK - Database Setup"
echo "========================================="

# Configuration
DB_NAME="atum_desk"
DB_USER="atum"
DB_PASSWORD="atum"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

echo "Creating database user..."
sudo -u postgres psql << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_USER}') THEN
        CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
    END IF;
END
\$\$;

ALTER ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
EOF

echo "Creating database..."
sudo -u postgres psql << EOF
SELECT 'CREATE DATABASE ${DB_NAME} OWNER ${DB_USER}' 
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}')\gexec
EOF

echo "Creating extensions..."
sudo -u postgres psql -d ${DB_NAME} << EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOF

echo "Granting privileges..."
sudo -u postgres psql -d ${DB_NAME} << EOF
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
GRANT ALL ON SCHEMA public TO ${DB_USER};
ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};
EOF

echo ""
echo "========================================="
echo "Database setup complete!"
echo "Database: ${DB_NAME}"
echo "User: ${DB_USER}"
echo "========================================="
