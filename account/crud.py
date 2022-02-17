import hashlib
from random import choice
from string import ascii_letters, digits
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from account import models, schemas
from constants import AUTH_TOKEN_LENGTH


async def get_user_by_login(db: AsyncSession, login: str) -> Optional[models.User]:
    rows = list(await db.execute(select(models.User).where(models.User.login == login)))
    row = rows[0] if rows else []
    return row[0] if row else None


async def create_user(db: AsyncSession, user_scheme: schemas.UserCreate) -> models.User:
    db_user = models.User(login=user_scheme.login, password=hashlib.sha256(user_scheme.password.encode()).hexdigest())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_auth_token(db: AsyncSession, user: models.User) -> models.AuthToken:
    async def get_unique_token():
        temp_token = ''.join(choice(ascii_letters + digits) for _ in range(AUTH_TOKEN_LENGTH))
        # check unique
        if not list(await db.execute(select(models.AuthToken).where(models.AuthToken.token == temp_token))):
            return temp_token
        else:
            return get_unique_token()

    db_token = models.AuthToken(user_id=user.id, token=(await get_unique_token()))
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token


async def get_user_by_token(db: AsyncSession, user_token: str) -> Optional[models.User]:
    rows = list(await db.execute(select(models.AuthToken).where(models.AuthToken.token == user_token)))
    row = rows[0] if rows else []
    return row[0] if row else None
