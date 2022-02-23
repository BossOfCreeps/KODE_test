from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from account.service import create_auth_token, create_user, get_user_by_login
from account.schemas import UserCreate, Token
from constants import Scheme404
from database import get_db

router = APIRouter()


@router.post("/account/login", response_model=Token, responses={404: {"model": Scheme404}})
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_login(db, login=form_data.username)

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not db_user.check_user_password(form_data.password):
        raise HTTPException(status_code=404, detail="Bad password")

    return {"access_token": await create_auth_token(db, user=db_user), "token_type": "bearer"}


@router.post("/account/reg", response_model=Token, responses={400: {"model": Scheme404}})
async def reg(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_login(db, login=user.username):
        raise HTTPException(status_code=400, detail="Login already registered")

    return {"access_token": await create_auth_token(db, user=(await create_user(db, user_scheme=user))),
            "token_type": "bearer"}
