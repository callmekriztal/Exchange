import asyncio
import os
import sys

# Ensure backend root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import Base, engine
import app.models  # noqa: F401


async def init_tables():
    print("Connecting to database and creating tables...")
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_tables())
