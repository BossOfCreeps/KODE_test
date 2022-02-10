import warnings

from opengraph_py3 import OpenGraph
from sqlalchemy.orm import Session

from messages import models, schemas
from messages.lib import save_file_from_url, save_file_from_base64


def get_messages(db: Session, limit: int, offset: int) -> list[schemas.MessageForList]:
    return db.query(models.Message).offset(offset).limit(limit).all()


def create_message(db: Session, message: schemas.MassageCreate, user_id: int) -> models.Message:
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
    db.commit()
    db.refresh(db_item)
    return db_item


def get_message_by_id(db: Session, message_id: int) -> models.Message:
    return db.query(models.Message).filter(models.Message.id == message_id).first()


def delete_message(db: Session, message_id: int) -> None:
    db.delete(db.query(models.Message).filter(models.Message.id == message_id).first())
    db.commit()


def tap_like(db: Session, message_id: int, user_id: int) -> bool:
    has_like = db.query(models.Like).filter(models.Like.message_id == message_id) \
        .filter(models.Like.user_id == user_id).first()

    if has_like:
        db.delete(has_like)
    else:
        db_item = models.Like(message_id=message_id, user_id=user_id)
        db.add(db_item)

    db.commit()
    return not has_like
