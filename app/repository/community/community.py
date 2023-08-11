from app.session import Transactional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.community import Community


@Transactional()
async def get_all(session: AsyncSession):
    res = await session.execute(select(Community))
    return res.scalars().all()


@Transactional()
async def get_where_id(id: int, session: AsyncSession):
    res = await session.execute(select(Community).where(Community.id == id))
    return res.scalar_one()


@Transactional()
async def create(community_data: dict, session: AsyncSession):
    community = Community(**community_data)
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community
