import asyncio
import sys
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.append(os.getcwd())
from app.config import get_settings

settings = get_settings()

async def check_alembic():
    engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT * FROM alembic_version"))
        for row in result:
             print(f"Current Head in DB: {row[0]}")

if __name__ == "__main__":
    asyncio.run(check_alembic())
