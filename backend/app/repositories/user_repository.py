from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_user_by_id(db: AsyncSession, id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email_or_username(
    db: AsyncSession, email: str, username: str
) -> User | None:
    result = await db.execute(
        select(User).where((User.email == email) | (User.username == username))
    )
    return result.scalar_one_or_none()


async def is_user_exists(db: AsyncSession, email: str, username: str) -> bool:
    user = await get_user_by_email_or_username(db, email=email, username=username)
    return user is not None