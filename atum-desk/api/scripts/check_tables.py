import sys
import os
import asyncio
from sqlalchemy import text

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app.db.base import engine

async def list_tables():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = sorted([row[0] for row in result])
            print("Tables found in DB:")
            for t in tables:
                print(f"- {t}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_tables())
