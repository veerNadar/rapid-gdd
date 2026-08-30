import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.enums import ReviewSource

from .gdd_section import GDDSectionRead


class ReviewBase(BaseModel):
    source: ReviewSource


class ReviewCreate(ReviewBase):
    project_id: uuid.UUID


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    raw_content: str | None = None
    created_at: datetime


class ReviewWithSections(BaseModel):
    """Response for a review-upload request: the review record, plus
    whichever sections were populated by parsing its content."""

    review: ReviewRead
    sections: list[GDDSectionRead]
