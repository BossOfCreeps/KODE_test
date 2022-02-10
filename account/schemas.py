from pydantic import BaseModel


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class AuthToken(BaseModel):
    token: str

    class Config:
        orm_mode = True
