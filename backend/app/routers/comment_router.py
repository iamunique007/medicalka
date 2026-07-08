from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.models import User
from app.dependencies import verified_required_and_return_user
from app.schemas.comment_schema import (
    SCommentCreateInput,
    SCommentResponseOutput,
    SCommentOutput,
)
from app.services.comment_service import (
    CommentService,
    get_comment_service,
    PostNotFound,
    CommentNotFound,
    CommentPermissionDenied,
)

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.post("", response_model=SCommentResponseOutput, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: UUID,
    body: SCommentCreateInput,
    service: CommentService = Depends(get_comment_service),
    user: User = Depends(verified_required_and_return_user),
):
    try:
        return await service.create(user=user, post_id=post_id, data=body)
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post topilmadi")


@router.get("", response_model=list[SCommentOutput])
async def list_comments(
    post_id: UUID,
    service: CommentService = Depends(get_comment_service),
):
    try:
        return await service.list_for_post(post_id)
    except PostNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post topilmadi")


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_id: UUID,
    comment_id: UUID,
    service: CommentService = Depends(get_comment_service),
    user: User = Depends(verified_required_and_return_user),
):
    try:
        await service.delete(user=user, post_id=post_id, comment_id=comment_id)
    except CommentNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Izoh topilmadi")
    except CommentPermissionDenied:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bu izohni o'chirishga ruxsatingiz yo'q")