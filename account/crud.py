from random import choice
from string import ascii_letters, digits

from sqlalchemy.orm import Session
import hashlib
from account import models, schemas
from constants import AUTH_TOKEN_LENGTH


def get_user_by_login(db: Session, login: str) -> models.User:
    return db.query(models.User).filter(models.User.login == login).first()


def create_user(db: Session, user_scheme: schemas.UserCreate) -> models.User:
    db_user = models.User(login=user_scheme.login, password=hashlib.sha256(user_scheme.password.encode()).hexdigest())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_auth_token(db: Session, user: models.User) -> models.AuthToken:
    def get_unique_token():
        temp_token = ''.join(choice(ascii_letters + digits) for _ in range(AUTH_TOKEN_LENGTH))
        # check unique
        if not db.query(models.AuthToken).filter(models.AuthToken.token == temp_token).first():
            return temp_token
        else:
            return get_unique_token()

    db_token = models.AuthToken(user_id=user.id, token=get_unique_token())
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_user_by_token(db: Session, user_token: str) -> models.User:
    return db.query(models.AuthToken).filter(models.AuthToken.token == user_token).first()
