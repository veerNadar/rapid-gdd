"""Shared read/write helpers for `GDDSection` rows, used by both the
generation endpoints (routers/sections.py) and the review-upload
endpoint (routers/reviews.py) — both save their output the same way, as
the next version of a project's section."""

import uuid

from sqlalchemy.orm import Session

from models import GDDSection
from models.enums import SectionType


def latest_section_rows(db: Session, project_id: uuid.UUID) -> list[GDDSection]:
    """The most recent version of each section type already generated
    for a project (one row per section type), as full rows."""
    return (
        db.query(GDDSection)
        .filter(GDDSection.project_id == project_id)
        .order_by(GDDSection.section_type, GDDSection.version.desc())
        .distinct(GDDSection.section_type)
        .all()
    )


def latest_sections(db: Session, project_id: uuid.UUID) -> dict[SectionType, str]:
    """The most recent version of each section type already generated
    for a project, keyed by section type."""
    return {
        row.section_type: row.content for row in latest_section_rows(db, project_id)
    }


def persist_section(
    db: Session, project_id: uuid.UUID, section_type: SectionType, content: str
) -> GDDSection:
    """Save new section content as the next version for its type."""
    latest = (
        db.query(GDDSection)
        .filter(
            GDDSection.project_id == project_id,
            GDDSection.section_type == section_type,
        )
        .order_by(GDDSection.version.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1

    section = GDDSection(
        project_id=project_id,
        section_type=section_type,
        content=content,
        version=next_version,
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return section
