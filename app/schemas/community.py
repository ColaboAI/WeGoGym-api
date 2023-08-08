from datetime import datetime
from enum import Enum
from re import A
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class CommunityEnum(int, Enum):
    WORKOUT = 1
    DIET = 2  # 식단
    FREE = 3
    ANONYMOUS = 4


class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    type: int = Field(CommunityEnum.WORKOUT, description="게시판 타입(운동, 식단, 자유, 익명)")

    class Config:
        orm_mode = True

    # password: Optional[str] = Field(None, description="관리자 비밀번호")


class CommunityRead(BaseModel):
    id: int
    type: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


class PostBase(BaseModel):
    community_id: int
    title: str
    content: str


class PostCreate(PostBase):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=1000)


class PostUpdate(BaseModel):
    id: int = Field(...)
    community_id: int = Field(...)
    title: Optional[str] = Field(min_length=1, max_length=200)
    content: Optional[str] = Field(min_length=1, max_length=1000)


class PostRead(PostBase):
    id: int
    user_id: int
    available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PostResponse(PostRead):
    like_cnt: int = 0


class CommentBase(BaseModel):
    post_id: int
    content: str


class CommentCreate(CommentBase):
    post_id: int = Field(...)
    content: str = Field(...)


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(..., min_length=1)


class CommentRead(CommentBase):
    id: int
    user_id: int
    available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CommentResponse(CommentRead):
    like_cnt: int = 0


class GetCommentsResponse(BaseModel):
    result: List[CommentResponse]
    total_count: int
    has_next: bool


class GetPostsResponse(BaseModel):
    result: List[PostResponse]
    total_count: int
    has_next: bool
