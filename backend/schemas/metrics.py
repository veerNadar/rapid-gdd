from pydantic import BaseModel

from models.enums import CallType, SectionType


class CallTypeStats(BaseModel):
    call_type: CallType
    total_calls: int
    successful: int
    failed: int
    success_rate: float
    avg_latency_ms: float | None


class SectionTypeStats(BaseModel):
    section_type: SectionType
    total_calls: int
    successful: int
    failed: int
    success_rate: float
    avg_latency_ms: float | None


class MetricsSummary(BaseModel):
    total_calls: int
    total_tokens_in: int
    total_tokens_out: int
    total_tokens_total: int
    calls_today: int
    free_tier_daily_limit: int
    free_tier_usage_pct: float | None
    by_call_type: list[CallTypeStats]
    by_section_type: list[SectionTypeStats]
