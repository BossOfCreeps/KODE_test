import asyncio
import os
import shutil
from typing import AsyncGenerator, Generator, Callable

import pytest
from fastapi import FastAPI

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from constants import BASE_MEDIA_PATH
from database import Base, async_session, get_db
from account import models  # NOT DELETE
from messages import models  # NOT DELETE

engine = create_async_engine("sqlite+aiosqlite:///./test.db?check_same_thread=False")


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
async def db_session() -> AsyncSession:
    async with engine.begin() as connection:
        if not os.path.exists(BASE_MEDIA_PATH):
            os.mkdir(BASE_MEDIA_PATH)
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        async with async_session(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()
        shutil.rmtree(os.path.join(os.curdir, "media"))


@pytest.fixture()
def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture()
def app(override_get_db: Callable) -> FastAPI:
    from main import app
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture()
async def async_client(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        yield ac
