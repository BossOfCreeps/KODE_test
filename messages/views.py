from functools import wraps

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from account.crud import get_user
from account.models import User
from constants import MESSAGES_LIMIT, Scheme404
from database import get_db
from messages.crud import add_like, get_messages, create_message, delete_message, get_message, del_like
from messages.lib import message_exist, user_exist
from messages.models import Message
from messages.schemas import Like, StatusOK, MessageFull, MassageCreate, MessagesScheme

router = APIRouter()


@router.get("/messages", response_model=MessagesScheme)
async def list_messages_endpoint(offset: int = 0, limit: int = MESSAGES_LIMIT, db: AsyncSession = Depends(get_db)):
    return {"data": await get_messages(db, limit=limit, offset=offset), "messages_lem": len(await get_messages(db))}


@router.get("/message/{message_id}", response_model=MessageFull, responses={404: {"model": Scheme404}})
@message_exist
async def get_message_endpoint(message: Message = Depends(get_message), db: AsyncSession = Depends(get_db)):
    return await message.serialize(db)


@router.post("/message", response_model=MessageFull, responses={404: {"model": Scheme404}})
@user_exist
async def add_message_endpoint(message: MassageCreate, db: AsyncSession = Depends(get_db),
                               user: User = Depends(get_user)):
    if not (message.text or message.files or message.url):
        raise HTTPException(status_code=404, detail="Must be text or files or url")

    return await (await create_message(db=db, message=message, user_id=user.id)).serialize(db)


@router.delete("/message/{message_id}", response_model=StatusOK, responses={404: {"model": Scheme404}})
@message_exist
async def delete_message_endpoint(message: Message = Depends(get_message), db: AsyncSession = Depends(get_db),
                                  user: User = Depends(get_user)):
    if message.user_id != user.id:
        raise HTTPException(status_code=404, detail="This user dont has access to message")

    await delete_message(db=db, message_id=message.id)
    return {"status": "ok"}


@router.post("/message/like/{message_id}", response_model=Like, responses={404: {"model": Scheme404}})
@message_exist
@user_exist
async def like_endpoint(message: Message = Depends(get_message), db: AsyncSession = Depends(get_db),
                        user: User = Depends(get_user)):
    return {"like": await add_like(db=db, message_id=message.id, user_id=user.id)}


@router.post("/message/dislike/{message_id}", response_model=Like, responses={404: {"model": Scheme404}})
@message_exist
@user_exist
async def dislike_endpoint(message: Message = Depends(get_message), db: AsyncSession = Depends(get_db),
                           user: User = Depends(get_user)):
    return {"like": await del_like(db=db, message_id=message.id, user_id=user.id)}
