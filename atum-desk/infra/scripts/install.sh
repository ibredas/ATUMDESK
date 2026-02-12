#!/bin/bash
# ATUM DESK Installation Script
# Sets up the complete system

set -e

echo "========================================="
echo "ATUM DESK - Installation"
echo "========================================="
echo ""

INSTALL_DIR="/data/ATUM DESK/atum-desk"

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "ERROR: PostgreSQL not found"
    exit 1
fi

if ! command -v redis-cli &> /dev/null; then
    echo "ERROR: Redis not found"
    exit 1
fi

if ! command -v nginx &> /dev/null; then
    echo "ERROR: nginx not found"
    exit 1
fi

if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found"
    exit 1
fi

echo "All prerequisites found!"
echo ""

# Setup database
echo "Setting up database..."
bash "${INSTALL_DIR}/infra/scripts/setup-db.sh"
echo ""

# Setup Python virtual environment
echo "Setting up Python virtual environment..."
cd "${INSTALL_DIR}/api"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Python dependencies installed!"
echo ""

# Create upload directory
echo "Creating upload directory..."
mkdir -p "${INSTALL_DIR}/data/uploads"
chmod 755 "${INSTALL_DIR}/data/uploads"
echo ""

# Copy environment file
echo "Setting up environment configuration..."
if [ ! -f "${INSTALL_DIR}/api/.env" ]; then
    cp "${INSTALL_DIR}/api/.env.example" "${INSTALL_DIR}/api/.env"
    echo "Created .env file from example. Please edit ${INSTALL_DIR}/api/.env to customize."
else
    echo ".env file already exists, skipping..."
fi
echo ""

# Setup systemd services
echo "Setting up systemd services..."
cp "${INSTALL_DIR}/infra/systemd/atum-desk-api.service" /etc/systemd/system/
cp "${INSTALL_DIR}/infra/systemd/atum-desk-ws.service" /etc/systemd/system/
cp "${INSTALL_DIR}/infra/systemd/atum-desk-worker.service" /etc/systemd/system/
systemctl daemon-reload
echo "Systemd services installed!"
echo ""

# Setup nginx
echo "Setting up nginx..."
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi
cp "${INSTALL_DIR}/infra/nginx/atum-desk.conf" /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/atum-desk.conf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
echo "nginx configured!"
echo ""

# Build frontend
echo "Building frontend..."
cd "${INSTALL_DIR}/web"
npm install
npm run build
echo "Frontend built!"
echo ""

echo "========================================="
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit ${INSTALL_DIR}/api/.env if needed"
echo "2. Start services:"
echo "   sudo systemctl start atum-desk-api"
echo "   sudo systemctl start atum-desk-ws"
echo "   sudo systemctl start atum-desk-worker"
echo "3. Enable auto-start:"
echo "   sudo systemctl enable atum-desk-api"
echo "   sudo systemctl enable atum-desk-ws"
echo "   sudo systemctl enable atum-desk-worker"
echo ""
echo "Access ATUM DESK at: https://localhost"
echo "========================================="
