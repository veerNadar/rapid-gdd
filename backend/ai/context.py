"""Shared helpers for turning a project's intake data and its other
sections into prompt variables — used by both section generation
(generator.py) and critique (critique.py)."""

from ai.prompts import SECTION_DEPENDENCIES, SECTION_LABELS
from models import Project
from models.enums import SectionType


def fmt(value: str | None) -> str:
    return value if value else "Not specified"


def fmt_list(values: list[str] | None) -> str:
    return ", ".join(values) if values else "Not specified"


def format_context(
    section_type: SectionType, available_sections: dict[SectionType, str] | None
) -> str:
    """Build the "other sections" block for a section's prompt, limited
    to the sections it's declared to depend on (see
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


def intake_variables(project: Project) -> dict[str, str]:
    """Flatten a project's intake JSON into prompt template variables,
    substituting "Not specified" for anything left blank."""
    intake = project.intake_data or {}
    return {
        "title": project.title,
        "genre": fmt(intake.get("genre")),
        "dimension": fmt(intake.get("dimension")),
        "perspective": fmt(intake.get("perspective")),
        "multiplayer": fmt(intake.get("multiplayer")),
        "core_hook": fmt(intake.get("core_hook")),
        "scope_team_size": fmt(intake.get("scope_team_size")),
        "target_platform": fmt_list(intake.get("target_platform")),
        "reference_games": fmt_list(intake.get("reference_games")),
        "target_feeling": fmt(intake.get("target_feeling")),
    }
