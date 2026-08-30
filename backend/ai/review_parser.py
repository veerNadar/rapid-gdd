"""LangChain + Gemini parsing of a developer's raw/uploaded GDD text into
our section schema (see `models.enums.SectionType`)."""

import logging
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAIError,
    GoogleRateLimitError,
)
from pydantic import BaseModel, Field

from ai.prompts import REVIEW_PARSE_PROMPT
from config import settings
from models.enums import CallType, GenerationStatus, SectionType
from services.metrics import record_generation_event

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.6-flash"

# How many times to ask Gemini again if a parse comes back with nothing
# mapped to any section at all, before giving up.
MAX_PARSE_ATTEMPTS = 3

# A full GDD document is realistically a few thousand words; this is a
# generous cap (~10k tokens) to keep cost/latency bounded against
# something absurdly large rather than a tight limit on legitimate input.
MAX_RAW_CONTENT_LENGTH = 40_000


class ReviewParsingError(Exception):
    """Raised when the AI backend fails to parse an uploaded/pasted GDD."""


class RateLimitError(ReviewParsingError):
    """Raised when Gemini's free-tier rate limit is hit (HTTP 429)."""


class ParsedGDDSections(BaseModel):
    """One field per `SectionType`, matching its value exactly. Empty
    string means the source had nothing recognizable for that section."""

    overview: str = Field(
        default="", description="Concept, genre, platform, core hook, target feeling"
    )
    gameplay_mechanics: str = Field(
        default="", description="Core loop, mechanics, controls, systems"
    )
    story_narrative: str = Field(
        default="", description="Premise, setting, structure, story beats, themes"
    )
    characters: str = Field(
        default="", description="Protagonist, cast, character-mechanic ties"
    )
    world_building: str = Field(default="", description="Locations, lore, world rules")
    progression: str = Field(default="", description="Leveling, unlocks, pacing, rewards")
    additional: str = Field(
        default="",
        description=(
            "Everything else (art/audio, UI/UX, technical, monetization, risks), "
            "plus any leftover content that didn't fit another category, appended "
            "under an '## Unmapped Content' heading."
        ),
    )


def _get_llm() -> ChatGoogleGenerativeAI:
    if not settings.google_api_key:
        raise ReviewParsingError(
            "GOOGLE_API_KEY is not configured — set it in backend/.env"
        )
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=settings.google_api_key,
        # Low temperature: this is classification/reorganization of the
        # developer's own text, not creative writing.
        temperature=0.2,
    )


def parse_gdd_content(raw_content: str) -> dict[SectionType, str]:
    """Use Gemini to sort a developer's raw/uploaded GDD text into our
    section schema.

    Returns a dict with all 7 `SectionType`s as keys; a section's value
    is `""` if the source had nothing recognizable for it. Content that
    doesn't clearly belong anywhere lands in `SectionType.ADDITIONAL`
    under an "Unmapped Content" heading rather than being discarded.
    """
    raw_content = raw_content.strip()
    if not raw_content:
        raise ReviewParsingError("No content to parse — the document is empty.")

    if len(raw_content) > MAX_RAW_CONTENT_LENGTH:
        raw_content = raw_content[:MAX_RAW_CONTENT_LENGTH]
        logger.warning(
            "review parse: input truncated to %d chars", MAX_RAW_CONTENT_LENGTH
        )

    llm = _get_llm()
    structured_llm = llm.with_structured_output(ParsedGDDSections)
    messages = REVIEW_PARSE_PROMPT.format_messages(raw_content=raw_content)

    last_issue: str | None = None
    for attempt in range(1, MAX_PARSE_ATTEMPTS + 1):
        start = time.monotonic()
        try:
            result = structured_llm.invoke(messages)
        except GoogleRateLimitError as err:
            latency = time.monotonic() - start
            logger.warning(
                "gemini review parse: attempt=%d/%d status=rate_limited latency=%.2fs",
                attempt,
                MAX_PARSE_ATTEMPTS,
                latency,
            )
            record_generation_event(
                CallType.REVIEW_PARSE, GenerationStatus.RATE_LIMITED, latency
            )
            raise RateLimitError(
                "Gemini free-tier rate limit reached. Wait a bit before "
                "retrying, or check your quota at "
                "https://ai.google.dev/gemini-api/docs/rate-limits."
            ) from err
        except ChatGoogleGenerativeAIError as err:
            latency = time.monotonic() - start
            logger.error(
                "gemini review parse: attempt=%d/%d status=error latency=%.2fs error=%r",
                attempt,
                MAX_PARSE_ATTEMPTS,
                latency,
                str(err),
            )
            record_generation_event(
                CallType.REVIEW_PARSE,
                GenerationStatus.ERROR,
                latency,
                error_message=str(err),
            )
            raise ReviewParsingError(f"Gemini request failed: {err}") from err

        latency = time.monotonic() - start
        if not isinstance(result, ParsedGDDSections):
            result = ParsedGDDSections.model_validate(result)

        sections = {
            SectionType.OVERVIEW: result.overview.strip(),
            SectionType.GAMEPLAY_MECHANICS: result.gameplay_mechanics.strip(),
            SectionType.STORY_NARRATIVE: result.story_narrative.strip(),
            SectionType.CHARACTERS: result.characters.strip(),
            SectionType.WORLD_BUILDING: result.world_building.strip(),
            SectionType.PROGRESSION: result.progression.strip(),
            SectionType.ADDITIONAL: result.additional.strip(),
        }
        populated = sum(1 for content in sections.values() if content)

        logger.info(
            "gemini review parse: attempt=%d/%d status=%s latency=%.2fs "
            "sections_populated=%d/7",
            attempt,
            MAX_PARSE_ATTEMPTS,
            "ok" if populated else "invalid",
            latency,
            populated,
        )
        record_generation_event(
            CallType.REVIEW_PARSE,
            GenerationStatus.OK if populated else GenerationStatus.INVALID,
            latency,
            error_message=None if populated else "no content was mapped to any section",
        )

        if populated > 0:
            return sections
        last_issue = "no content was mapped to any section"

    raise ReviewParsingError(
        "Gemini could not extract any recognizable GDD content from this "
        f"document after {MAX_PARSE_ATTEMPTS} attempts"
        + (f" ({last_issue})" if last_issue else "")
        + "."
    )
