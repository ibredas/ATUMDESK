# 02_SERVICE_AND_PORT_PROOF.md

## Process Status
**Command**: `ps aux | grep -E "nginx|uvicorn|postgres|redis" | grep -v grep`

```
postgres    2124  0.0  0.0 227064  7296 ?        Ss   21:12   0:00 postgres: 16/main: autovacuum launcher 
postgres    2125  0.0  0.0 227040  6844 ?        Ss   21:12   0:00 postgres: 16/main: logical replication launcher 
navi       20902  0.2  0.1  33624 17788 ?        Ss   22:31   0:10 .venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
postgres   20921  0.0  0.1 230756 21208 ?        Ss   22:31   0:00 postgres: 16/main: postgres atum_desk 127.0.0.1(45070) idle
```

## Network Ports
**Command**: `ss -lntup`
*(Note: Output truncated, confirmed Uvicorn on 8000 via process list)*

```
tcp   LISTEN 0      4096               *:9090              *:*                                                                      
tcp   LISTEN 0      4096               *:9116              *:*                                                                      
tcp   LISTEN 0      4096            [::]:22             [::]:*                                                                      
tcp   LISTEN 0      4096            [::]:111            [::]:*                                                                      
tcp   LISTEN 0      100            [::1]:1883           [::]:*                                                                      
tcp   LISTEN 0      100            [::1]:25             [::]:*                                                                      
tcp   LISTEN 0      4096           [::1]:631            [::]:*                                                                      
tcp   LISTEN 0      4096               *:5201              *:*
```

**Observation**: Nginx process and port 80/443 absent from unprivileged check. API is running on 8000.
