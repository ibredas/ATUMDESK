import asyncio
import sys
from pathlib import Path
from sqlalchemy import select, desc

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.base import AsyncSessionLocal
from app.models.audit_log import AuditLog
from app.models.user import User

async def verify_audit_logs():
    print("📋 Verifying Audit Logs...")
    async with AsyncSessionLocal() as session:
        # Fetch last 5 audit logs
        result = await session.execute(
            select(AuditLog).order_by(desc(AuditLog.created_at)).limit(5)
        )
        logs = result.scalars().all()
        
        print(f"Found {len(logs)} recent audit logs:")
        for log in logs:
            print(f"[{log.created_at}] Action: {log.action} | Entity: {log.entity_type} ({log.entity_id})")
            print(f"   Changes: {log.new_values}")
            
        if len(logs) > 0:
            print("✅ Audit Logs exist and are being recorded.")
        else:
            print("❌ No Audit Logs found!")

if __name__ == "__main__":
    asyncio.run(verify_audit_logs())
