from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SCommentCreateInput(BaseModel):
    content: str = Field(..., min_length=2, max_length=2000)


class SCommentResponseOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    post_id: UUID
    author_id: UUID
    created_at: datetime


class SCommentAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    full_name: str


class SCommentOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    created_at: datetime
    author: SCommentAuthor