from fastapi import APIRouter, Depends, Form, Query, UploadFile
from typing import List

from pydantic import UUID4, Json
from app.utils.common import load_posts_json_fields, normalize_post
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
    community_dict = community.dict()
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
@router.get(
    "/{community_id}",
    status_code=200,
    response_model=CommunityRead,
    summary="Get community where community_id",
)
async def get_community(community_id: int):
    return await community_service.get_community_where_id(community_id)


async def post_post(
    images: list[UploadFile] | None = None,
    post: Json[PostCreate] = Form(...),
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    post_obj = await community_service.create_post(user_id, post, images)
    return normalize_post(post_obj)


@router.get("/posts/{post_id}", status_code=200, response_model=PostResponse)
async def get_post(
    post_id: int, user_id: UUID4 | None = Depends(get_user_id_from_request)
):
    post = await community_service.get_post_with_like_cnt_where_id(
        post_id, user_id=user_id
    )

    return normalize_post(post)


@router.patch(
    "/posts/{post_id}",
    status_code=200,
    response_model=PostResponse,
    response_model_exclude={"like_cnt"},
    summary="Update post",
    dependencies=[
        Depends(PermissionDependency([IsAuthenticated])),
    ],
)
async def patch_post_where_id(
    post_id: int,
    images: list[UploadFile] | None = None,
    post_update: Json[PostUpdate] = Form(...),
    user_id: UUID4 = Depends(get_user_id_from_request),
):
    return normalize_post(
        await community_service.update_post_where_id(
            post_id, user_id, post_update, images
        )
    )


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
    return normalize_post(
        await community_service.create_or_update_post_like(post_id, user_id, True)
    )


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
    return normalize_post(
        await community_service.create_or_update_post_like(post_id, user_id, False)
    )


@router.get(
    "/comments",
    status_code=200,
    response_model=GetCommentsResponse,
    summary="Get comments with pagination",
)
async def get_comments(post_id: int, pagination: dict = Depends(limit_offset_query)):
    total, items, next_cursor = await community_service.get_comments_where_post_id(
        post_id=post_id, **pagination
    )
    return {"total": total, "items": items, "next_cursor": next_cursor}


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
    return await community_service.update_comment_where_id(
        comment_id, user_id, comment_update
    )


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
