# 05 - Request Size Limits Proof

## NGINX Configuration

### Change Applied
Added `client_max_body_size 10M;` to nginx config.

**Before**: No size limit
**After**: 10MB limit enforced at nginx level

```bash
$ grep -n "client_max_body_size" /etc/nginx/sites-available/atum-desk.conf
31:    client_max_body_size 10M;
```

### Verification
```bash
$ pkexec --user root nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

$ pkexec --user root systemctl reload nginx
(success)
```

---

## FastAPI Validation

The FastAPI attachments router already has upload validation:

**File**: `atum-desk/api/app/routers/attachments.py`

```python
# Line 67-74
# Validate file size
contents = await file.read()
if len(contents) > settings.MAX_UPLOAD_SIZE:
    raise HTTPException(status_code=413, detail="File too large")

# Validate extension
file_ext = os.path.splitext(file.filename)[1][1:].lower()
if file_ext not in settings.ALLOWED_EXTENSIONS:
    raise HTTPException(status_code=400, detail="File type not allowed")
```

**Config** (`app/config.py`):
```python
MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS: List[str] = Field(...)  # whitelist of safe extensions
```

---

## Summary

| Layer | Limit | Status |
|-------|-------|--------|
| NGINX | 10MB | ✅ Configured |
| FastAPI | 50MB | ✅ Already present |
| Extension whitelist | Configured | ✅ Already present |

---

## Testing

```bash
# Test upload > 10MB (should fail at nginx level)
curl -X POST -H "Content-Type: application/octet-stream" \
  --data-binary @large_file.bin \
  https://localhost/api/v1/attachments/ticket/{ticket_id}
# Expected: 413 Payload Too Large
```

```bash
# Test upload < 10MB (should pass through to FastAPI)
curl -X POST -F "file=@small_file.txt" \
  https://localhost/api/v1/attachments/ticket/{ticket_id}
# Expected: 200 OK (if auth valid)
```
