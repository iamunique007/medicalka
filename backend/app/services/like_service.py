from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Like, User
from app.repositories.post_repository import get_post_by_id
from app.repositories.like_repository import get_like


class PostNotFound(Exception): ...
class CannotLikeOwnPost(Exception): ...
class AlreadyLiked(Exception): ...
class LikeNotFound(Exception): ...


class LikeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def like(self, user: User, post_id: UUID) -> Like:
        post = await get_post_by_id(self.db, id=post_id)
        if not post:
            raise PostNotFound
        if post.author_id == user.id:
            raise CannotLikeOwnPost

        existing = await get_like(self.db, user_id=user.id, post_id=post_id)
        if existing:
            raise AlreadyLiked

        like = Like(user_id=user.id, post_id=post_id)
        self.db.add(like)
        await self.db.commit()
        await self.db.refresh(like)
        return like

    async def unlike(self, user: User, post_id: UUID) -> None:
        like = await get_like(self.db, user_id=user.id, post_id=post_id)
        if not like:
            raise LikeNotFound
        await self.db.delete(like)
        await self.db.commit()


def get_like_service(db: AsyncSession = Depends(get_db)) -> LikeService:
    return LikeService(db)