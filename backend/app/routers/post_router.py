from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.models import User
from app.dependencies import verified_required_and_return_user
from app.schemas.post_schema import (
    SPostCreateInput, SPostUpdateInput,
    SPostResponseOutput, SPostDetailOutput, SPaginatedPosts
)
from app.services.post_service import (
    PostService, get_post_service,
    PostNotFound, PostPermissionDenied, NoUpdateData,
)

from app.dependencies import login_required_or_none

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=SPostResponseOutput, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: SPostCreateInput,
    service: PostService = Depends(get_post_service),
    user: User = Depends(verified_required_and_return_user),
):
    return await service.create(user=user, data=body)


@router.get("/{post_id}", response_model=SPostDetailOutput)
async def get_post(
    post_id: UUID,
    user: User = Depends(login_required_or_none),
    service: PostService = Depends(get_post_service),
):
    try:
        post = await service.get(post_id)

        post.likes_count  = await service.get_like_count(post_id=post.id)

        if user is not None:
            post.is_liked = await service.is_liked(post_id=post.id, user_id=user.id)

        return post 
    
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post topilmadi")


@router.patch("/{post_id}", response_model=SPostResponseOutput)
async def update_post(
    post_id: UUID,
    body: SPostUpdateInput,
    service: PostService = Depends(get_post_service),
    user: User = Depends(verified_required_and_return_user),
):
    try:
        return await service.update(user=user, post_id=post_id, data=body)
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post topilmadi")
    except PostPermissionDenied:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bu postni tahrirlashga ruxsatingiz yo'q")
    except NoUpdateData:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Yangilash uchun maydon yuborilmadi")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    service: PostService = Depends(get_post_service),
    user: User = Depends(verified_required_and_return_user),
):
    try:
        await service.delete(user=user, post_id=post_id)
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post topilmadi")
    except PostPermissionDenied:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bu postni o'chirishga ruxsatingiz yo'q")
    



@router.get("", response_model=SPaginatedPosts)
async def list_posts(
    service: PostService = Depends(get_post_service),
    page: int = Query(1, ge=1, description="Sahifa raqami"),
    page_size: int = Query(20, ge=1, le=100, description="Sahifadagi elementlar soni"),
    search: str | None = Query(None, description="title/content bo'yicha qidiruv"),
    date_from: datetime | None = Query(None, description="ISO: 2026-01-01 yoki 2026-01-01T00:00:00"),
    date_to: datetime | None = Query(None, description="ISO format"),
):
    return await service.list(
        page=page,
        page_size=page_size,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )