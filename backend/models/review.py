import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import ReviewSource


class Review(Base):
    """A single review pass over a project's GDD, either an uploaded
    document or a Rapid GDD-generated draft."""

    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source: Mapped[ReviewSource] = mapped_column(
        Enum(
            ReviewSource,
            name="review_source",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    # The raw text this review was built from — pasted directly, or
    # extracted from an uploaded .txt/.docx file. Kept for reference and
    # so a failed/partial parse can be retried without re-uploading.
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="reviews")
    section_feedback: Mapped[list["ReviewSectionFeedback"]] = relationship(
        back_populates="review", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Review id={self.id} source={self.source}>"
