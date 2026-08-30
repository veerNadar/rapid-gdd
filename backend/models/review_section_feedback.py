import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import FeedbackStatus, SectionType


class ReviewSectionFeedback(Base):
    """One piece of critique + suggested rewrite for a section of a
    reviewed GDD, and the author's decision on it."""

    __tablename__ = "review_section_feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_type: Mapped[SectionType] = mapped_column(
        Enum(
            SectionType,
            name="section_type",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    critique: Mapped[str] = mapped_column(Text, nullable=False)
    suggested_rewrite: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[FeedbackStatus] = mapped_column(
        Enum(
            FeedbackStatus,
            name="feedback_status",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=FeedbackStatus.PENDING,
        server_default=FeedbackStatus.PENDING.value,
    )

    review: Mapped["Review"] = relationship(back_populates="section_feedback")

    def __repr__(self) -> str:
        return f"<ReviewSectionFeedback id={self.id} section={self.section_type} status={self.status}>"
