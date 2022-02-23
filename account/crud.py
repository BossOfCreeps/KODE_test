from datetime import datetime, timedelta
from hashlib import sha256
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from account import models, schemas
from database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="account/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "b600e45fcf96f62053cb8bc13f6f28911dbe23057a6d82ae38a046c76e86a3b9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


async def create_auth_token(db: AsyncSession, user: models.User, expires_delta: Optional[timedelta] = None) -> str:
    to_e = {"sub": user.login, "exp": datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))}
    db_token = models.AuthToken(user_id=user.id, token=jwt.encode(to_e, SECRET_KEY, algorithm=ALGORITHM))
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token.token


async def get_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Optional[models.User]:
    rows = list(await db.execute(select(models.User, models.AuthToken).where(
        (models.AuthToken.token == token) & (models.User.id == models.AuthToken.user_id))))
    return rows[0][0] if rows else []
