from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Comment


async def get_comment_by_id(db: AsyncSession, id: UUID) -> Comment | None:
    result = await db.execute(select(Comment).where(Comment.id == id))
    return result.scalar_one_or_none()


async def get_comments_by_post_id(db: AsyncSession, post_id: UUID) -> list[Comment]:
    query = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())