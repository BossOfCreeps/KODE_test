from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class AuthToken(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True
