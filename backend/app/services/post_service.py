from uuid import UUID
from datetime import datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Post, User
from app.repositories.like_repository import get_like
from app.schemas.post_schema import SPostCreateInput, SPostUpdateInput
from app.repositories.post_repository import get_post_by_id, list_posts, get_like_count_by_post_id


class PostNotFound(Exception): ...
class PostPermissionDenied(Exception): ...
class NoUpdateData(Exception): ...


class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
        date_to: datetime | None = None,
        date_from: datetime | None = None,
    ) -> dict:
        posts, total = await list_posts(
            self.db,
            page=page,
            page_size=page_size,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "items": posts,
        }

    async def create(self, user: User, data: SPostCreateInput) -> Post:

        post = Post(title=data.title, content=data.content, author_id=user.id)

        self.db.add(post)

        await self.db.commit()

        await self.db.refresh(post)
        
        return post

    async def get(self, post_id: UUID) -> Post:

        post = await get_post_by_id(self.db, id=post_id)

        if post is None:
            raise PostNotFound
        
        return post

    async def update(self, user: User, post_id: UUID, data: SPostUpdateInput) -> Post:
        post = await self.get(post_id)

        if post.author_id != user.id:
            raise PostPermissionDenied

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise NoUpdateData

        for key, value in update_data.items():
            setattr(post, key, value)

        await self.db.commit()

        await self.db.refresh(post)

        return post

    async def delete(self, user: User, post_id: UUID) -> None:
        post = await self.get(post_id)

        if post.author_id != user.id:
            raise PostPermissionDenied
        
        await self.db.delete(post)

        await self.db.commit()

    async def get_like_count(self, post_id: UUID) -> int:
        return await get_like_count_by_post_id(self.db, post_id)
    
    async def is_liked(self, user_id: UUID, post_id: UUID) -> bool:
        liked = await get_like(self.db, user_id=user_id, post_id=post_id)

        return liked is not None

def get_post_service(db: AsyncSession = Depends(get_db)) -> PostService:
    return PostService(db)