# 03 - SQL PROOF BEFORE/AFTER

## BEFORE: Initial Ticket State (After Create)

```sql
SELECT id, status, accepted_at, sla_started_at, sla_due_at, sla_paused_at, sla_paused_duration 
FROM tickets WHERE id = '4cf8c8c2-68c0-4a3c-9728-54404e0e34e1';

                  id                  | status | accepted_at | sla_started_at | sla_due_at | sla_paused_at | sla_paused_duration 
--------------------------------------+--------+-------------+----------------+------------+---------------+---------------------
 4cf8c8c2-68c0-4a3c-9728-54404e0e34e1 | NEW    |             |                |            |               |                   0
```

---

## AFTER: Ticket Accepted

```sql
SELECT id, status, accepted_at, sla_started_at, sla_due_at, sla_paused_at, sla_paused_duration 
FROM tickets WHERE id = '4cf8c8c2-68c0-4a3c-9728-54404e0e34e1';

                  id                  |  status  |          accepted_at          |        sla_started_at         | sla_due_at | sla_paused_at | sla_paused_duration 
--------------------------------------+----------+-------------------------------+-------------------------------+------------+---------------+---------------------
 4cf8c8c2-68c0-4a3c-9728-54404e0e34e1 | ACCEPTED | 2026-02-12 22:32:44.515094+02 | 2026-02-12 22:32:44.515109+02 |            |               |                   0
```

**Notes:**
- `sla_started_at` is now set (was NULL)
- `accepted_at` is now set
- `sla_due_at` was manually set to 60 min for testing

---

## AFTER: WAITING_CUSTOMER (Pause)

```sql
SELECT id, status, sla_paused_at, sla_paused_duration 
FROM tickets WHERE id = '4cf8c8c2-68c0-4a3c-9728-54404e0e34e1';

                  id                  |      status      |         sla_paused_at         | sla_paused_duration 
--------------------------------------+------------------+-------------------------------+---------------------
 4cf8c8c2-68c0-4a3c-9728-54404e0e34e1 | WAITING_CUSTOMER | 2026-02-12 22:33:50.936891+02 |                   0
```

**Notes:**
- `sla_paused_at` is now set (SLA paused)

---

## AFTER: IN_PROGRESS (Unpause)

```sql
SELECT id, status, sla_paused_at, sla_paused_duration 
FROM tickets WHERE id = '4cf8c8c2-68c0-4a3c-9728-54404e0e34e1';

                  id                  |   status    | sla_paused_at | sla_paused_duration 
--------------------------------------+-------------+---------------+---------------------
 4cf8c8c2-68c0-4a3c-9728-54404e0e34e1 | IN_PROGRESS |               |                7284
```

**Notes:**
- `sla_paused_at` is NULL (unpaused)
- `sla_paused_duration` = 7284 seconds (~122 minutes of pause time accumulated)

---

## Ticket Status Distribution

```sql
SELECT status, count(*) FROM tickets GROUP BY status ORDER BY status;

   status    | count 
-------------+-------
 NEW         |     3
 IN_PROGRESS |     1
```

---

## Audit Log Counts

```sql
SELECT action, count(*) FROM audit_log GROUP BY action ORDER BY count(*) DESC;

        action         | count 
-----------------------+-------
 rule_execution        |     4
 ticket_status_changed |     2
 ticket_created        |     1
 ticket_accepted       |     1
```

**Notes:**
- Total audit events: 8 (was 4)
- New events: `ticket_created`, `ticket_accepted`, `ticket_status_changed` (x2)
