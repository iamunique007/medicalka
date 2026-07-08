from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post, Like

async def get_like_count_by_post_id(db: AsyncSession, id: UUID) -> int:
    result = await db.execute(select(func.count()).select_from(Like).where(Like.post_id == id))

    return result.scalar_one()

 
async def get_post_by_id(db: AsyncSession, id: UUID) -> Post | None:
    result = await db.execute(select(Post).where(Post.id == id))
    return result.scalar_one_or_none()


async def list_posts(
    db: AsyncSession,
    page: int,
    page_size: int,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> tuple[list[Post], int]:
    conditions = []

    if search:
        pattern = f"%{search}%"
        conditions.append(or_(Post.title.ilike(pattern), Post.content.ilike(pattern)))
    if date_from is not None:
        conditions.append(Post.created_at >= date_from)
    if date_to is not None:
        conditions.append(Post.created_at <= date_to)

    count_query = select(func.count(Post.id))
    if conditions:
        count_query = count_query.where(*conditions)
    total = (await db.execute(count_query)).scalar_one()

    offset = (page - 1) * page_size
    items_query = select(Post)
    if conditions:
        items_query = items_query.where(*conditions)
    items_query = (
        items_query.order_by(Post.created_at.desc()).limit(page_size).offset(offset)
    )

    result = await db.execute(items_query)
    posts = list(result.scalars().all())

    return posts, total