import asyncio
import sys
import os
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine

# Path hack
sys.path.append(os.getcwd())
from app.config import get_settings

settings = get_settings()

async def inspect_db():
    print(f"--- DB CONNECTION INFO ---")
    # Redact password from URL
    db_url = str(settings.DATABASE_URL)
    safe_url = db_url.split("@")[-1] if "@" in db_url else "Check Env"
    print(f"Target: {safe_url}")
    
    # Sync inspection using async engine's sync connector
    # But Alembic uses sync driver mostly. Let's use the async engine to connect and run sql
    
    engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
    
    async with engine.connect() as conn:
        print("\n--- ALEMBIC VERSION ---")
        result = await conn.execute(text("SELECT * FROM alembic_version"))
        for row in result:
             print(f"Current Head: {row[0]}")

        print("\n--- TABLES & COLUMNS ---")
        # We need run_sync for inspection
        await conn.run_sync(do_inspection)

def do_inspection(conn):
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    for table in tables:
        print(f"\nTABLE: {table}")
        print("  Columns:")
        for col in inspector.get_columns(table):
            print(f"    - {col['name']} ({col['type']}) Nullable: {col['nullable']}")
            
        print("  Indexes:")
        for idx in inspector.get_indexes(table):
             print(f"    - {idx['name']}: {idx['column_names']}")

if __name__ == "__main__":
    try:
        asyncio.run(inspect_db())
    except Exception as e:
        print(e)
