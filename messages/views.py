from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from account.crud import get_user_by_token
from constants import MESSAGES_LIMIT, Scheme404
from database import get_db
from messages import schemas, crud

router = APIRouter()


@router.get("/messages", response_model=list[schemas.MessageForList])
def list_messages(offset: int = 0, limit: int = MESSAGES_LIMIT, db: Session = Depends(get_db)):
    return crud.get_messages(db, limit=limit, offset=offset)


@router.get("/message", response_model=schemas.MessageFull, responses={404: {"model": Scheme404}})
def get_message(message_id: int, db: Session = Depends(get_db)):
    mes = crud.get_message_by_id(db=db, message_id=message_id)
    if not mes:
        raise HTTPException(status_code=404, detail="Message not found")
    return mes.serialize()


@router.post("/message", response_model=schemas.MessageFull, responses={404: {"model": Scheme404}})
def create_message(message: schemas.MassageCreate, db: Session = Depends(get_db), AuthToken: str = Header(None)):
    if not (message.text or message.files or message.url):
        raise HTTPException(status_code=404, detail="Must be text or files or url")

    user = get_user_by_token(db, user_token=AuthToken)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return crud.create_message(db=db, message=message, user_id=user.id).serialize()


@router.delete("/message", response_model=schemas.StatusOK, responses={404: {"model": Scheme404}})
def delete_message(message_id: int, db: Session = Depends(get_db), AuthToken: str = Header(None)):
    mes = crud.get_message_by_id(db=db, message_id=message_id)
    if not mes:
        raise HTTPException(status_code=404, detail="Message not found")

    user = get_user_by_token(db, user_token=AuthToken)
    if mes.user_id != user.id:
        raise HTTPException(status_code=404, detail="This user dont has access to message")

    crud.delete_message(db=db, message_id=message_id)
    return {"status": "ok"}


@router.post("/message/like", response_model=schemas.Like, responses={404: {"model": Scheme404}})
def tap_like(message_id: int, db: Session = Depends(get_db), AuthToken: str = Header(None)):
    mes = crud.get_message_by_id(db=db, message_id=message_id)
    if not mes:
        raise HTTPException(status_code=404, detail="Message not found")

    user = get_user_by_token(db, user_token=AuthToken)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"like": crud.tap_like(db=db, message_id=message_id, user_id=user.id)}
