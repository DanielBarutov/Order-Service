from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import src.settings

db_url = src.settings.POSTGRES_CONNECTION_STRING
if not db_url:
    raise ValueError("POSTGRES_CONNECTION_STRING is not set")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
engine = create_async_engine(db_url)


AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_session():
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
    except Exception as e:
        raise e
