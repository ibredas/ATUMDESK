# 07 - IMAP Policy Proof

## Issue
IMAP credentials were configured but invalid, causing error logs every minute.

---

## Fix Applied

Disabled IMAP in `.env` by commenting out credentials:

**File**: `atum-desk/api/.env`

```bash
# Before:
IMAP_HOST=imap.gmail.com
IMAP_USER=support@atum.desk
IMAP_PASSWORD=your-app-password

# After:
# Email Ingestion (IMAP) - DISABLED UNTIL CREDENTIALS CONFIGURED
# IMAP_HOST=imap.gmail.com
# IMAP_USER=support@atum.desk
# IMAP_PASSWORD=your-app-password
```

---

## Verification

### Log Output After Fix
```
Feb 13 00:24:32 Hera bash[129526]: IMAP not configured. Email ingestion disabled.
Feb 13 00:24:32 Hera bash[129526]: INFO:     Application startup complete.
```

### No More Error Spam
```bash
$ journalctl -u atum-desk-api -n 20 | grep -i imap
Feb 13 00:24:32 IMAP not configured. Email ingestion disabled.
```

---

## To Re-enable

When valid IMAP credentials are available, uncomment and configure:

```bash
IMAP_HOST=imap.yourprovider.com
IMAP_USER=your-email@domain.com
IMAP_PASSWORD=your-app-password
```

Then restart: `sudo systemctl restart atum-desk-api`

---

## Summary

| Item | Status |
|------|--------|
| IMAP disabled | ✅ Config commented out |
| Error logs stopped | ✅ Verified in journalctl |
| Service restarted | ✅ Running |
