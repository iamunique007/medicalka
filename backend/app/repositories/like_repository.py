from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Like


async def get_like(db: AsyncSession, user_id: UUID, post_id: UUID) -> Like | None:
    result = await db.execute(
        select(Like).where((Like.user_id == user_id) & (Like.post_id == post_id))
    )
    return result.scalar_one_or_none()