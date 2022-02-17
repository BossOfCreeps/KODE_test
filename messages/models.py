from sqlalchemy import Column, Integer, String, ForeignKey, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="messages")
    files = relationship("MessageFile", back_populates="message")
    url = relationship("MessageUrl", back_populates="message", uselist=False)

    likes = relationship("Like", back_populates="message")

    async def serialize(self, db: AsyncSession) -> dict:
        files = [el[0] for el in list(await db.execute(select(MessageFile).where(MessageFile.message_id == self.id)))]
        url_list = list(await db.execute(select(MessageUrl).where(MessageUrl.message_id == self.id)))
        url = (await url_list[0][0].serialize(db)) if url_list else None
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "files": [await file.serialize(db) for file in files],
            "url": url
        }


class MessageFile(Base):
    __tablename__ = "message_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))

    message = relationship("Message", back_populates="files")

    async def serialize(self, _: AsyncSession) -> dict:
        return {"id": self.id, "url": self.url}


class MessageUrl(Base):
    __tablename__ = "message_urls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image = Column(String)
    title = Column(Text)
    message_id = Column(Integer, ForeignKey("messages.id"))

    message = relationship("Message", back_populates="url")

    async def serialize(self, _: AsyncSession) -> dict:
        return {"id": self.id, "image": self.image, "title": self.title}


class Like(Base):
    __tablename__ = "message_likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message_id = Column(Integer, ForeignKey("messages.id"))

    message = relationship("Message", back_populates="likes")
    user = relationship("User", back_populates="likes")
