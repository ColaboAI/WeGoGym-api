from typing_extensions import Annotated
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Form, Query, UploadFile, File
from typing import List

from pydantic import UUID4, Json
from app.utils.common import normalize_post
from app.utils.pagination import limit_offset_query
from app.utils.user import get_user_id_from_request
from app.schemas.community import (
    CommunityCreate,
    CommunityRead,
    CommentResponse,
    GetCommentsResponse,
    GetPostsResponse,
    PostCreate,
    PostResponse,
    CommentCreate,
    CommentUpdate,
    PostUpdate,
)
from app.services import community_service
from app.core.fastapi.dependencies.premission import (
    AllowAll,
    IsAuthenticated,
    IsAdmin,
    PermissionDependency,
)
from app.ai import service as ai_service

router = APIRouter(prefix="/communities", tags=["community"])


@router.get(
    "",
    status_code=200,
    response_model=List[CommunityRead],
    summary="Get all communities",
)
async def get_all_communities():
    return await community_service.get_all_communities()


@router.post(
    "",
    status_code=201,
    response_model=CommunityRead,
    summary="Create new community",
    description="Only admin can create new community",
    dependencies=[
        Depends(PermissionDependency([IsAdmin])),
    ],
)
async def post_community(
    community: CommunityCreate,
):
    community_dict = community.model_dump()
    return await community_service.create_community(community_dict)


@router.get(
    "/posts",
    status_code=200,
    response_model=GetPostsResponse,
    summary="Get posts with pagination",
    dependencies=[
        Depends(PermissionDependency([AllowAll])),
    ],
)
async def get_posts_where_community_id(
    community_id: int | None = Query(None, description="community id"),
    pagination: dict = Depends(limit_offset_query),
    user_id: UUID4 | None = Depends(get_user_id_from_request),
):
    total, posts, next_cursor = await community_service.get_posts_where_community_id(
        community_id=community_id, **pagination, user_id=user_id
    )
    posts = normalize_post(posts)
    return {
        "total": total,
        "items": posts,
        "next_cursor": next_cursor,
    }


@router.post(
    "/posts",
    status_code=201,
    response_model=PostResponse,
    summary="Create new post",
    description="Only authenticated user can create new post",
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def post_post(
    background_task: BackgroundTasks,
    post: Annotated[Json[PostCreate], Form(media_type="multipart/form-data")],
    images: list[UploadFile] = File(None, description="Post Images"),  # FIXME: Is definition correct?
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    post_obj = await community_service.create_post(user_id, post, images)
    if post.want_ai_coach is True and post_obj is not None and len(post_obj.content) > 5:
        # make ai coaching
        background_task.add_task(
            ai_service.make_ai_coaching,
            user_input=f"{post_obj.title}\n{post_obj.content}",
            user_id=user_id,
            post_id=post_obj.id,
            model_name="gpt-4",
        )

    return normalize_post(post_obj)


@router.get(
    "/posts/{post_id}",
    status_code=200,
    response_model=PostResponse,
    dependencies=[
        Depends(PermissionDependency([AllowAll])),
    ],
)
async def get_post(post_id: int, user_id: UUID4 | None = Depends(get_user_id_from_request)):
    post = await community_service.get_post_with_like_cnt_where_id(post_id, user_id=user_id)

    return normalize_post(post)


@router.post(
    "/posts/{post_id}/update",
    status_code=200,
    response_model=PostResponse,
    summary="Update post",
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def update_post_where_id(
    post_id: int,
    post_update: Annotated[Json[PostUpdate], Form(media_type="multipart/form-data")],
    images: list[UploadFile] = File(None, description="Post Images"),  # FIXME: same as above
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    return normalize_post(await community_service.update_post_where_id(post_id, user_id, post_update, images))


@router.delete(
    "/posts/{post_id}",
    status_code=204,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def delete_post(
    post_id: int,
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    await community_service.delete_post_where_id(post_id, user_id)
    return {"message": "success"}


@router.post(
    "/posts/{post_id}/like",
    status_code=201,
    response_model=PostResponse,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def post_post_like(
    post_id: int,
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    return normalize_post(await community_service.create_or_update_post_like(post_id, user_id, True))


@router.post(
    "/posts/{post_id}/unlike",
    status_code=201,
    response_model=PostResponse,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def post_post_unlike(
    post_id: int,
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    return normalize_post(await community_service.create_or_update_post_like(post_id, user_id, False))


@router.get(
    "/comments",
    status_code=200,
    response_model=GetCommentsResponse,
    summary="Get comments with pagination",
)
async def get_comments(
    post_id: Annotated[int, Query(..., description="post id")],
    user_id: Annotated[UUID4 | None, Depends(get_user_id_from_request)],
    pagination: dict = Depends(limit_offset_query),
):
    total, items, next_cursor = await community_service.get_comments_where_post_id(
        post_id=post_id, **pagination, user_id=user_id
    )
    return {"total": total, "items": items, "next_cursor": next_cursor}


@router.get(
    "/comments/{comment_id}",
    status_code=200,
    response_model=CommentResponse,
)
async def get_comment(comment_id: int, user_id: UUID4 | None = Depends(get_user_id_from_request)):
    return await community_service.get_comment_where_id(comment_id)


@router.post(
    "/comments",
    status_code=201,
    response_model=CommentResponse,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def post_comment(
    comment: CommentCreate,
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    return await community_service.create_comment(user_id, comment)


@router.patch(
    "/comments/{comment_id}",
    status_code=200,
    response_model=CommentResponse,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def patch_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    return await community_service.update_comment_where_id(comment_id, user_id, comment_update)


@router.delete(
    "/comments/{comment_id}",
    status_code=204,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def delete_comment(
    comment_id: int,
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    await community_service.delete_comment_where_id(comment_id, user_id)
    return {"message": "success"}


@router.post(
    "/comments/{comment_id}/like",
    status_code=201,
    response_model=CommentResponse,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def post_comment_like(
    comment_id: int,
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    return await community_service.create_or_update_comment_like(comment_id, user_id, 1)


@router.post(
    "/comments/{comment_id}/unlike",
    status_code=201,
    response_model=CommentResponse,
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def post_comment_unlike(
    comment_id: int,
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    return await community_service.create_or_update_comment_like(comment_id, user_id, 0)


@router.get(
    "/{community_id}",
    status_code=200,
    response_model=CommunityRead,
    summary="Get community where community_id",
)
async def get_community(community_id: int):
    return await community_service.get_community_where_id(community_id)
