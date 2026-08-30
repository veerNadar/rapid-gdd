"""LangChain + Gemini orchestration for generating GDD section content."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import (
    ChatGoogleGenerativeAIError,
    GoogleRateLimitError,
)

from ai.prompts import SECTION_DEPENDENCIES, SECTION_LABELS, SECTION_PROMPTS
from config import settings
from models import Project
from models.enums import SectionType

GEMINI_MODEL = "gemini-3.6-flash"


class SectionGenerationError(Exception):
    """Raised when the AI backend fails to generate a section."""


class RateLimitError(SectionGenerationError):
    """Raised when Gemini's free-tier rate limit is hit (HTTP 429)."""


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

    try:
        response = llm.invoke(messages)
    except GoogleRateLimitError as err:
        raise RateLimitError(
            "Gemini free-tier rate limit reached. Wait a bit before "
            "retrying, or check your quota at "
            "https://ai.google.dev/gemini-api/docs/rate-limits."
        ) from err
    except ChatGoogleGenerativeAIError as err:
        raise SectionGenerationError(f"Gemini request failed: {err}") from err

    # response.content can be a plain string or a list of content blocks
    # (e.g. Gemini 3's reasoning/thinking blocks alongside text). `.text`
    # extracts and concatenates just the `type: "text"` blocks.
    return str(response.text).strip()
