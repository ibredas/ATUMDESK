# 02_METRICS_ENDPOINT_PROOF.md

## Metrics Endpoint Proof

**Date:** 2026-02-13

---

## Endpoint Verification

```bash
$ curl -s http://localhost:8000/metrics | head -30
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 149.0
...
```

---

## Health Metrics

```bash
$ curl -s http://localhost:8000/metrics | grep -E "^atum_(db|ollama)_up"
atum_db_up 1.0
atum_ollama_up 1.0
```

---

## Prometheus Metrics Available

| Metric | Type | Description |
|--------|------|-------------|
| `atum_db_up` | Gauge | Database availability (1=up, 0=down) |
| `atum_ollama_up` | Gauge | Ollama availability (1=up, 0=down) |
| `atum_http_requests_total` | Counter | Total HTTP requests |
| `atum_http_request_duration_seconds` | Histogram | Request duration |
| `atum_errors_total` | Counter | Error count by type |
| `atum_job_queue_depth` | Gauge | Job queue depth |
| `atum_worker_job_total` | Counter | Jobs processed |

---

## Implementation

- **Endpoint:** `/metrics` (Prometheus format)
- **Router:** `/data/ATUM DESK/atum-desk/api/app/routers/metrics.py`
- **Background Task:** Updates health metrics every 30 seconds

---

*Proof generated: 2026-02-13*
