import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Use fallback for local testing without docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://koinos:password@localhost:5432/koinos_db")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
