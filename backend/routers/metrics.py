from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import GenerationMetric
from models.enums import CallType, GenerationStatus, SectionType
from schemas import CallTypeStats, MetricsSummary, SectionTypeStats

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Gemini's free tier caps generateContent requests per model per day.
# Observed directly from a 429 response during development:
# "GenerateRequestsPerDayPerProjectPerModel-FreeTier ... quotaValue: '20'".
# Hardcoded rather than fetched — Google doesn't expose a quota-status
# API — so treat this as an estimate that should be updated if the
# limit or model changes.
FREE_TIER_DAILY_REQUEST_LIMIT = 20


def _stats(rows: list[GenerationMetric]) -> tuple[int, int, int, float, float | None]:
    total = len(rows)
    successful = sum(1 for r in rows if r.status == GenerationStatus.OK)
    failed = total - successful
    success_rate = successful / total if total else 0.0
    latencies = [r.latency_ms for r in rows]
    avg_latency_ms = sum(latencies) / len(latencies) if latencies else None
    return total, successful, failed, success_rate, avg_latency_ms


@router.get("/", response_model=MetricsSummary)
def get_metrics(db: Session = Depends(get_db)):
    """Aggregate stats over every Gemini call this backend has made:
    success/failure rate and average latency per call type and per
    section type, total token usage, and today's call volume against
    the free-tier daily request limit.

    Row count here is inherently bounded by the free-tier limit itself
    (a handful of calls a day at most), so aggregating in Python after
    one query is simpler than — and just as fast as — doing it in SQL.
    """
    rows = db.query(GenerationMetric).all()

    total_tokens_in = sum(r.tokens_in or 0 for r in rows)
    total_tokens_out = sum(r.tokens_out or 0 for r in rows)
    total_tokens_total = sum(r.tokens_total or 0 for r in rows)

    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    calls_today = sum(1 for r in rows if r.created_at >= today_start)

    by_call_type = []
    for call_type in CallType:
        group = [r for r in rows if r.call_type == call_type]
        if not group:
            continue
        total, successful, failed, rate, avg_latency = _stats(group)
        by_call_type.append(
            CallTypeStats(
                call_type=call_type,
                total_calls=total,
                successful=successful,
                failed=failed,
                success_rate=rate,
                avg_latency_ms=avg_latency,
            )
        )

    by_section_type = []
    for section_type in SectionType:
        group = [r for r in rows if r.section_type == section_type]
        if not group:
            continue
        total, successful, failed, rate, avg_latency = _stats(group)
        by_section_type.append(
            SectionTypeStats(
                section_type=section_type,
                total_calls=total,
                successful=successful,
                failed=failed,
                success_rate=rate,
                avg_latency_ms=avg_latency,
            )
        )

    return MetricsSummary(
        total_calls=len(rows),
        total_tokens_in=total_tokens_in,
        total_tokens_out=total_tokens_out,
        total_tokens_total=total_tokens_total,
        calls_today=calls_today,
        free_tier_daily_limit=FREE_TIER_DAILY_REQUEST_LIMIT,
        free_tier_usage_pct=(
            calls_today / FREE_TIER_DAILY_REQUEST_LIMIT
            if FREE_TIER_DAILY_REQUEST_LIMIT
            else None
        ),
        by_call_type=by_call_type,
        by_section_type=by_section_type,
    )
