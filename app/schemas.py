from pydantic import BaseModel, Field, EmailStr, conint
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, List


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = False


class CreatePost(PostBase):
    pass


class UserBase(BaseModel):
    email: EmailStr


class CreateUser(UserBase):
    password: str


class ResponseUser(UserBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ResponsePost(PostBase):
    id: UUID = Field(default_factory=uuid4)
    published: bool
    owner_id: UUID
    owner: ResponseUser
    created_at: datetime

    class Config:
        orm_mode = True


class ResponsePostVote(PostBase):
    Post: ResponsePost
    votes: int

    class Config:
        orm_mode = True


class ResponsePostVote2(ResponsePost):
    votes: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: UUID
    dir: conint(le=1)
