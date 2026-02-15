import asyncio
import os
import sys
import inspect
from sqlalchemy import text
from app.db.base import engine
from app.api.deps import get_db

# Verification of Code Structure & DB
async def verify_system():
    print("=== VERIFICATION STARTED ===")
    
    # 1. DB Tables
    tables = ["ticket_ai_triage", "ai_suggestions", "ticket_kb_suggestions", "kb_suggestion_votes", 
              "sla_calculations", "metrics_snapshots", "workflow_execution_logs", 
              "rules", "playbooks", "audit_log"]
    
    async with engine.connect() as conn:
        for t in tables:
            try:
                await conn.execute(text(f"SELECT 1 FROM {t} LIMIT 1"))
                print(f"✅ Table '{t}' exists")
            except Exception as e:
                print(f"❌ Table '{t}' MISSING or Error: {e}")

        # 2. Org Settings Columns
        try:
            r = await conn.execute(text("SELECT require_2fa, audit_retention_days, auto_escalate_negative_sentiment FROM org_settings LIMIT 1"))
            print("✅ org_settings columns (require_2fa, retention, auto_escalate) exist")
        except Exception as e:
            print(f"❌ org_settings columns MISSING: {e}")

    # 3. Job Worker Handlers (Static Analysis via Import)
    try:
        from scripts.job_worker import JobWorker
        jw = JobWorker()
        handlers = ["handle_triage_ticket", "handle_cleanup_logs", "handle_sentiment_analysis", "handle_metrics_snapshot"]
        for h in handlers:
            if hasattr(jw, h):
                print(f"✅ JobWorker.{h} method exists")
            else:
                print(f"❌ JobWorker.{h} method MISSING")
                
        # Check source code for audit_log checks
        import inspect
        src = inspect.getsource(jw.handle_triage_ticket)
        if "audit_log_write" in src:
            print("✅ handle_triage_ticket calls audit_log_write")
        else:
            print("❌ handle_triage_ticket MISSING audit_log_write call")
            
        src_clean = inspect.getsource(jw.handle_cleanup_logs)
        if "DELETE FROM audit_log" in src_clean:
             print("✅ handle_cleanup_logs has DELETE logic")
        else:
             print("❌ handle_cleanup_logs MISSING delete logic")
             
    except Exception as e:
        print(f"❌ Worker Verification Failed: {e}")

    # 4. API Endpoints (Static Check of routers)
    try:
        from app.routers import metrics, two_factor
        
        # Check /metrics/live
        if hasattr(metrics, "metrics_live"):
             print("✅ metrics.metrics_live function exists")
        else:
             print("❌ metrics.metrics_live function MISSING")
             
        # Check 2FA policy
        if hasattr(two_factor, "get_2fa_status"):
             # Inspect validation logic? simpler to just check if func exists
             print("✅ two_factor.get_2fa_status function exists")
    except Exception as e:
        print(f"❌ Router Verification Failed: {e}")

    print("=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    # Add path to allow imports
    sys.path.append(os.getcwd()) 
    asyncio.run(verify_system())
