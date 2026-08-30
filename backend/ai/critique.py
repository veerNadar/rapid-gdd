"""LangChain + Gemini critique of a reviewed GDD section: a critique
against the review checklist, plus a suggested rewrite."""

import logging
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAIError,
    GoogleRateLimitError,
)
from pydantic import BaseModel, Field

from ai.context import format_context, intake_variables
from ai.prompts import CRITIQUE_PROMPT, SECTION_LABELS
from config import settings
from models import Project
from models.enums import SectionType

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.6-flash"

# Floors well below what a real critique/rewrite should look like — just
# enough to catch an empty, truncated, or one-line non-answer.
MIN_CRITIQUE_LENGTH = 30
MIN_REWRITE_LENGTH = 150

# How many times to ask Gemini again if the critique or rewrite fails
# basic validation, before giving up.
MAX_CRITIQUE_ATTEMPTS = 3


class CritiqueError(Exception):
    """Raised when the AI backend fails to critique a section."""


class RateLimitError(CritiqueError):
    """Raised when Gemini's free-tier rate limit is hit (HTTP 429)."""


class SectionCritique(BaseModel):
    critique: str = Field(
        description=(
            "Specific, actionable feedback grounded in the review checklist and "
            "the section's actual content — only the issues that actually apply."
        )
    )
    suggested_rewrite: str = Field(
        description=(
            "A complete, ready-to-use replacement for the section that fixes the "
            "critique, in the same Markdown '##' subheading style as the original."
        )
    )


def _get_llm() -> ChatGoogleGenerativeAI:
    if not settings.google_api_key:
        raise CritiqueError("GOOGLE_API_KEY is not configured — set it in backend/.env")
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=settings.google_api_key,
        temperature=0.4,
    )


def _validate(critique: str, suggested_rewrite: str) -> str | None:
    """Check a critique + rewrite pair for the basic shape they should
    have. Returns a short description of what's wrong, or `None` if they
    look acceptable."""
    if not critique or len(critique.strip()) < MIN_CRITIQUE_LENGTH:
        return "critique missing or too short"
    if not suggested_rewrite or len(suggested_rewrite.strip()) < MIN_REWRITE_LENGTH:
        return "suggested rewrite missing or too short"
    if "##" not in suggested_rewrite:
        return "suggested rewrite missing expected Markdown headings ('##')"
    return None


def critique_section(
    project: Project,
    section_type: SectionType,
    section_content: str,
    available_sections: dict[SectionType, str] | None = None,
) -> SectionCritique:
    """Critique one parsed GDD section against the review checklist
    (vague core loop, scope mismatch, mechanics vs. target feeling, weak
    progression, narrative inconsistency, structurally shallow) and
    propose a full rewrite, using Gemini via LangChain.

    `available_sections` maps section types to their content; only the
    ones this section is declared to depend on (see
    `ai.prompts.SECTION_DEPENDENCIES`) are included as context, mainly
    to support the narrative-inconsistency check.
    """
    llm = _get_llm()
    structured_llm = llm.with_structured_output(SectionCritique)
    messages = CRITIQUE_PROMPT.format_messages(
        **intake_variables(project),
        section_label=SECTION_LABELS[section_type],
        section_content=section_content,
        context=format_context(section_type, available_sections),
    )

    last_issue: str | None = None
    for attempt in range(1, MAX_CRITIQUE_ATTEMPTS + 1):
        start = time.monotonic()
        try:
            result = structured_llm.invoke(messages)
        except GoogleRateLimitError as err:
            latency = time.monotonic() - start
            logger.warning(
                "gemini critique: section=%s attempt=%d/%d status=rate_limited "
                "latency=%.2fs",
                section_type.value,
                attempt,
                MAX_CRITIQUE_ATTEMPTS,
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
                "gemini critique: section=%s attempt=%d/%d status=error "
                "latency=%.2fs error=%r",
                section_type.value,
                attempt,
                MAX_CRITIQUE_ATTEMPTS,
                latency,
                str(err),
            )
            raise CritiqueError(f"Gemini request failed: {err}") from err

        latency = time.monotonic() - start
        if not isinstance(result, SectionCritique):
            result = SectionCritique.model_validate(result)

        issue = _validate(result.critique, result.suggested_rewrite)

        logger.info(
            "gemini critique: section=%s attempt=%d/%d status=%s latency=%.2fs%s",
            section_type.value,
            attempt,
            MAX_CRITIQUE_ATTEMPTS,
            "ok" if issue is None else "invalid",
            latency,
            f" reason={issue!r}" if issue else "",
        )

        if issue is None:
            return result
        last_issue = issue

    raise CritiqueError(
        f"Gemini returned a malformed critique for '{section_type.value}' after "
        f"{MAX_CRITIQUE_ATTEMPTS} attempts ({last_issue})."
    )
