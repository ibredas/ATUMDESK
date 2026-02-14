# 06_EMAIL_VERIFICATION_PROOF.md

## Email Verification Proof

**Date:** 2026-02-13

---

## Endpoints

- `POST /api/v1/auth/register` - Register user, creates inactive user + token
- `GET /api/v1/auth/verify-email?token=...` - Verify email
- `POST /api/v1/auth/resend-verification` - Resend verification

---

## Implementation

- **Table:** `email_verification_tokens`
- **Token:** Hashed before storage (security)
- **Expiry:** 24 hours

---

## Code Location

`/data/ATUM DESK/atum-desk/api/app/services/security/email_verification.py`

---

*Proof generated: 2026-02-13*
