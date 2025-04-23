
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select
from config import settings
import redis

# Create async engine
engine = create_async_engine(settings.DATABASE_URL)
# Create async session
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# Async dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# redis://redis:6379/0
# redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_one_object_by_filter(db: AsyncSession, model, **filters):
    result = await db.execute(select(model).filter_by(**filters))
    return result.scalars().first()


async def get_all_objects_by_filter(db: AsyncSession, model, **filters):
    result = await db.execute(select(model).filter_by(**filters))
    return result.scalars().all()