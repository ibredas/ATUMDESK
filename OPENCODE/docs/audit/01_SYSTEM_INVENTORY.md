# System Inventory
## ATUM DESK - Technical Stack Overview

---

## 1. Operating System & Runtime

| Property | Value |
|----------|-------|
| **OS** | Ubuntu (via `lsb_release` or similar) |
| **Kernel** | Linux (observed in processes) |
| **Python** | 3.x (uvicorn in `.venv`) |
| **Node.js** | Not running (frontend is pre-built) |
| **PostgreSQL** | 16 |
| **Redis** | Running on localhost:6379 (not actively used by API) |
| **NGINX** | 1.24.0 |

---

## 2. Repository Structure

```
/data/ATUM DESK/
├── atum-desk/                    # Main application
│   ├── api/                      # FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/         # API endpoints
│   │   │   ├── models/          # SQLAlchemy models
│   │   │   ├── services/         # Business logic
│   │   │   ├── auth/             # JWT & auth
│   │   │   ├── db/               # Database session
│   │   │   └── config.py         # Settings
│   │   ├── migrations/          # Alembic migrations
│   │   ├── scripts/             # Utility scripts
│   │   ├── requirements.txt      # Python dependencies
│   │   └── .env                 # Environment config
│   ├── web/                      # React frontend
│   │   ├── src/                 # Source code
│   │   ├── dist/                # Built assets (served)
│   │   └── public/               # Static public assets
│   ├── data/
│   │   ├── uploads/             # File uploads (outside web root)
│   │   ├── backups/             # Backup directory (EMPTY)
│   │   └── exports/             # Export directory
│   └── infra/
│       ├── nginx/               # nginx configs
│       ├── systemd/             # systemd units
│       └── scripts/             # Infrastructure scripts
├── OPENCODE/                    # This audit documentation
└── DOCS/                        # Original blueprints
```

---

## 3. Exact Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Web Server** | NGINX | 1.24.0 |
| **API Framework** | FastAPI | (from requirements.txt) |
| **ASGI Server** | Uvicorn | (from requirements.txt) |
| **ORM** | SQLAlchemy (async) | (from requirements.txt) |
| **Database** | PostgreSQL | 16 |
| **Migrations** | Alembic | (from requirements.txt) |
| **Auth** | JWT (python-jose) | (from requirements.txt) |
| **Frontend** | React + Vite | (from package.json) |
| **Styling** | TailwindCSS | (from package.json) |

---

## 4. Environment Variables Used

| Variable | Purpose | Status |
|----------|---------|--------|
| `DEBUG` | Debug mode | Set |
| `DATABASE_URL` | PostgreSQL connection | Set |
| `SECRET_KEY` | JWT signing | Set |
| `REDIS_URL` | Redis connection | Set (not used) |
| `OLLAMA_URL` | AI endpoint | Set |
| `OLLAMA_MODEL` | AI model | Set |
| `AI_ENABLED` | AI toggle | Set |
| `UPLOAD_DIR` | Upload path | Set |
| `FRONTEND_URL` | CORS origin | Set |
| `IMAP_HOST` | Email ingestion | NOT SET |
| `IMAP_USER` | Email ingestion | NOT SET |
| `IMAP_PASSWORD` | Email ingestion | NOT SET |
| `SMTP_*` | Email notifications | NOT SET |

---

## 5. Upload Storage Location

| Property | Value |
|----------|-------|
| **Path** | `/data/ATUM DESK/atum-desk/data/uploads/` |
| **Outside Web Root** | YES - not accessible via HTTP |
| **Exists** | YES (empty, only .gitkeep) |
| **Permissions** | Owner: navi, Mode: 755 |

---

## 6. Key Files

| File | Purpose |
|------|---------|
| `/data/ATUM DESK/atum-desk/api/app/main.py` | FastAPI app entry point |
| `/data/ATUM DESK/atum-desk/api/app/config.py` | Settings & config |
| `/etc/nginx/sites-available/atum-desk.conf` | NGINX config |
| `/etc/systemd/system/atum-desk-api.service` | API systemd unit |
| `/etc/systemd/system/atum-desk-sla-worker.service` | SLA worker systemd unit |

---

*Evidence: All paths verified to exist via `ls` and file inspection.*
