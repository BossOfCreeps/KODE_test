import hashlib

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    login = Column(String, unique=True, index=True)
    password = Column(String)

    messages = relationship("Message", back_populates="user")
    auth_tokens = relationship("AuthToken", back_populates="user")
    likes = relationship("Like", back_populates="user")

    def check_user_password(self, password: str) -> bool:
        return self.password == hashlib.sha256(password.encode()).hexdigest()


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True)

    user = relationship("User", back_populates="auth_tokens")
