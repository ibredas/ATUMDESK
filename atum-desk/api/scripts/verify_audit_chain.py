#!/usr/bin/env python3
"""
ATUM DESK - Audit Log Hash Chain Verification Tool

Verifies the integrity of the audit log hash chain.
Performs per-organization chain verification.

Usage:
    python scripts/verify_audit_chain.py [--org-id UUID] [--start-date DATE] [--end-date DATE]
"""
import asyncio
import argparse
import sys
import os
from datetime import datetime
from uuid import UUID

# Add path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/atum_desk")


async def compute_hash(prev_hash: str, org_id: UUID, user_id: UUID, action: str, 
                       entity_type: str, entity_id: UUID, created_at: datetime) -> str:
    """Compute SHA256 hash for audit row"""
    import hashlib
    import json
    
    data = {
        "prev_hash": prev_hash or "GENESIS",
        "org_id": str(org_id) if org_id else "",
        "user_id": str(user_id) if user_id else "",
        "action": action or "",
        "entity_type": entity_type or "",
        "entity_id": str(entity_id) if entity_id else "",
        "created_at": created_at.isoformat() if created_at else ""
    }
    
    hash_input = json.dumps(data, sort_keys=True)
    return hashlib.sha256(hash_input.encode()).hexdigest()


async def verify_chain(org_id: UUID = None, start_date: datetime = None, end_date: datetime = None):
    """Verify audit log hash chain"""
    
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.connect() as conn:
        # Build query
        query = """
            SELECT id, organization_id, user_id, action, entity_type, entity_id, created_at, prev_hash, row_hash
            FROM audit_log
            WHERE 1=1
        """
        params = {}
        
        if org_id:
            query += " AND organization_id = :org_id"
            params["org_id"] = str(org_id)
        
        if start_date:
            query += " AND created_at >= :start_date"
            params["start_date"] = start_date
        
        if end_date:
            query += " AND created_at <= :end_date"
            params["end_date"] = end_date
        
        query += " ORDER BY organization_id, created_at"
        
        result = await conn.execute(text(query), params)
        rows = result.fetchall()
    
    await engine.dispose()
    
    if not rows:
        print("No audit log entries found.")
        return True
    
    # Verify chain per organization
    org_chains = {}
    for row in rows:
        org_id_str = str(row[1]) if row[1] else "global"
        if org_id_str not in org_chains:
            org_chains[org_id_str] = []
        org_chains[org_id_str].append(row)
    
    all_verified = True
    total_entries = 0
    
    for org_id_str, entries in org_chains.items():
        print(f"\nVerifying chain for organization: {org_id_str}")
        expected_prev_hash = None
        
        for i, entry in enumerate(entries):
            entry_id, organization_id, user_id, action, entity_type, entity_id, created_at, prev_hash, row_hash = entry
            
            # Check previous hash
            if prev_hash != expected_prev_hash:
                print(f"  ❌ FAILED at entry {i+1}: prev_hash mismatch")
                print(f"     Expected: {expected_prev_hash}")
                print(f"     Found: {prev_hash}")
                all_verified = False
                break
            
            # Compute expected hash
            expected_hash = await compute_hash(
                prev_hash,
                organization_id,
                user_id,
                action,
                entity_type,
                entity_id,
                created_at
            )
            
            # Check row hash
            if row_hash != expected_hash:
                print(f"  ❌ FAILED at entry {i+1}: row_hash mismatch")
                print(f"     Expected: {expected_hash}")
                print(f"     Found: {row_hash}")
                all_verified = False
                break
            
            expected_prev_hash = row_hash
            total_entries += 1
        
        if all_verified or (i == len(entries) - 1):
            print(f"  ✓ Chain verified: {len(entries)} entries")
    
    print(f"\n{'='*50}")
    print(f"Total entries verified: {total_entries}")
    
    if all_verified:
        print("✓ VERIFIED - All audit log chains are intact")
        return True
    else:
        print("❌ FAILED - Chain integrity compromised!")
        return False


def main():
    parser = argparse.ArgumentParser(description="Verify audit log hash chain integrity")
    parser.add_argument("--org-id", type=str, help="Organization UUID to verify")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    org_id = UUID(args.org_id) if args.org_id else None
    start_date = datetime.fromisoformat(args.start_date) if args.start_date else None
    end_date = datetime.fromisoformat(args.end_date) if args.end_date else None
    
    result = asyncio.run(verify_chain(org_id, start_date, end_date))
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
