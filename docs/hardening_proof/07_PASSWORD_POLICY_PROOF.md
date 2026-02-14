# 07_PASSWORD_POLICY_PROOF.md

## Password Policy Proof

**Date:** 2026-02-13

---

## Test: Weak Password Rejected

```bash
$ curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"weak","full_name":"Test"}'

{"detail":"Password must be at least 12 characters long"}
```

---

## Policy Requirements

- Minimum length: 12 characters
- Maximum length: 128 characters
- Must include: uppercase, lowercase, digit, special character
- Blocks common passwords (top 100)

---

## Implementation

`/data/ATUM DESK/atum-desk/api/app/services/security/password_policy.py`

---

*Proof generated: 2026-02-13*
