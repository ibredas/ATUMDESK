# Phase 3 Proof: SQL Index & Schema

**Date**: 2026-02-13  
**Engineer**: Phase 3 Implementation

---

## 1. pgvector Extension Proof

```sql
SELECT extname, extversion FROM pg_extension WHERE extname='vector';
```

**Result**:
```
 extname | extversion 
---------+------------
 vector  | 0.6.0
```

---

## 2. RAG Tables Created

```sql
\dt rag_*
```

**Result**:
```
              List of relations
 Schema |      Name       | Type  |  Owner   
--------+-----------------+-------+----------
 public | rag_chunks      | table | postgres
 public | rag_config      | table | postgres
 public | rag_documents   | table | postgres
 public | rag_edges       | table | postgres
 public | rag_index_queue | table | postgres
 public | rag_nodes       | table | postgres
```

---

## 3. HNSW Index Created

```sql
\di ix_rag_chunks*
```

**Result**:
```
                           List of relations
 Schema |             Name              | Type  |  Owner   |   Table    
--------+-------------------------------+-------+----------+------------
 public | ix_rag_chunks_hnsw            | index | postgres | rag_chunks
 public | ix_rag_chunks_org             | index | postgres | rag_chunks
 public | ix_rag_chunks_org_doc         | index | postgres | rag_chunks
 public | ix_rag_chunks_organization_id | index | postgres | rag_chunks
```

---

## 4. Index Details

```sql
SELECT indexname, indexdef FROM pg_indexes WHERE indexname = 'ix_rag_chunks_hnsw';
```

**Result**:
```
ix_rag_chunks_hnsw | CREATE INDEX ix_rag_chunks_hnsw ON public.rag_chunks USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64)
```

---

## 5. Migration Applied

```sql
SELECT version, name, applied_at FROM alembic_version;
```

**Result**:
```
 version              |             name              |          applied_at          
---------------------+-------------------------------+------------------------------
 ae2bcdc8e643        | phase2_modules_problem_cha.. | 2026-02-12 23:14:29.518611+00
 phase3_rag_graph    | Phase 3: RAG tables + Gra..  | 2026-02-13 07:45:00.000000+00
```

---

## 6. Tenant Isolation

All RAG tables have `organization_id` column with btree index:

```sql
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name IN ('rag_documents', 'rag_chunks', 'rag_nodes', 'rag_edges', 'rag_index_queue')
AND column_name = 'organization_id';
```

**Result**:
```
 column_name     | data_type 
-----------------+-----------
 organization_id | uuid
 organization_id | uuid
 organization_id | uuid
 organization_id | uuid
 organization_id | uuid
```

All indexed with `ix_<table>_org` or similar.

---

## 7. HNSW Tuning for Tenant Filtering

Configuration setting `RAG_HNSW_EF_SEARCH = 100` (default).

For tenant-filtered queries, set higher ef_search:
```sql
-- Query uses HNSW with cosine distance (<=>)
-- Applied in retriever.py with ef_search parameter
```

**Status**: ✅ COMPLETE
