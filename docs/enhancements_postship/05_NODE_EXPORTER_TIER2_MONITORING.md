# 05_NODE_EXPORTER_TIER2_MONITORING.md

## Node Exporter Tier-2 Monitoring Proof

**Date:** 2026-02-13

---

## Service Status

```bash
$ systemctl status prometheus-node-exporter
● prometheus-node-exporter.service - Prometheus Node Exporter
     Loaded: loaded (/etc/systemd/system/prometheus-node-exporter.service; enabled)
     Active: active (running) since Fri 2026-02-13 16:55:02 EET
   Main PID: 519546 (node_exporter)
```

---

## Endpoint Verification

```bash
$ curl -s http://localhost:9100/metrics | head -10
# HELP go_gc_duration_seconds A summary of the pause duration of garbage collection cycles.
# TYPE go_gc_duration_seconds summary
go_gc_duration_seconds{quantile="0"} 0
...
```

---

## Available Metrics

| Category | Metrics |
|-----------|---------|
| CPU | `node_cpu_seconds_total`, `node_load1` |
| Memory | `node_memory_MemAvailable_bytes`, `node_memory_MemTotal_bytes` |
| Disk | `node_disk_io_time_seconds_total`, `node_filesystem_avail_bytes` |
| Network | `node_network_receive_bytes_total`, `node_network_transmit_bytes_total` |
| System | `node_time_seconds`, `node_uptime_seconds` |

---

## Implementation

- **Binary:** `/usr/local/bin/node_exporter`
- **Port:** 9100
- **Systemd:** `/etc/systemd/system/prometheus-node-exporter.service`

---

*Proof generated: 2026-02-13*
