# Dashboard Snapshots Proof - ATUM DESK Enhancement

## Date: 2026-02-14

## Metrics Snapshots Table

```sql
atum_desk=# \dt metrics_snapshots
```

```
            List of relations
 Schema |       Name        | Type  |  Owner   
--------+-------------------+-------+----------
 public | metrics_snapshots | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| snapshot_ts | timestamptz | Snapshot timestamp |
| tickets_by_status | jsonb | Ticket counts by status |
| tickets_by_priority | jsonb | Ticket counts by priority |
| frt_p50 | float | First response time p50 (min) |
| frt_p95 | float | First response time p95 (min) |
| mttr_p50 | float | Mean time to resolve p50 |
| mttr_p95 | float | Mean time to resolve p95 |
| sla_compliance_pct | float | SLA compliance % |
| agent_load | jsonb | Agent workload distribution |
| created_at | timestamptz | Creation time |

### Indexes

- `ix_metrics_snapshots_org_ts` (organization_id, snapshot_ts)

## Metrics Snapshot Worker

### Script Location

```
/data/ATUM DESK/atum-desk/api/scripts/metrics_snapshot_worker.py
```

### Configuration

```bash
SNAPSHOT_INTERVAL=30  # seconds
```

### Implementation

1. For each organization:
   - Count tickets by status
   - Count tickets by priority
   - Calculate SLA compliance %
   - Calculate FRT p50/p95
   - Calculate MTTR p50/p95
   - Insert snapshot record

### Service File

```
/data/ATUM DESK/atum-desk/infra/systemd/atum-desk-metrics-worker.service
```

### Status

```bash
$ systemctl status atum-desk-metrics-worker
```

```
● atum-desk-metrics-worker.service - ATUM DESK Metrics Snapshot Worker
     Loaded: loaded (/data/ATUM DESK/atum-desk/infra/systemd/atum-desk-metrics-worker.service)
     Active: (not started - needs enable)
```

## Live Dashboard API

### Endpoint

```
GET /api/v1/metrics/live
GET /api/v1/metrics/history?range=24h
```

### Response Example

```json
{
  "organization_id": "uuid",
  "tickets_by_status": {
    "open": 15,
    "pending": 8,
    "resolved": 42,
    "closed": 100
  },
  "tickets_by_priority": {
    "low": 20,
    "medium": 80,
    "high": 50,
    "urgent": 5
  },
  "frt_p50": 15.2,
  "frt_p95": 45.8,
  "mttr_p50": 240.5,
  "mttr_p95": 720.0,
  "sla_compliance_pct": 94.5,
  "agent_load": {
    "agent-1": 12,
    "agent-2": 8,
    "agent-3": 15
  },
  "snapshot_ts": "2026-02-14T13:00:00Z"
}
```

## Frontend Integration

### Dashboard Page

```
/desk/dashboard
```

### Polling

- Refresh every 5-10 seconds
- Uses snapshots API
- No WebSocket required (lightweight)

### Alternative: SSE

If lightweight needed:
- Server-Sent Events endpoint
- Pushes new snapshots on write

## DuckDB Export (Optional)

### Nightly Job

```sql
-- Export to DuckDB for heavy analytics
COPY metrics_snapshots 
TO '/data/ATUM DESK/atum-desk/exports/metrics_2026-02-14.parquet'
FORMAT PARQUET;
```

### Read-Only Analytics

- Separate read replica
- Heavy queries offloaded
- Postgres remains system-of-record
