from datetime import datetime
from enum import Enum
from typing import Annotated
from fastapi import Form
from pydantic import UUID4, BaseModel, ConfigDict, Field
import ujson


class CommunityEnum(int, Enum):
    WORKOUT = 1
    DIET = 2  # 식단
    FREE = 3
    ANONYMOUS = 4


class AuthorRead(BaseModel):
    id: UUID4
    username: str
    profile_pic: str | None = None

    class Config:
        orm_mode = True


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
    title: Annotated[str, Form(min_length=1, max_length=100)]
    content: Annotated[str, Form(min_length=1, max_length=1000)]
    want_ai_coach: Annotated[bool | None, Form(description="AI 코치를 원하는지 여부")] = None
    video: Annotated[list[str] | None, Form(description="video url. ex) https://www.youtube.com/watch?v=1234")] = None

    def create_dict(self, user_id: UUID4) -> dict:
        d = self.model_dump(exclude_unset=True, exclude={"want_ai_coach"})
        d["user_id"] = user_id
        if "video" in d and d["video"] is not None:
            d["video"] = ujson.dumps(d["video"])
        return d


class PostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1, max_length=1000)
    video: list[str] | None = Field(None, description="video url. ex) https://www.youtube.com/watch?v=1234")

    def create_dict(self) -> dict:
        d = self.model_dump(exclude_unset=True)
        if "video" in d and d["video"] is not None:
            d["video"] = ujson.dumps(d["video"])
        return d


class PostRead(PostBase):
    id: int
    image: list[str] | None = Field(None, description="Json encoded list of image urls")
    # Json encoded list of video urls
    video: list[str] | None = Field(None, description="video url. ex) https://www.youtube.com/watch?v=1234")
    available: bool
    created_at: datetime
    updated_at: datetime
    user: AuthorRead | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class PostResponse(PostRead):
    like_cnt: int | None = 0
    comment_cnt: int | None = 0
    is_liked: int = -1


class CommentBase(BaseModel):
    post_id: int
    content: str


class CommentCreate(CommentBase):
    post_id: int = Field(...)
    content: str = Field(...)


class CommentUpdate(BaseModel):
    content: str | None = Field(..., min_length=1)


class CommentRead(CommentBase):
    id: int
    available: bool
    created_at: datetime
    updated_at: datetime
    user: AuthorRead | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class CommentResponse(CommentRead):
    like_cnt: int | None = 0
    comment_cnt: int | None = 0
    is_liked: int | None = -1


class GetCommentsResponse(BaseModel):
    total: int
    items: list[CommentResponse]
    next_cursor: int | None


class GetPostsResponse(BaseModel):
    total: int
    items: list[PostResponse]
    next_cursor: int | None
