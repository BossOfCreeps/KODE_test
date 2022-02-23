import warnings
from typing import Optional

from fastapi import Depends
from opengraph_py3 import OpenGraph
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from messages.lib import save_file_from_url, save_file_from_base64
from messages.models import Message, MessageFile, MessageUrl, Like
from messages.schemas import MassageCreate, MessageForList


async def get_message(message_id: int, db: AsyncSession = Depends(get_db)) -> Optional[Message]:
    return await db.scalar(select(Message).where(Message.id == message_id))


async def get_messages(db: AsyncSession, limit: Optional[int] = None, offset: int = 0) -> list[MessageForList]:
    return [mes for mes in (await db.execute(select(Message).limit(limit).offset(offset))).scalars().fetchall()]


async def create_message(db: AsyncSession, message: MassageCreate, user_id: int) -> Message:
    message_dict = message.dict()

    # файлы передаются в base64
    files = [MessageFile(url=save_file_from_base64(**file)) for file in message_dict["files"]]

    url = None
    # Skip warning because lib always say, that bs4 use lxml parser
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Get image and title from url by open graph
        graph = OpenGraph(url=message_dict["url"], parser="lxml")
        if graph.is_valid() and "image" in graph:
            url = MessageUrl(
                image=save_file_from_url(graph["image"]),
                title=graph["title"] if "title" in graph else None
            )

    db_item = Message(text=message_dict["text"], files=files, url=url, user_id=user_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def delete_message(db: AsyncSession, message_id: int) -> None:
    await db.execute(delete(Message).where(Message.id == message_id))


async def add_like(db: AsyncSession, message_id: int, user_id: int) -> bool:
    db.add(Like(message_id=message_id, user_id=user_id))
    await db.commit()
    return True


async def del_like(db: AsyncSession, message_id: int, user_id: int) -> bool:
    await db.execute(delete(Like).where((Like.message_id == message_id) & (Like.user_id == user_id)))
    return False
