import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ai.generator import RateLimitError, SectionGenerationError, generate_section
from ai.prompts import SECTION_ORDER
from database import get_db
from models import GDDSection, Project
from models.enums import SectionType
from schemas import GDDSectionCreate, GDDSectionRead, GDDSectionUpdate
from services.gdd_sections import latest_section_rows, latest_sections, persist_section

router = APIRouter(prefix="/sections", tags=["sections"])

# Separate router so the generation endpoints can live at
# /projects/{project_id}/..., as specified, while the CRUD routes above
# stay under /sections.
generation_router = APIRouter(prefix="/projects", tags=["sections"])


@router.get("/", response_model=list[GDDSectionRead])
def list_sections(project_id: uuid.UUID, db: Session = Depends(get_db)):
    """The latest version of each section type generated for a project."""
    return latest_section_rows(db, project_id)


@router.post("/")
def create_section(payload: GDDSectionCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{section_id}")
def get_section(section_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.patch("/{section_id}", response_model=GDDSectionRead)
def update_section(
    section_id: uuid.UUID, payload: GDDSectionUpdate, db: Session = Depends(get_db)
):
    """Manually edit a section's content in place. This does not create a
    new version — versioning is reserved for AI (re)generation; a manual
    edit just updates the current row's content and `updated_at`."""
    section = db.get(GDDSection, section_id)
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")

    if payload.content is not None:
        section.content = payload.content

    db.commit()
    db.refresh(section)
    return section


@router.delete("/{section_id}")
def delete_section(section_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@generation_router.post(
    "/{project_id}/sections/{section_type}/generate",
    response_model=GDDSectionRead,
    status_code=201,
)
def generate_project_section(
    project_id: uuid.UUID,
    section_type: SectionType,
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    available_sections = latest_sections(db, project_id)

    try:
        content = generate_section(project, section_type, available_sections)
    except RateLimitError as err:
        raise HTTPException(status_code=429, detail=str(err)) from err
    except SectionGenerationError as err:
        raise HTTPException(status_code=502, detail=str(err)) from err

    return persist_section(db, project_id, section_type, content)


@generation_router.post(
    "/{project_id}/generate",
    response_model=list[GDDSectionRead],
    status_code=201,
)
def generate_full_gdd(project_id: uuid.UUID, db: Session = Depends(get_db)):
    """Generate every section of the GDD in sequence, in dependency order
    (see `ai.prompts.SECTION_ORDER`), each one able to reference the
    sections generated before it for consistency.

    If generation fails partway through (e.g. hitting the Gemini
    free-tier rate limit), whatever sections were already generated stay
    saved, and the error reports how far it got.
    """
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Seed with anything already generated, so re-running this on a
    # partially-complete project still gives later sections real context.
    available_sections = latest_sections(db, project_id)
    generated: list[GDDSection] = []

    for section_type in SECTION_ORDER:
        try:
            content = generate_section(project, section_type, available_sections)
        except RateLimitError as err:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"{err} Generated {len(generated)} of {len(SECTION_ORDER)} "
                    "sections before hitting the rate limit; the rest were "
                    "not created. Re-run this once the limit resets to pick "
                    "up where it left off."
                ),
            ) from err
        except SectionGenerationError as err:
            raise HTTPException(status_code=502, detail=str(err)) from err

        section = persist_section(db, project_id, section_type, content)
        available_sections[section_type] = content
        generated.append(section)

    return generated
