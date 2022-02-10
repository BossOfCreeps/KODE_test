from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from account import schemas, crud
from constants import Scheme404
from database import get_db

router = APIRouter()


@router.post("/account/login", response_model=schemas.AuthToken, responses={404: {"model": Scheme404}})
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_login(db, login=user.login)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not db_user.check_user_password(user.password):
        raise HTTPException(status_code=404, detail="Bad password")

    return crud.create_auth_token(db, user=db_user)


@router.post("/account/reg", response_model=schemas.AuthToken, responses={400: {"model": Scheme404}})
def reg(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_login(db, login=user.login):
        raise HTTPException(status_code=400, detail="Login already registered")

    return crud.create_auth_token(db, user=crud.create_user(db, user_scheme=user))
