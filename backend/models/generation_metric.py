import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .enums import CallType, GenerationStatus, SectionType


class GenerationMetric(Base):
    """One row per Gemini call attempt (section generation, review
    parsing, or critique), for the /metrics aggregate endpoint. Written
    best-effort by `services.metrics` — never blocks the AI call it's
    tracking."""

    __tablename__ = "generation_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    call_type: Mapped[CallType] = mapped_column(
        Enum(
            CallType,
            name="call_type",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    # Null for review_parse, which parses a whole document rather than
    # one section.
    section_type: Mapped[SectionType | None] = mapped_column(
        Enum(
            SectionType,
            name="section_type",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=True,
    )
    status: Mapped[GenerationStatus] = mapped_column(
        Enum(
            GenerationStatus,
            name="generation_status",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return (
            f"<GenerationMetric call_type={self.call_type} "
            f"section_type={self.section_type} status={self.status}>"
        )
