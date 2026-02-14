# SLA Prediction & Alerts Proof - ATUM DESK Enhancement

## Date: 2026-02-14

## SLA Prediction Columns

```sql
atum_desk=# \d tickets
```

```
...
time_to_breach_minutes    | integer           | 
sla_risk_score            | double precision  | 
```

### Description

- `time_to_breach_minutes`: Minutes until SLA breach
- `sla_risk_score`: 0-1 risk score (1 = highest risk)

## SLA Worker Implementation

### Script Location

```
/data/ATUM DESK/atum-desk/api/scripts/run_sla_worker.py
```

### Algorithm (Deterministic Heuristic v1)

1. Get ticket with SLA policy
2. Calculate elapsed time
3. Calculate remaining time
4. Compute risk score: `elapsed / total * 100`
5. If >= 90%: HIGH risk
6. If >= 75%: MEDIUM risk
7. Else: LOW risk

### Alert Thresholds

- **75%**: Warning notification
- **90%**: Critical notification
- **100%**: Breached (already handled)

## Notifications Table

```sql
atum_desk=# \dt notifications
```

```
            List of relations
 Schema |     Name     | Type  |  Owner   
--------+--------------+-------+----------
 public | notifications | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| ticket_id | uuid | Ticket reference |
| type | text | Alert type |
| payload | jsonb | Alert data |
| created_at | timestamptz | Creation time |
| read_at | timestamptz | Read timestamp |

## SLA Policies Table

```sql
atum_desk=# \dt sla_policies
```

```
            List of relations
 Schema |     Name     | Type  |  Owner   
--------+--------------+-------+----------
 public | sla_policies  | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| name | text | Policy name |
| response_time_minutes | int | First response SLA |
| resolution_time_minutes | int | Resolution SLA |
| priority | text | Ticket priority |

## SLA Calculations Table

```sql
atum_desk=# \dt sla_calculations
```

```
            List of relations
 Schema |      Name       | Type  |  Owner   
--------+-----------------+-------+----------
 public | sla_calculations | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| ticket_id | uuid | Ticket reference |
| policy_id | uuid | Policy reference |
| started_at | timestamptz | SLA start |
| first_response_at | timestamptz | First response |
| resolved_at | timestamptz | Resolution time |
| sla_breached | boolean | Breach flag |

## Worker Status

```bash
$ systemctl status atum-desk-sla-worker
```

```
● atum-desk-sla-worker.service - ATUM DESK SLA Worker - SLA monitoring and alerts
     Loaded: loaded (/etc/systemd/system/atum-desk-sla-worker.service; enabled)
     Active: active (running) since Sat 2026-02-14 01:39:03 EET (11h ago)
```

## Sentiment-Based Escalation

### Organization Setting

```sql
atum_desk=# SELECT * FROM org_settings LIMIT 1;
```

```
 id | organization_id | auto_escalate_negative_sentiment | auto_escalate_threshold | ...
```

### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| auto_escalate_negative_sentiment | false | Auto-escalate negative tickets |
| auto_escalate_threshold | 0.7 | Confidence threshold |

### Behavior

1. Ticket triage detects sentiment
2. If negative AND confidence > threshold:
   - Create escalation suggestion (always)
   - If org setting enabled: set priority urgent + notify manager

### Audit Events

- `sla_risk_alert_created`
- `ticket_escalated`
