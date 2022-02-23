from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import get_user
from account.models import User
from constants import MESSAGES_LIMIT, Scheme404
from database import get_db
from messages.crud import get_message_by_id, tap_like, get_messages, create_message, delete_message
from messages.schemas import MessageForList, Like, StatusOK, MessageFull, MassageCreate

router = APIRouter()


@router.get("/messages", response_model=list[MessageForList])
async def list_messages(offset: int = 0, limit: int = MESSAGES_LIMIT, db: AsyncSession = Depends(get_db)):
    return await get_messages(db, limit=limit, offset=offset)


@router.get("/message/{message_id}", response_model=MessageFull, responses={404: {"model": Scheme404}})
async def get_message(message_id: int, db: AsyncSession = Depends(get_db)):
    mes = await get_message_by_id(db=db, message_id=message_id)
    if not mes:
        raise HTTPException(status_code=404, detail="Message not found")
    return await mes.serialize(db)


@router.post("/message", response_model=MessageFull, responses={404: {"model": Scheme404}})
async def add_message(mes: MassageCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_user)):
    if not (mes.text or mes.files or mes.url):
        raise HTTPException(status_code=404, detail="Must be text or files or url")

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return await (await create_message(db=db, message=mes, user_id=user.id)).serialize(db)


@router.delete("/message/{message_id}", response_model=StatusOK, responses={404: {"model": Scheme404}})
async def del_message(message_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_user)):
    mes = await get_message_by_id(db=db, message_id=message_id)
    if not mes:
        raise HTTPException(status_code=404, detail="Message not found")

    if mes.user_id != user.id:
        raise HTTPException(status_code=404, detail="This user dont has access to message")

    await delete_message(db=db, message_id=message_id)
    return {"status": "ok"}


@router.post("/message/like/{message_id}", response_model=Like, responses={404: {"model": Scheme404}})
async def like(message_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_user)):
    mes = await get_message_by_id(db=db, message_id=message_id)
    if not mes:
        raise HTTPException(status_code=404, detail="Message not found")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"like": await tap_like(db=db, message_id=message_id, user_id=user.id)}
