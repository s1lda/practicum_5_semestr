from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from sqlalchemy import Column, String, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

# SQLAlchemy модели
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    role = Column(SQLAlchemyEnum(Role), default=Role.USER)
    vk_id = Column(String, nullable=True)
    disabled = Column(Boolean, default=False)
    refresh_token = Column(String, nullable=True)

# Pydantic модели
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    role: Role
    vk_id: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[Role] = None 