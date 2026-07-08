from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.models import User
from app.dependencies import login_required
from app.schemas.like_schema import SLikeResponseOutput
from app.services.like_service import (
    LikeService,
    get_like_service,
    PostNotFound,
    CannotLikeOwnPost,
    AlreadyLiked,
    LikeNotFound,
)

router = APIRouter(prefix="/posts/{post_id}/like", tags=["likes"])


@router.post("", response_model=SLikeResponseOutput, status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: UUID,
    service: LikeService = Depends(get_like_service),
    user: User = Depends(login_required),
):
    try:
        return await service.like(user=user, post_id=post_id)
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post topilmadi")
    except CannotLikeOwnPost:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "O'z postingizga like bosa olmaysiz")
    except AlreadyLiked:
        raise HTTPException(status.HTTP_409_CONFLICT, "Siz bu postga allaqachon like bosgansiz")


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_post(
    post_id: UUID,
    service: LikeService = Depends(get_like_service),
    user: User = Depends(login_required),
):
    try:
        await service.unlike(user=user, post_id=post_id)
    except LikeNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Siz bu postga like bosmagansiz")