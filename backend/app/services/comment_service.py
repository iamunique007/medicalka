from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Comment, User
from app.schemas.comment_schema import SCommentCreateInput
from app.repositories.post_repository import get_post_by_id
from app.repositories.comment_repository import get_comment_by_id, get_comments_by_post_id


class PostNotFound(Exception): ...
class CommentNotFound(Exception): ...
class CommentPermissionDenied(Exception): ...


class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User, post_id: UUID, data: SCommentCreateInput) -> Comment:
        post = await get_post_by_id(self.db, id=post_id)
        if not post:
            raise PostNotFound

        comment = Comment(post_id=post_id, author_id=user.id, content=data.content)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def list_for_post(self, post_id: UUID) -> list[Comment]:
        post = await get_post_by_id(self.db, id=post_id)
        if not post:
            raise PostNotFound
        return await get_comments_by_post_id(self.db, post_id=post_id)

    async def delete(self, user: User, post_id: UUID, comment_id: UUID) -> None:
        comment = await get_comment_by_id(self.db, id=comment_id)
        if not comment or comment.post_id != post_id:
            raise CommentNotFound
        if comment.author_id != user.id:
            raise CommentPermissionDenied

        await self.db.delete(comment)
        await self.db.commit()


def get_comment_service(db: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(db)