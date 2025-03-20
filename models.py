from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True, unique=True)
    email = Column(String, index=True, unique=True)
    full_name = Column(String)
    hashed_password = Column(String)

    messages = relationship('MessageModel', back_populates='user', cascade='all, delete-orphan')

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    full_name: str | None = None

class MessageModel(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(String, nullable=False)

    user = relationship('User', back_populates='messages')

class Message(BaseModel):
    message: str

    class Config:
        orm_mode = True
