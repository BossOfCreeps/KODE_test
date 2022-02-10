from sqlalchemy import Column, Integer, String, ForeignKey, Text
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

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "files": [file.serialize() for file in self.files],
            "url": self.url.serialize() if self.url else None
        }


class MessageFile(Base):
    __tablename__ = "message_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String)
    message_id = Column(Integer, ForeignKey("messages.id"))

    message = relationship("Message", back_populates="files")

    def serialize(self) -> dict:
        return {"id": self.id, "url": self.url}


class MessageUrl(Base):
    __tablename__ = "message_urls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image = Column(String)
    title = Column(Text)
    message_id = Column(Integer, ForeignKey("messages.id"))

    message = relationship("Message", back_populates="url")

    def serialize(self) -> dict:
        return {"id": self.id, "image": self.image, "title": self.title}


class Like(Base):
    __tablename__ = "message_likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message_id = Column(Integer, ForeignKey("messages.id"))

    message = relationship("Message", back_populates="likes")
    user = relationship("User", back_populates="likes")
