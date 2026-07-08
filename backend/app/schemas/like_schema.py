from uuid import UUID

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SLikeResponseOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    post_id: UUID
    created_at: datetime