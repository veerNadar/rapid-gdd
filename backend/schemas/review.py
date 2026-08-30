import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import ReviewSource


class ReviewBase(BaseModel):
    source: ReviewSource


class ReviewCreate(ReviewBase):
    project_id: uuid.UUID


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime
