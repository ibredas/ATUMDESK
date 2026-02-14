# Admin User Proof

**Date**: 2026-02-13

---

## Script Created

**Location**: `api/scripts/create_or_update_admin.py`

Usage:
```bash
python api/scripts/create_or_update_admin.py --email ibreda@local --password 'Mido@Meiam' --role ADMIN
```

---

## SQL Verification

```sql
SELECT id, email, role, is_active FROM users WHERE email ILIKE '%ibreda%';
```

**Result**:
```
                  id                  |    email     | role  | is_active 
--------------------------------------+--------------+-------+-----------
 8eda56d6-acf5-49bd-9343-08da99bce173 | ibreda@local | ADMIN | t
```

---

## Credentials

- **Email**: ibreda@local
- **Password**: Mido@Meiam
- **Role**: ADMIN

**Status**: ✅ CREATED
