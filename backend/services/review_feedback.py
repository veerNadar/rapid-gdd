"""Persistence helper for `ReviewSectionFeedback` rows, used by the
review-upload endpoint's critique step."""

import uuid

from sqlalchemy.orm import Session

from models import ReviewSectionFeedback
from models.enums import SectionType


def persist_feedback(
    db: Session,
    review_id: uuid.UUID,
    section_type: SectionType,
    critique: str,
    suggested_rewrite: str,
) -> ReviewSectionFeedback:
    feedback = ReviewSectionFeedback(
        review_id=review_id,
        section_type=section_type,
        critique=critique,
        suggested_rewrite=suggested_rewrite,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
