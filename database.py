from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL_ASYNC = "sqlite+aiosqlite:///./production.db?check_same_thread=False"
DATABASE_URL_SYNC = "sqlite:///./production.db?check_same_thread=False"

engine = create_async_engine(DATABASE_URL_ASYNC)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
        await session.commit()
