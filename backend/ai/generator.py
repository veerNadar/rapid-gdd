"""LangChain + Gemini orchestration for generating GDD section content."""

import logging
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAIError,
    GoogleRateLimitError,
)

from ai.prompts import SECTION_DEPENDENCIES, SECTION_LABELS, SECTION_PROMPTS
from config import settings
from models import Project
from models.enums import SectionType

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.6-flash"

# Generated content well below this length is almost certainly truncated,
# empty, or otherwise broken — real sections run ~300-500 words (roughly
# 1800-3000 characters), so this is a conservative floor, not a target.
MIN_CONTENT_LENGTH = 200

# How many times to ask Gemini again if a response fails validation
# (empty, too short, missing the expected Markdown structure, or a
# refusal), before giving up.
MAX_GENERATION_ATTEMPTS = 3

_REFUSAL_MARKERS = (
    "i cannot fulfill",
    "i can't fulfill",
    "i cannot assist",
    "i'm sorry, but i can't",
    "as an ai language model",
)


class SectionGenerationError(Exception):
    """Raised when the AI backend fails to generate a section."""


class RateLimitError(SectionGenerationError):
    """Raised when Gemini's free-tier rate limit is hit (HTTP 429)."""


class SectionValidationError(SectionGenerationError):
    """Raised when every generation attempt produced malformed content."""


def _get_llm() -> ChatGoogleGenerativeAI:
    if not settings.google_api_key:
        raise SectionGenerationError(
            "GOOGLE_API_KEY is not configured — set it in backend/.env"
        )
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=settings.google_api_key,
        temperature=0.7,
    )


def _fmt(value: str | None) -> str:
    return value if value else "Not specified"


def _fmt_list(values: list[str] | None) -> str:
    return ", ".join(values) if values else "Not specified"


def _format_context(
    section_type: SectionType, available_sections: dict[SectionType, str] | None
) -> str:
    """Build the "already-generated sections" block for a section's
    prompt, limited to the sections it's declared to depend on (see
    `ai.prompts.SECTION_DEPENDENCIES`) and only including ones that are
    actually present in `available_sections`."""
    relevant_types = SECTION_DEPENDENCIES.get(section_type, [])
    if available_sections:
        blocks = [
            f"#### {SECTION_LABELS[dep_type]}\n{available_sections[dep_type]}"
            for dep_type in relevant_types
            if dep_type in available_sections
        ]
        if blocks:
            return "\n\n".join(blocks)
    return "(No other sections have been generated yet.)"


def _prompt_variables(
    project: Project,
    section_type: SectionType,
    available_sections: dict[SectionType, str] | None,
) -> dict[str, str]:
    """Flatten a project's intake JSON into the prompt template's
    variables, substituting "Not specified" for anything left blank, plus
    the cross-section consistency context."""
    intake = project.intake_data or {}
    return {
        "title": project.title,
        "genre": _fmt(intake.get("genre")),
        "dimension": _fmt(intake.get("dimension")),
        "perspective": _fmt(intake.get("perspective")),
        "multiplayer": _fmt(intake.get("multiplayer")),
        "core_hook": _fmt(intake.get("core_hook")),
        "scope_team_size": _fmt(intake.get("scope_team_size")),
        "target_platform": _fmt_list(intake.get("target_platform")),
        "reference_games": _fmt_list(intake.get("reference_games")),
        "target_feeling": _fmt(intake.get("target_feeling")),
        "context": _format_context(section_type, available_sections),
    }


def _validate_content(content: str) -> str | None:
    """Check generated content for the basic shape a GDD section should
    have. Returns a short description of what's wrong, or `None` if the
    content looks acceptable."""
    if not content or not content.strip():
        return "empty response"
    if len(content) < MIN_CONTENT_LENGTH:
        return f"too short ({len(content)} chars, expected at least {MIN_CONTENT_LENGTH})"
    if "##" not in content:
        return "missing expected Markdown section headings ('##')"
    lowered = content.lower()
    if any(marker in lowered for marker in _REFUSAL_MARKERS):
        return "model declined to generate content"
    return None


def generate_section(
    project: Project,
    section_type: SectionType,
    available_sections: dict[SectionType, str] | None = None,
) -> str:
    """Generate the content for one GDD section using Gemini via LangChain.

    `available_sections` maps section types to their latest generated
    content; only the ones this section is declared to depend on (see
    `ai.prompts.SECTION_DEPENDENCIES`) are actually included in the
    prompt, for consistency (e.g. Characters referencing an existing
    Story & Narrative section). Callers can pass in everything they have
    on hand — irrelevant sections are filtered out automatically.

    If Gemini's response fails basic structural validation (empty, too
    short, missing the expected Markdown headings, or a refusal), this
    retries up to `MAX_GENERATION_ATTEMPTS` times before giving up.
    """
    prompt = SECTION_PROMPTS.get(section_type)
    if prompt is None:
        raise SectionGenerationError(
            f"Generation for section '{section_type.value}' is not implemented yet"
        )

    llm = _get_llm()
    messages = prompt.format_messages(
        **_prompt_variables(project, section_type, available_sections)
    )

    last_issue: str | None = None
    for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
        start = time.monotonic()
        try:
            response = llm.invoke(messages)
        except GoogleRateLimitError as err:
            latency = time.monotonic() - start
            logger.warning(
                "gemini generation: section=%s attempt=%d/%d status=rate_limited "
                "latency=%.2fs",
                section_type.value,
                attempt,
                MAX_GENERATION_ATTEMPTS,
                latency,
            )
            raise RateLimitError(
                "Gemini free-tier rate limit reached. Wait a bit before "
                "retrying, or check your quota at "
                "https://ai.google.dev/gemini-api/docs/rate-limits."
            ) from err
        except ChatGoogleGenerativeAIError as err:
            latency = time.monotonic() - start
            logger.error(
                "gemini generation: section=%s attempt=%d/%d status=error "
                "latency=%.2fs error=%r",
                section_type.value,
                attempt,
                MAX_GENERATION_ATTEMPTS,
                latency,
                str(err),
            )
            raise SectionGenerationError(f"Gemini request failed: {err}") from err

        latency = time.monotonic() - start

        # response.content can be a plain string or a list of content
        # blocks (e.g. Gemini 3's reasoning/thinking blocks alongside
        # text). `.text` extracts and concatenates just the `type:
        # "text"` blocks.
        content = str(response.text).strip()
        issue = _validate_content(content)

        usage = response.usage_metadata
        tokens_in = usage.get("input_tokens") if usage else None
        tokens_out = usage.get("output_tokens") if usage else None
        tokens_total = usage.get("total_tokens") if usage else None

        logger.info(
            "gemini generation: section=%s attempt=%d/%d status=%s "
            "latency=%.2fs chars=%d tokens_in=%s tokens_out=%s tokens_total=%s%s",
            section_type.value,
            attempt,
            MAX_GENERATION_ATTEMPTS,
            "ok" if issue is None else "invalid",
            latency,
            len(content),
            tokens_in,
            tokens_out,
            tokens_total,
            f" reason={issue!r}" if issue else "",
        )

        if issue is None:
            return content
        last_issue = issue

    raise SectionValidationError(
        f"Gemini returned malformed content for '{section_type.value}' after "
        f"{MAX_GENERATION_ATTEMPTS} attempts ({last_issue}). Please try again."
    )
