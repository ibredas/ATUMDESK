# Metrics Proof

## Prometheus Metrics

All RLS guardrail metrics are exposed at `/metrics`.

### atum_org_context_missing_total
Counts requests that arrive without org context.

```prometheus
atum_org_context_missing_total{endpoint="/api/v1/tickets"} 12
atum_org_context_missing_total{endpoint="/api/v1/users"} 5
```

### atum_rls_denied_total
Counts RLS policy denials (blocked by policy).

```prometheus
atum_rls_denied_total{table="tickets"} 3
atum_rls_denied_total{table="users"} 1
```

### atum_rls_emergency_actions_total
Counts emergency RLS actions taken.

```prometheus
atum_rls_emergency_actions_total{action="degrade",actor="admin@atum.desk"} 1
atum_rls_emergency_actions_total{action="rollback",actor="admin@atum.desk"} 1
atum_rls_emergency_actions_total{action="restore",actor="admin@atum.desk"} 1
atum_rls_emergency_actions_total{action="degrade_failed",actor="unknown"} 2
```

## Viewing Metrics

### Curl
```bash
curl http://localhost:8000/metrics | grep -E "atum_.*rls|atum_org_context"
```

### Sample Output
```
# HELP atum_org_context_missing_total Total requests missing org context
# TYPE atum_org_context_missing_total counter
atum_org_context_missing_total{endpoint="/api/v1/tickets"} 12.0
atum_org_context_missing_total{endpoint="/api/v1/users"} 5.0

# HELP atum_rls_denied_total RLS policy denials
# TYPE atum_rls_denied_total counter
atum_rls_denied_total{table="tickets"} 3.0
atum_rls_denied_total{table="users"} 1.0

# HELP atum_rls_emergency_actions_total Emergency RLS actions
# TYPE atum_rls_emergency_actions_total counter
atum_rls_emergency_actions_total{action="degrade",actor="admin@atum.desk"} 1.0
atum_rls_emergency_actions_total{action="rollback",actor="admin@atum.desk"} 1.0
atum_rls_emergency_actions_total{action="restore",actor="admin@atum.desk"} 1.0
```

## Alerting Suggestions

### High org context missing
```yaml
- alert: HighOrgContextMissing
  expr: rate(atum_org_context_missing_total[5m]) > 10
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High rate of requests missing org context"
```

### Emergency action taken
```yaml
- alert: RLSEmergencyAction
  expr: increase(atum_rls_emergency_actions_total[1h]) > 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "RLS emergency action taken: {{ $labels.action }} by {{ $labels.actor }}"
```

## Dashboard Integration

Import this JSON into Grafana for a quick dashboard:

```json
{
  "title": "RLS Guardrails",
  "panels": [
    {
      "title": "Org Context Missing",
      "targets": [
        {"expr": "sum(rate(atum_org_context_missing_total[5m])) by (endpoint)"}
      ]
    },
    {
      "title": "RLS Denials",
      "targets": [
        {"expr": "sum(rate(atum_rls_denied_total[5m])) by (table)"}
      ]
    },
    {
      "title": "Emergency Actions",
      "targets": [
        {"expr": "sum(atum_rls_emergency_actions_total) by (action, actor)"}
      ]
    }
  ]
}
```
