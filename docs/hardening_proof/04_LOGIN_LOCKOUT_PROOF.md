# 04_LOGIN_LOCKOUT_PROOF.md

## Login Lockout Proof

**Date:** 2026-02-13

---

## Test: Failed Login Attempts

```bash
$ curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=test@test.com&password=wrong"
{"detail":"Too many failed attempts. Try again in 14 minutes."}
```

---

## Implementation

- **Table:** `auth_login_attempts`
- **Storage:** PostgreSQL (NO Redis)
- **Max attempts:** 5
- **Lockout duration:** 15 minutes

---

## Code Location

`/data/ATUM DESK/atum-desk/api/app/services/security/login_attempt.py`

---

*Proof generated: 2026-02-13*
