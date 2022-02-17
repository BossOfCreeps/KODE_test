from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from account import schemas, crud
from constants import Scheme404
from database import get_db

router = APIRouter()


@router.post("/account/login", response_model=schemas.AuthToken, responses={404: {"model": Scheme404}})
async def login(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_login(db, login=user.login)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not db_user.check_user_password(user.password):
        raise HTTPException(status_code=404, detail="Bad password")

    return await crud.create_auth_token(db, user=db_user)


@router.post("/account/reg", response_model=schemas.AuthToken, responses={400: {"model": Scheme404}})
async def reg(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    if await crud.get_user_by_login(db, login=user.login):
        raise HTTPException(status_code=400, detail="Login already registered")

    return await crud.create_auth_token(db, user=(await crud.create_user(db, user_scheme=user)))
