import warnings
from typing import Optional

from opengraph_py3 import OpenGraph
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from messages import models, schemas
from messages.lib import save_file_from_url, save_file_from_base64


async def get_messages(db: AsyncSession, limit: int, offset: int) -> list[schemas.MessageForList]:
    return list(el[0] for el in tuple(await db.execute(select(models.Message))))[offset:][:limit]


async def create_message(db: AsyncSession, message: schemas.MassageCreate, user_id: int) -> models.Message:
    message_dict = message.dict()

    # файлы передаются в base64
    files = [models.MessageFile(url=save_file_from_base64(**file)) for file in message_dict["files"]]

    url = None
    # Skip warning because lib always say, that bs4 use lxml parser
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Get image and title from url by open graph
        graph = OpenGraph(url=message_dict["url"], parser="lxml")
        if graph.is_valid() and "image" in graph:
            url = models.MessageUrl(
                image=save_file_from_url(graph["image"]),
                title=graph["title"] if "title" in graph else None
            )

    db_item = models.Message(text=message_dict["text"], files=files, url=url, user_id=user_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[models.Message]:
    rows = tuple(await db.execute(select(models.Message).where(models.Message.id == message_id)))
    return rows[0][0] if rows else None


async def delete_message(db: AsyncSession, message_id: int) -> None:
    await db.execute(delete(models.Message).where(models.Message.id == message_id))


async def tap_like(db: AsyncSession, message_id: int, user_id: int) -> bool:
    has_like = tuple(await db.execute(
        select(models.Like).where((models.Like.message_id == message_id) & (models.Like.user_id == user_id))))

    if has_like:
        await db.execute(delete(models.Like).where((models.Like.message_id == message_id) &
                                                   (models.Like.user_id == user_id)))
    else:
        db.add(models.Like(message_id=message_id, user_id=user_id))
        await db.commit()
    return not has_like
