import asyncio
from fastapi import UploadFile
import ujson
from pydantic import UUID4
from app.core.exceptions.base import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.core.exceptions.community import PostNotFound
from app.models.community import Comment, Post
from app.schemas.community import CommentCreate, CommentUpdate, PostCreate, PostUpdate
from app.repository.community import community, post, comment
from sqlalchemy.exc import NoResultFound, IntegrityError

from app.utils import aws


async def get_all_communities():
    return await community.get_all()


async def get_community_where_id(id: int):
    return await community.get_where_id(id)


async def create_community(community_data: dict):
    return await community.create(community_data)


async def get_posts_where_community_id(
    community_id: int | None, limit: int, offset: int, user_id: UUID4 | None
):
    try:
        total = await post.count_where_community_id(community_id)
        posts = await post.get_list_with_like_cnt_comment_cnt_where_community_id(
            community_id, limit, offset, user_id
        )

    except NoResultFound as e:
        raise NotFoundException("Community not found") from e

    next_cursor = offset + len(posts) if total and total > offset + len(posts) else None
    return total, posts, next_cursor


async def create_post(
    user_id: UUID4, post_data: PostCreate, images: list[UploadFile] | None
):
    post_dict = post_data.create_dict(user_id)
    try:
        post_obj: Post = await post.create(post_dict)

        if images and len(images) > 0:
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(
                None,
                aws.upload_files_to_s3,
                images,
                f"test/posts/{post_obj.id}",
            )
            image_urls = ujson.dumps(res)

            post_obj = await post.update_where_id(post_obj.id, {"image": image_urls})

        return post_obj
    except IntegrityError as e:
        raise BadRequestException(str(e.orig)) from e


async def get_post_where_id(id: int) -> Post:
    try:
        return await post.get_where_id(id)
    except NoResultFound as e:
        raise PostNotFound from e


async def get_post_with_like_cnt_where_id(id: int, user_id: UUID4 | None = None):
    try:
        return await post.get_with_like_cnt_where_id(id, user_id=user_id)
    except NoResultFound as e:
        raise PostNotFound from e


async def update_post_where_id(
    id: int, user_id: UUID4, post_data: PostUpdate, images: list[UploadFile] | None
):
    post_obj = await get_post_where_id(id)

    if post_obj.user_id != user_id:
        raise ForbiddenException("You are not authorized to update this post")

    post_dict = post_data.create_dict()
    if images and len(images) > 0:
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(
            None,
            aws.upload_files_to_s3,
            images,
            f"test/posts/{post_obj.id}",
        )
        image_urls = ujson.dumps(res)
        post_dict["image"] = image_urls

    new_post_obj: Post = await post.update_where_id(
        id,
        post_dict,
    )
    new_post_obj.like_cnt = post_obj.like_cnt
    return new_post_obj


async def delete_post_where_id(id: int, user_id: UUID4):
    try:
        post_obj: Post = await get_post_where_id(id)
    except NoResultFound as e:
        raise PostNotFound from e
    if post_obj.user_id != user_id:
        raise ForbiddenException("You are not authorized to delete this post")

    await post.delete_where_id(id)


async def create_or_update_post_like(post_id: int, user_id: UUID4, like: int):
    await post.create_or_update_like(post_id, user_id, like)
    return await get_post_with_like_cnt_where_id(post_id, user_id)


async def delete_post_like(post_id: int, user_id: UUID4):
    try:
        await post.delete_like_where_post_id_and_user_id(post_id, user_id)
        return await get_post_with_like_cnt_where_id(post_id, user_id)
    except NoResultFound as e:
        raise PostNotFound from e


async def get_comments_where_post_id(
    post_id: int, user_id: UUID4 | None, limit: int, offset: int
):
    try:
        total = await comment.count_where_post_id(post_id)
        comments = (
            await comment.get_list_with_like_cnt_where_post_id(
                post_id, user_id, limit, offset
            ),
        )

    except NoResultFound as e:
        raise NotFoundException("Post not found") from e

    next_cursor = (
        offset + len(comments) if total and total > offset + len(comments) else None
    )
    return total, comments, next_cursor


async def create_comment(user_id: UUID4, comment_data: CommentCreate):
    comment_ = comment_data.dict()
    comment_["user_id"] = user_id
    try:
        cmt_obj = await comment.create(comment_)
        return cmt_obj
    except IntegrityError as e:
        raise BadRequestException(str(e.orig)) from e


async def get_comment_where_id(id: int):
    return await comment.get_where_id(id)


async def get_comment_with_like_cnt_where_id(id: int, user_id: UUID4 | None = None):
    return await comment.get_with_like_cnt_where_id(id, user_id)


async def update_comment_where_id(id: int, user_id: UUID4, comment_data: CommentUpdate):
    comment_obj: Comment = await get_comment_where_id(id)
    if comment_obj.user_id != user_id:
        raise ForbiddenException("You are not authorized to update this comment")

    return await comment.update_where_id(
        id,
        comment_data.dict(
            exclude_unset=True,
        ),
    )


async def delete_comment_where_id(id: int, user_id: UUID4):
    try:
        comment_obj: Comment = await get_comment_where_id(id)
    except NoResultFound as e:
        raise PostNotFound from e
    if comment_obj.user_id != user_id:
        raise ForbiddenException("You are not authorized to delete this post")

    await comment.delete_where_id(id)


async def create_or_update_comment_like(comment_id: int, user_id: UUID4, like: int):
    try:
        await comment.create_or_update_like(comment_id, user_id, like)
        return await get_comment_with_like_cnt_where_id(comment_id, user_id)
    except IntegrityError as e:
        raise BadRequestException(str(e.orig)) from e


async def delete_comment_like(comment_id: int, user_id: UUID4):
    try:
        await comment.delete_like_where_comment_id_and_user_id(comment_id, user_id)
        return await get_comment_with_like_cnt_where_id(comment_id, user_id)
    except NoResultFound as e:
        raise NotFoundException("Like not found") from e
