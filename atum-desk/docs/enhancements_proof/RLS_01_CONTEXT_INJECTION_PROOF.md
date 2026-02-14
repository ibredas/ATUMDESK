# RLS 01 - CONTEXT INJECTION PROOF

## Date: 2026-02-14

## Implementation

### Files Created

1. `api/app/db/session.py` - Updated with org context injection
2. `api/app/middleware/rls_context.py` - New middleware

### Context Variables

```python
org_context_var: ContextVar[Optional[str]] = ContextVar('org_context', default=None)
user_context_var: ContextVar[Optional[str]] = ContextVar('user_context', default=None)
```

### Session Functions

| Function | Purpose |
|----------|---------|
| get_session() | Auto-injects org context from context var |
| set_org_context() | Set org for current request |
| set_user_context() | Set user for current request |
| get_session_with_org() | Explicit org for workers |
| get_global_session() | NULL org for global queries |

### How It Works

1. **FastAPI Request Flow**:
   ```
   Request → Auth Middleware → set_org_context() → get_session() → SET app.current_org
   ```

2. **Worker Flow**:
   ```
   Job Worker → get_session_with_org(org_id) → SET app.current_org
   ```

3. **Global Queries**:
   ```
   System queries → get_global_session() → SET app.current_org = NULL
   ```

### Verification

```sql
-- Test SET works
SHOW app.current_org;

-- Helper function
SELECT set_app_org('org-uuid');
```

### Status

✅ Context injection infrastructure implemented
✅ Ready for staged RLS rollout
