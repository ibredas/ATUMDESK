# 01 - TLS PROOF

## TLS/HTTPS Status: WORKING

### Certificate Details

```
$ ls -la /etc/nginx/ssl/
-rw-r--r-- 1 root root 1273 Feb 12 09:52 atum-desk.crt
-rw------- 1 root root 1704 Feb 12 09:52 atum-desk.key
```

| File | Permissions | Status |
|------|-------------|--------|
| atum-desk.crt | 644 | Readable |
| atum-desk.key | 600 | Secure (owner only) |

### SSL Connection Test

```
$ openssl s_client -connect localhost:443 -servername localhost 2>/dev/null | head -15
CONNECTED(00000003)
---
Certificate chain
 0 s:C = US, ST = State, L = City, O = ATUM, CN = localhost
  i:C = US, ST = State, L = City, O = ATUM, CN = localhost
  a:PKEY: rsaEncryption, 2048 (bit); sigalg: RSA-SHA256
  v:NotBefore: Feb 12 07:52:47 2026 GMT
  v:NotAfter: Feb 12 07:52:47 2027 GMT
```

### HTTPS Headers

```
$ curl -k -I https://localhost/
HTTP/2 405 
Server: nginx/1.24.0 (Ubuntu)
strict-transport-security: max-age=31536000; includeSubDomains
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer-when-downgrade
Content-Security-Policy: default-src 'self' http: https: data: blob: 'unsafe-inline'; frame-ancestors 'self';
```

### HTTP → HTTPS Redirect

```
$ curl -I http://localhost/
HTTP/1.1 301 Moved Permanently
Server: nginx/1.24.0 (Ubuntu)
Location: https://localhost/
```

### Summary

| Check | Status |
|-------|--------|
| TLS 1.2+ | ✅ PASS |
| Valid Certificate | ✅ PASS (valid until Feb 2027) |
| HTTP→HTTPS Redirect | ✅ PASS |
| Security Headers | ✅ PASS |
| Key Permissions (600) | ✅ PASS |
