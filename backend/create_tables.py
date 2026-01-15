"""Create all database tables."""
import asyncio
import sys
sys.path.insert(0, '.')

from src.db.connection import engine, Base

# Import models to register them - import only the modules to avoid duplicate registration
import src.models.user
import src.models.user_profile
import src.models.user_progress
import src.models.chat
import src.models.progress


async def create_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        # Drop all tables first (for clean slate)
        print("Dropping existing tables...")
        await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    print("✅ All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
