# Ticket Relationships Proof - ATUM DESK Enhancement

## Date: 2026-02-14

## Ticket Relationships Table

```sql
atum_desk=# \dt ticket_relationships
```

```
            List of relations
 Schema |         Name          | Type  |  Owner   
--------+----------------------+-------+----------
 public | ticket_relationships  | table | postgres
```

### Schema

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| organization_id | uuid | Tenant ID |
| source_ticket_id | uuid | Source ticket |
| target_ticket_id | uuid | Target ticket |
| relationship_type | text | parent/child/duplicate/related |
| created_by | uuid | User who created |
| created_at | timestamptz | Creation time |

### Relationship Types

| Type | Description |
|------|-------------|
| parent | Parent ticket (epic) |
| child | Child ticket |
| duplicate | Duplicate of another |
| related | Related ticket |

### Indexes

- `ix_ticket_relationships_source` (source_ticket_id)
- `ix_ticket_relationships_target` (target_ticket_id)
- `ix_ticket_relationships_org` (organization_id)

## API Endpoints

### Link Tickets

```
POST /api/v1/tickets/{id}/relationships
```

```json
{
  "target_ticket_id": "uuid",
  "relationship_type": "related"
}
```

### Unlink Tickets

```
DELETE /api/v1/tickets/{id}/relationships/{relationship_id}
```

### Get Relationships

```
GET /api/v1/tickets/{id}/relationships
```

### Response

```json
{
  "relationships": [
    {
      "id": "uuid",
      "target_ticket_id": "uuid",
      "target_subject": "Related Issue",
      "relationship_type": "related",
      "created_at": "2026-02-14T10:00:00Z"
    }
  ]
}
```

## Implementation

### Router

```
/data/ATUM DESK/atum-desk/api/app/routers/ticket_relationships.py
```

### Features

1. **Create Link**: POST to create relationship
2. **Delete Link**: DELETE to remove
3. **Get All**: List all relationships for ticket
4. **Bulk Operations**: Link/unlink multiple

## UI Component

### Ticket Detail Page

Located at: `/desk/ticket/{id}`

Shows:
- Parent/Child tickets
- Duplicates
- Related tickets
- "Link to ticket" button

### Features

- Quick search to find tickets
- Drag-drop to reorder
- Bulk link/unlink

## Audit Events

| Event | Description |
|-------|-------------|
| ticket_relationship_created | Link created |
| ticket_relationship_deleted | Link removed |

## Example Usage

### Create Parent-Child

```json
POST /api/v1/tickets/child-123/relationships
{
  "target_ticket_id": "parent-456",
  "relationship_type": "child"
}
```

### Mark as Duplicate

```json
POST /api/v1/tickets/duplicate-789/relationships
{
  "target_ticket_id": "original-101",
  "relationship_type": "duplicate"
}
```

## Tenant Isolation

All operations filter by `organization_id`:
- Users can only see relationships within their org
- Cross-org relationships blocked
- Full audit trail maintained
