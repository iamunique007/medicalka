from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SPostCreateInput(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=1, max_length=10000)


class SPostUpdateInput(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=1, max_length=10000)


class SPostResponseOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime
    updated_at: datetime


class SPostDetailOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author_id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    is_liked: bool = False


class SPaginatedPosts(BaseModel):
    page: int
    total: int
    page_size: int
    items: list[SPostResponseOutput]