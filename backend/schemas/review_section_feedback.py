import uuid

from pydantic import BaseModel, ConfigDict

from models.enums import FeedbackStatus, SectionType


class ReviewSectionFeedbackBase(BaseModel):
    section_type: SectionType
    critique: str
    suggested_rewrite: str | None = None


class ReviewSectionFeedbackCreate(ReviewSectionFeedbackBase):
    review_id: uuid.UUID


class ReviewSectionFeedbackUpdate(BaseModel):
    """For the accept / reject / edit flow on a piece of feedback."""

    status: FeedbackStatus | None = None
    suggested_rewrite: str | None = None


class ReviewSectionFeedbackRead(ReviewSectionFeedbackBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    review_id: uuid.UUID
    status: FeedbackStatus
