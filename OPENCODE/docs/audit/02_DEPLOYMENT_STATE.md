# Deployment State
## Running Services & Network Configuration

---

## 1. Systemd Units Found

### API Service
```
UNIT: atum-desk-api.service
FILE: /etc/systemd/system/atum-desk-api.service
STATUS: enabled, active (running)
SINCE: Thu 2026-02-12 22:31:43 EET
PID: 20902 (python3)
WORKERS: 4 uvicorn workers
PORT: 8000
```

### SLA Worker Service
```
UNIT: atum-desk-sla-worker.service
FILE: /etc/systemd/system/atum-desk-sla-worker.service
STATUS: enabled, active (running)
SINCE: Thu 2026-02-12 22:31:43 EET
PID: 20896 (python3)
RUNS: Every 60 seconds (checking SLAs)
```

---

## 2. Timers Found

No systemd timers found. The SLA worker runs as a continuous service, not a timer.

---

## 3. NGINX Configuration

### Config File
`/etc/nginx/sites-available/atum-desk.conf` (symlinked from sites-enabled)

### Server Blocks
```nginx
# HTTP (redirect to HTTPS)
server {
    listen 80 default_server;
    server_name localhost _ atum.local;
    return 301 https://$host$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2 default_server;
    server_name localhost _ atum.local;
    
    # SSL certs
    ssl_certificate /etc/nginx/ssl/atum-desk.crt;
    ssl_certificate_key /etc/nginx/ssl/atum-desk.key;
    
    # API proxy
    location ^~ /api {
        proxy_pass http://127.0.0.1:8000;
        limit_req zone=atum_api_limit burst=20 nodelay;
    }
    
    # Frontend
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### SSL Status
```
PROBLEM: nginx -T fails with:
"nginx: [emerg] cannot load certificate key 
 /etc/nginx/ssl/atum-desk.key: BIO_new_file() failed 
 (SSL: error:8000000D:system library::Permission denied)"
```

---

## 4. Open Ports (ss -lntup)

| Port | Service | Bind Address |
|------|---------|--------------|
| 80 | nginx | 0.0.0.0:80 |
| 443 | nginx | 0.0.0.0:443 |
| 5432 | postgres | 127.0.0.1:5432 |
| 8000 | uvicorn | 0.0.0.0:8000 |
| 6379 | redis | 127.0.0.1:6379 |
| 22 | ssh | 0.0.0.0:22 |
| 8280 | ? | 127.0.0.1:8280 |
| 8765 | ? | 0.0.0.0:8765 |

---

## 5. Running Processes

### API Processes
```
USER    PID    COMMAND
navi   20902  .venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
navi   20908  python3 (multiprocessing resource tracker)
navi   20909  python3 (uvicorn worker)
navi   20910  python3 (uvicorn worker)
navi   20911  python3 (uvicorn worker)
navi   20912  python3 (uvicorn worker)
```

### Database
```
postgres 1973  /usr/lib/postgresql/16/bin/postgres -D /var/lib/postgresql/16/main
postgres 2097  checkpointer
postgres 2098  background writer
postgres 2123  walwriter
postgres 2124  autovacuum launcher
```

### Web Server
```
root    1966  nginx: master process /usr/sbin/nginx
www-data 1967  nginx: worker process
www-data 1968  nginx: worker process
www-data 1969  nginx: worker process
www-data 1971  nginx: worker process
```

---

## 6. Log Locations & Health

### API Logs (journalctl)
```
SOURCE: journalctl -u atum-desk-api
LOCATION: /var/log/journal/ (systemd journal)
LAST 100 LINES:
- IMAP Connection Error: b'[AUTHENTICATIONFAILED] Invalid credentials (Failure)'
- Error polling email: b'[AUTHENTICATIONFAILED] Invalid credentials (Failure)'
- request_completed: GET /api/v1/health 200 OK
```

### SLA Worker Logs (journalctl)
```
SOURCE: journalctl -u atum-desk-sla-worker
LOCATION: /var/log/journal/
LAST 10 ENTRIES:
2026-02-12 22:41:46 - Checking SLAs for 1 tickets...
2026-02-12 22:42:46 - Checking SLAs for 1 tickets...
2026-02-12 22:43:46 - Checking SLAs for 1 tickets...
... (runs every minute)
```

### NGINX Logs
```
DEFAULT ACCESS LOG: /var/log/nginx/access.log
DEFAULT ERROR LOG: /var/log/nginx/error.log
NOTE: SSL errors logged to error.log
```

---

## 7. Service Health Checks

```bash
# API Health
curl http://localhost:8000/api/v1/health
# Returns: {"status":"healthy","timestamp":...,"version":"1.0.0",...}

# Frontend (via nginx)
curl -I http://localhost/
# Returns: HTTP/1.1 301 Moved Permanently (to HTTPS)

curl -k -I https://localhost/
# Returns: HTTP/2 405 (GET not allowed on root)
```
