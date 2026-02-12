import asyncio
import sys
import os
sys.path.append(os.getcwd())
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import get_settings

async def enable_vector():
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL.unicode_string())
    
    async with engine.begin() as conn:
        try:
            print("Checking vector extension...")
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("Vector extension enabled!")
        except Exception as e:
            print(f"Error enabling vector extension: {e}")
            print("You might need superuser permissions.")

if __name__ == "__main__":
    asyncio.run(enable_vector())
