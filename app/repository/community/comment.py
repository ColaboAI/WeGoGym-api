from uuid import UUID
from app.session import Transactional
from app.models.community import Comment, CommentLike
from sqlalchemy import delete, select, case, func, update
from sqlalchemy.orm import with_expression
from sqlalchemy.ext.asyncio import AsyncSession


@Transactional()
async def get_list_with_like_cnt_where_post_id(
    post_id: int, limit: int, offset: int, session: AsyncSession
):
    stmt = (
        select(Comment)
        .join_from(
            Comment,
            CommentLike,
            onclause=CommentLike.comment_id == Comment.id,
            isouter=True,
        )
        .options(
            with_expression(
                Comment.like_cnt,
                func.count(
                    case(
                        (CommentLike.is_liked == 1, CommentLike.id),
                        else_=None,
                    ).distinct()
                ),
            )
        )
        .group_by(Comment.id)
        .order_by(Comment.created_at.desc())
        .where(Comment.post_id == post_id)
    )
    stmt = stmt.limit(limit).offset(offset)
    res = await session.execute(stmt)
    return res.scalars().all()


@Transactional()
async def create(comment_data: dict, session: AsyncSession):
    post = Comment(**comment_data)
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@Transactional()
async def get_where_id(id: int, session: AsyncSession):
    res = await session.execute(select(Comment).where(Comment.id == id))
    return res.scalar_one()


@Transactional()
async def get_with_like_cnt_where_id(id: int, session: AsyncSession):
    stmt = (
        select(Comment)
        .join_from(
            Comment,
            CommentLike,
            onclause=CommentLike.comment_id == Comment.id,
            isouter=True,
        )
        .options(
            with_expression(
                Comment.like_cnt,
                func.count(
                    case(
                        (CommentLike.is_liked == 1, CommentLike.id),
                        else_=None,
                    ).distinct()
                ),
            )
        )
        .where(Comment.id == id)
        .group_by(Comment.id)
    )

    res = await session.execute(stmt)
    return res.scalar_one()


@Transactional()
async def count_where_post_id(post_id: int, session: AsyncSession):
    stmt = select(func.count(Comment.id)).where(Comment.post_id == post_id)
    res = await session.execute(stmt)
    return res.scalar_one()


@Transactional()
async def update_where_id(comment_id, comment_data: dict, session: AsyncSession):
    stmt = update(Comment).where(Comment.id == comment_id).values(**comment_data)
    await session.execute(stmt)
    return await get_where_id(comment_id, session=session)


@Transactional()
async def delete_where_id(id, session: AsyncSession):
    stmt = delete(Comment).where(Comment.id == id)
    await session.execute(stmt)
    return


@Transactional()
async def get_like_where_comment_id_and_user_id(
    c_id: int, u_id: UUID, session: AsyncSession
):
    stmt = select(CommentLike).where(
        (CommentLike.comment_id == c_id),
        (CommentLike.user_id == u_id),
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


@Transactional()
async def create_or_update_like(
    comment_id: int, user_id: int, is_like: int, session: AsyncSession
):
    comment_like: CommentLike = await get_like_where_comment_id_and_user_id(
        comment_id,
        user_id,
        session=session,
    )
    if comment_like is None:
        comment_like = CommentLike(
            comment_id=comment_id, user_id=user_id, is_liked=is_like
        )
        session.add(comment_like)
    else:
        if comment_like.is_liked == is_like:
            return comment_like.is_liked
        comment_like.is_liked = is_like

    await session.commit()
    await session.refresh(comment_like)
    return comment_like.is_liked


@Transactional()
async def delete_like_where_comment_id_and_user_id(
    comment_id: int, user_id: int, session: AsyncSession
):
    stmt = delete(CommentLike).where(
        (CommentLike.comment_id == comment_id),
        (CommentLike.user_id == user_id),
    )
    await session.execute(stmt)
    return
