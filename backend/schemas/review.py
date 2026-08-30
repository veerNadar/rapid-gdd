import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.enums import ReviewSource

from .gdd_section import GDDSectionRead
from .review_section_feedback import ReviewSectionFeedbackRead


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
    """Response for a review-upload request: the review record, the
    sections parsed from its content, and the critique feedback
    generated for each of them."""

    review: ReviewRead
    sections: list[GDDSectionRead]
    feedback: list[ReviewSectionFeedbackRead] = Field(default_factory=list)


class ReviewWithFeedback(BaseModel):
    """Response for fetching a review: the review record plus all of its
    section critique feedback."""

    review: ReviewRead
    feedback: list[ReviewSectionFeedbackRead]


class PromoteReviewRequest(BaseModel):
    """Body for promoting a review's accepted/edited sections into a new
    project. If `title` is omitted, a default derived from the original
    project's title is used."""

    title: str | None = None
