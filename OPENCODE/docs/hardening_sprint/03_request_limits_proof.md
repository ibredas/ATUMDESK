# 03 - REQUEST LIMITS PROOF

## NGINX Configuration

### Body Size Limit

```
$ grep "client_max_body_size" /etc/nginx/sites-available/atum-desk.conf
    client_max_body_size 10M;
```

**Limit**: 10 MB per request

### Rate Limiting

```
$ grep "limit_req_zone" /etc/nginx/sites-available/atum-desk.conf
limit_req_zone $binary_remote_addr zone=atum_api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=atum_login_limit:10m rate=1r/s;
```

| Zone | Rate | Burst |
|------|------|-------|
| atum_api_limit | 10 requests/second | 20 |
| atum_login_limit | 1 request/second | 5 |

### Rate Limiting Applied

```nginx
location ^~ /api {
    limit_req zone=atum_api_limit burst=20 nodelay;
}

location ^~ /api/v1/auth/login {
    limit_req zone=atum_login_limit burst=5 nodelay;
}
```

## FastAPI Configuration

### Upload Size

```
$ grep "MAX_UPLOAD_SIZE" /data/ATUM DESK/atum-desk/api/app/config.py
MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
```

### Allowed Extensions

```
$ grep -A 15 "ALLOWED_EXTENSIONS" /data/ATUM DESK/atum-desk/api/app/config.py
ALLOWED_EXTENSIONS: List[str] = Field(
    default=[
        # Images
        "jpg", "jpeg", "png", "gif", "svg", "webp",
        # Documents
        "pdf", "doc", "docx", "txt", "rtf",
        # Spreadsheets
        "xls", "xlsx", "csv",
        # Archives
        "zip", "tar", "gz", "bz2", "7z",
        # Code
        "json", "xml", "yaml", "yml", "log"
    ]
)
```

### Upload Validation Code

```python
# From attachments.py
contents = await file.read()
if len(contents) > settings.MAX_UPLOAD_SIZE:
    raise HTTPException(status_code=413, detail="File too large")

file_ext = os.path.splitext(file.filename)[1][1:].lower()
if file_ext not in settings.ALLOWED_EXTENSIONS:
    raise HTTPException(status_code=400, detail="File type not allowed")
```

## Summary

| Check | Limit | Status |
|-------|-------|--------|
| NGINX body size | 10 MB | ✅ Configured |
| NGINX API rate | 10 r/s | ✅ Configured |
| NGINX login rate | 1 r/s | ✅ Configured |
| FastAPI upload size | 50 MB | ✅ Configured |
| Extension whitelist | 24 types | ✅ Configured |
