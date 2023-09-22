from pydantic import UUID4
from app.ai.models import AiCoaching, AiCoachingLike
from app.models.community import Post
from app.session import Transactional
from sqlalchemy import delete, select, func, case, and_, update
from sqlalchemy.orm import with_expression
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.ecs_log import logger


@Transactional()
async def create_ai_coaching(result: dict, session: AsyncSession):
    ai_coaching_obj = AiCoaching(**result)  # type: ignore

    session.add(ai_coaching_obj)
    await session.commit()
    logger.debug(f"ai coaching created: {ai_coaching_obj}")


@Transactional()
async def get_all_ai_coaching(session: AsyncSession):
    stmt = select(AiCoaching)
    ai_coachings = await session.execute(stmt)
    return ai_coachings.scalars().all()


@Transactional()
async def get_ai_coaching_where_post_id(post_id: int, user_id: UUID4 | None, session: AsyncSession):
    stmt = (
        select(AiCoaching)
        .join_from(AiCoaching, AiCoachingLike, isouter=True, onclause=AiCoaching.id == AiCoachingLike.ai_coaching_id)
        .options(
            with_expression(
                AiCoaching.like_cnt,
                func.count(
                    case(
                        (AiCoachingLike.is_liked == 1, AiCoachingLike.id),
                        else_=None,
                    ).distinct()
                ),
            )
        )
        .group_by(AiCoaching.id)
        .order_by(AiCoaching.created_at.desc())
        .where(AiCoaching.post_id == post_id)
    )
    if user_id is not None:
        stmt = stmt.options(
            with_expression(
                AiCoaching.is_liked,
                func.max(
                    case(
                        (and_(AiCoachingLike.user_id == user_id, AiCoachingLike.is_liked == 1), 1),
                        (and_(AiCoachingLike.is_liked == 0), 0),
                        else_=-1,
                    ),
                ),
            )
        )
    ai_coaching = await session.execute(stmt)
    return ai_coaching.scalar_one_or_none()


@Transactional()
async def get_ai_coaching_where_id(id: int, user_id: UUID4 | None, session: AsyncSession):
    stmt = (
        select(AiCoaching)
        .join_from(AiCoaching, AiCoachingLike, isouter=True, onclause=AiCoaching.id == AiCoachingLike.ai_coaching_id)
        .options(
            with_expression(
                AiCoaching.like_cnt,
                func.count(
                    case(
                        (AiCoachingLike.is_liked == 1, AiCoachingLike.id),
                        else_=None,
                    ).distinct()
                ),
            )
        )
        .group_by(AiCoaching.id)
        .order_by(AiCoaching.created_at.desc())
        .where(AiCoaching.id == id)
    )
    if user_id is not None:
        stmt = stmt.options(
            with_expression(
                AiCoaching.is_liked,
                func.max(
                    case(
                        (and_(AiCoachingLike.user_id == user_id, AiCoachingLike.is_liked == 1), 1),
                        (and_(AiCoachingLike.is_liked == 0), 0),
                        else_=-1,
                    ),
                ),
            )
        )
    ai_coaching = await session.execute(stmt)
    return ai_coaching.scalar_one()


@Transactional()
async def update_post_summary_where_id(id: int, summary: str, session: AsyncSession):
    stmt = update(Post).where(Post.id == id).values(summary=summary)
    await session.execute(stmt)
    await session.commit()
    logger.debug(f"post summary updated: {id}")


async def get_like_where_ai_coaching_id_and_user_id(
    ac_id: int, u_id: int, session: AsyncSession
) -> AiCoachingLike | None:
    stmt = select(AiCoachingLike).where(
        AiCoachingLike.ai_coaching_id == ac_id,
        AiCoachingLike.user_id == u_id,
    )
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


@Transactional()
async def create_or_update_like(ai_coaching_id: int, user_id: int, like: int, session: AsyncSession):
    ai_coaching_like: AiCoachingLike | None = await get_like_where_ai_coaching_id_and_user_id(
        ai_coaching_id, user_id, session=session
    )

    if ai_coaching_like is None:
        # FIXME: mypy
        ai_coaching_like = AiCoachingLike(ai_coaching_id=ai_coaching_id, user_id=user_id, is_liked=like)  # type: ignore
        session.add(ai_coaching_like)
    else:
        if ai_coaching_like.is_liked == like:
            return ai_coaching_like
        ai_coaching_like.is_liked = like

    await session.commit()
    await session.refresh(ai_coaching_like)

    return ai_coaching_like


@Transactional()
async def delete_like_where_ai_coaching_id_and_user_id(ai_coaching_id: int, user_id: int, session: AsyncSession):
    stmt = delete(AiCoachingLike).where(
        AiCoachingLike.ai_coaching_id == ai_coaching_id,
        AiCoachingLike.user_id == user_id,
    )
    await session.execute(stmt)
    return
