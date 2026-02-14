# DB Connection Proof

**Date**: 2026-02-13

---

## Canonical DATABASE_URL (Redacted)

```
DATABASE_URL=postgresql+asyncpg://postgres:****@localhost:5432/atum_desk
```

---

## PSQL Connection Test

```bash
$ psql -h localhost -U postgres -d atum_desk -c "SELECT 1 as test"
 test 
------
    1
(1 row)
```

**Status**: ✅ CONNECTED

---

## PostgreSQL Users

```bash
$ sudo -u postgres psql -c "\du"
```

Available roles: postgres (superuser), etc.

---

## API Service Uses Correct DB

```bash
$ systemctl cat atum-desk-api.service | grep EnvironmentFile
EnvironmentFile=/data/ATUM DESK/atum-desk/api/.env
```

```bash
$ grep DATABASE_URL /data/ATUM\ DESK/atum-desk/api/.env
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/atum_desk"
```

**Status**: ✅ VERIFIED
