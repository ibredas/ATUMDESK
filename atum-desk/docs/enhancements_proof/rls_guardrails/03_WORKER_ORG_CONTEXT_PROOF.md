# Worker Org Context Proof

## Overview
Background workers (job_worker.py, rag_worker.py, etc.) must set org context per job to ensure tenant isolation.

## Implementation

### Job Worker
```python
# In scripts/job_worker.py

async def set_org_context(self, org_id: str):
    """Set RLS org context for this connection"""
    if org_id:
        await self.conn.execute(f"SET LOCAL app.current_org = '{org_id}'")
        logger.debug("org_context_set", org_id=org_id)

async def process_job(self, job: Dict[str, Any]) -> bool:
    org_id = job.get("organization_id")
    
    # Set RLS org context per job (CRITICAL for tenant isolation)
    await self.set_org_context(org_id)
    
    try:
        return await handler(job)
    finally:
        await self.clear_org_context()
```

### Key Points
1. **SET LOCAL**: Uses session-local setting so it doesn't affect other connections
2. **Per-job**: Sets context before each job processes
3. **Cleanup**: Clears context after job completes (in finally block)
4. **NULL handling**: Jobs without org_id get NULL context (global queries only)

## Verification

### 1. Check Worker Sets Context
```bash
# Start job worker and process a job
python scripts/job_worker.py

# Check logs for org context
# Should see: "org_context_set" org_id="<uuid>"
```

### 2. Verify Isolation
```sql
-- In a job that queries tickets:
-- Job with org_id = 'org-a' should only see org-a's tickets

-- Verify with:
SELECT COUNT(*) FROM tickets; 
-- Should return only tickets for that org
```

### 3. Test No Cross-Tenant Leakage
```python
# Create two jobs with different orgs
Job 1: organization_id = 'org-a'
Job 2: organization_id = 'org-b'

# Each should only see their own data
# Check job logs for correct ticket counts
```

## Protected Job Types
All tenant-aware jobs must have organization_id:
- TRIAGE_TICKET
- KB_SUGGEST
- SMART_REPLY
- SLA_PREDICT
- METRICS_SNAPSHOT

## Global Jobs (No Org Context)
Some system jobs may need global access:
- Cleanup jobs
- Migration jobs
- System metric collection

These should use `get_global_session()` from `app/db/session.py`.

## Metrics
Workers increment metrics when org context is missing:
```python
from app.routers.metrics import org_context_missing_total
org_context_missing_total.labels(endpoint="worker").inc()
```
