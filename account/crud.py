from hashlib import sha256
from secrets import choice
from string import ascii_letters, digits
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from account import models, schemas
from constants import AUTH_TOKEN_LENGTH
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="account/login")


async def get_user_by_login(db: AsyncSession, login: str) -> Optional[models.User]:
    rows = list(await db.execute(select(models.User).where(models.User.login == login)))
    row = rows[0] if rows else []
    return row[0] if row else None


async def create_user(db: AsyncSession, user_scheme: schemas.UserCreate) -> models.User:
    db_user = models.User(login=user_scheme.username, password=sha256(user_scheme.password.encode()).hexdigest())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_auth_token(db: AsyncSession, user: models.User) -> str:
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
    return db_token.token


async def get_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Optional[models.User]:
    rows = list(await db.execute(select(models.User, models.AuthToken).where(
        (models.AuthToken.token == token) & (models.User.id == models.AuthToken.user_id))))
    return rows[0][0] if rows else []
