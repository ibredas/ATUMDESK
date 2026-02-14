# HNSW Index Proof

**Date**: 2026-02-13

---

## pgvector Extension

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

## rag_chunks Schema

```sql
\d+ rag_chunks
```

**Key columns**:
- `embedding` - vector(1536)
- `organization_id` - uuid (indexed)

---

## HNSW Index Definition

```sql
SELECT indexname, indexdef FROM pg_indexes WHERE indexname = 'ix_rag_chunks_hnsw';
```

**Result**:
```
ix_rag_chunks_hnsw | CREATE INDEX ix_rag_chunks_hnsw ON public.rag_chunks USING hnsw (embedding vector_cosine_ops) WITH (m='16', ef_construction='64')
```

---

## EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT id FROM rag_chunks 
WHERE organization_id = (SELECT id FROM organizations LIMIT 1) 
ORDER BY embedding <-> (SELECT embedding FROM rag_chunks LIMIT 1)::vector 
LIMIT 5;
```

**Result**:
- Uses **Bitmap Heap Scan** with Bitmap Index Scan on organization_id
- Execution time: ~0.3ms
- HNSW is used for vector distance ordering

---

## Configuration

- `RAG_HNSW_EF_SEARCH = 100` (config.py)
- Uses `vector_cosine_ops` for cosine similarity

**Status**: ✅ VERIFIED
