# PHASE 2.2: CSRF PROTECTION DESIGN

## Overview
Implement CSRF protection using Double Submit Cookie pattern for JWT-based authentication.

## Architecture

### 1. CSRF Token Generation
- Algorithm: HMAC-SHA256
- Secret: Use existing SECRET_KEY
- Token format: base64(timestamp + random + signature)
- Lifetime: 24 hours

### 2. Token Distribution
- Set cookie: `csrf_token` (httpOnly=false, secure=true, SameSite=Lax)
- Cookie sent with every response
- Frontend reads cookie and sends in header

### 3. Token Validation
- Middleware intercepts POST/PUT/DELETE/PATCH
- Reads cookie from request
- Reads header `X-CSRF-Token` from request
- Compares: cookie value == header value
- If mismatch: 403 Forbidden

### 4. Implementation Files
1. `app/middleware/csrf.py` - CSRF middleware
2. `app/services/csrf_service.py` - Token generation/validation
3. Update `app/main.py` - Add middleware
4. Update `app/routers/auth.py` - Set CSRF cookie on login

### 5. Frontend Changes
1. Extract CSRF cookie on app load
2. Add `X-CSRF-Token` header to all mutating requests
3. Handle 403 errors gracefully

## Security Considerations
- Tokens are signed with SECRET_KEY
- Short lifetime (24h) reduces attack window
- SameSite=Lax prevents CSRF from external sites
- Secure flag ensures HTTPS only
- No httpOnly so JS can read it (required for Double Submit)

## Constraints Compliance
✓ No Redis - uses signed cookies only
✓ No External APIs - pure Python/HMAC
✓ Stateless - no server-side storage needed

## Testing Strategy
1. Verify token generation works
2. Verify cookie is set on login
3. Verify middleware blocks requests without token
4. Verify valid requests pass
5. Verify token expires after 24h

