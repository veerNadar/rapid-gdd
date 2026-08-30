"""Best-effort recording of every Gemini call attempt, for the /metrics
aggregate endpoint. A metrics write must never break the AI call it's
tracking, so failures here are logged and swallowed, not raised."""

import logging

from database import SessionLocal
from models import GenerationMetric
from models.enums import CallType, GenerationStatus, SectionType

logger = logging.getLogger(__name__)


def record_generation_event(
    call_type: CallType,
    status: GenerationStatus,
    latency_seconds: float,
    section_type: SectionType | None = None,
    tokens_in: int | None = None,
    tokens_out: int | None = None,
    tokens_total: int | None = None,
    error_message: str | None = None,
) -> None:
    """Record one Gemini call attempt in its own short-lived DB session,
    independent of whatever session/transaction the caller is using."""
    db = SessionLocal()
    try:
        db.add(
            GenerationMetric(
                call_type=call_type,
                section_type=section_type,
                status=status,
                latency_ms=round(latency_seconds * 1000),
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                tokens_total=tokens_total,
                error_message=(error_message[:500] if error_message else None),
            )
        )
        db.commit()
    except Exception:
        logger.exception("Failed to record generation metric (non-fatal)")
        db.rollback()
    finally:
        db.close()
