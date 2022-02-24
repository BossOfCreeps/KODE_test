from typing import Optional

from pydantic import BaseModel


class MessageFile(BaseModel):
    id: int
    url: str


class MessageUrl(BaseModel):
    id: int
    image: str
    title: Optional[str] = None


class MassageBase(BaseModel):
    text: Optional[str] = None


class MessageForList(MassageBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class MessagesScheme(BaseModel):
    data: list[MessageForList]
    messages_lem: int


class MessageFull(MassageBase):
    id: int
    user_id: int
    url: Optional[MessageUrl] = None
    files: Optional[list[MessageFile]] = []

    class Config:
        orm_mode = True


class Like(BaseModel):
    like: bool


class StatusOK(BaseModel):
    status: str
