import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from account import models as account_models
from messages import models as messages_models


async def create_user(db_session: AsyncSession, login: str, password: str) -> tuple[int, str]:
    user = account_models.User(login=login, password=hashlib.sha256(password.encode()).hexdigest())
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = account_models.AuthToken(user_id=user.id, token=f"random token for {login}")
    db_session.add(token)
    await db_session.commit()
    await db_session.refresh(token)
    return user.id, token.token


async def create_message(db_session: AsyncSession, user_id: int, text: str) -> messages_models.Message:
    message = messages_models.Message(user_id=user_id, text=text)
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message
