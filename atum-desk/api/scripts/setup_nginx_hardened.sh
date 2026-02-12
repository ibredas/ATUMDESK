#!/bin/bash
# ATUM DESK - NGINX Hardening Setup Script
# Run this script with sudo: sudo bash scripts/setup_nginx_hardened.sh

set -e

echo "🚀 Starting NGINX Security Hardening..."

# 1. Create SSL Directory
mkdir -p /etc/nginx/ssl

# 2. Generate Self-Signed Certificates
if [ ! -f /etc/nginx/ssl/atum-desk.key ]; then
    echo "🔑 Generating SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/atum-desk.key \
        -out /etc/nginx/ssl/atum-desk.crt \
        -subj "/C=US/ST=State/L=City/O=ATUM/CN=localhost"
    chmod 600 /etc/nginx/ssl/atum-desk.key
fi

# 3. Create Hardened NGINX Configuration
echo "📝 Writing NGINX configuration..."
cat << 'EOF' > /etc/nginx/sites-available/atum-desk.conf
# ATUM DESK - Hardened NGINX Config

# Rate Limiting Zones
limit_req_zone $binary_remote_addr zone=atum_api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=atum_login_limit:10m rate=1r/s;

server {
    listen 80 default_server;
    server_name localhost _ atum.local;
    # Redirect all HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2 default_server;
    server_name localhost _ atum.local;

    # SSL Certificates
    ssl_certificate /etc/nginx/ssl/atum-desk.crt;
    ssl_certificate_key /etc/nginx/ssl/atum-desk.key;

    # Secure SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_session_timeout 1d;
    ssl_session_cache shared:ATUM_SSL:20m;
    ssl_stapling off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'; frame-ancestors 'self';" always;

    # Backend API Proxy (Prioritized)
    location ^~ /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Apply Rate Limiting
        limit_req zone=atum_api_limit burst=20 nodelay;
        
        # Specific limit for login
        location ^~ /api/v1/auth/login {
            limit_req zone=atum_login_limit burst=5 nodelay;
            proxy_pass http://127.0.0.1:8000;
        }
        
        location ^~ /api/v1/health {
            proxy_pass http://127.0.0.1:8000;
        }
    }

    # Static Assets & Frontend
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}



EOF

# 4. Enable Configuration
ln -sf /etc/nginx/sites-available/atum-desk.conf /etc/nginx/sites-enabled/atum-desk.conf
# Remove default to avoid "duplicate default server" conflicts
rm -f /etc/nginx/sites-enabled/default

# 5. Test and Restart
echo "🔍 Testing NGINX configuration..."
nginx -t

echo "🔄 Restarting NGINX..."
systemctl restart nginx

echo "✅ NGINX Hardening Complete! Access at https://localhost"
