from pydantic import UUID4
from app.ai.models import AiCoaching
from app.session import Transactional
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.ecs_log import logger


@Transactional()
async def create_ai_coaching(result: dict, session: AsyncSession):
    ai_coaching_obj = AiCoaching(**result)  # type: ignore

    session.add(ai_coaching_obj)
    await session.commit()
    logger.debug(f"ai coaching created: {ai_coaching_obj}")
