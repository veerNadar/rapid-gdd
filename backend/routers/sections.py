import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ai.generator import RateLimitError, SectionGenerationError, generate_section
from database import get_db
from models import GDDSection, Project
from models.enums import SectionType
from schemas import GDDSectionCreate, GDDSectionRead, GDDSectionUpdate

router = APIRouter(prefix="/sections", tags=["sections"])

# Separate router so the generation endpoint can live at
# /projects/{project_id}/sections/{section_type}/generate, as specified,
# while the CRUD routes above stay under /sections.
generation_router = APIRouter(prefix="/projects", tags=["sections"])


@router.get("/")
def list_sections(project_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/")
def create_section(payload: GDDSectionCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{section_id}")
def get_section(section_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.patch("/{section_id}")
def update_section(
    section_id: uuid.UUID, payload: GDDSectionUpdate, db: Session = Depends(get_db)
):
    raise NotImplementedError


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

    try:
        content = generate_section(project, section_type)
    except RateLimitError as err:
        raise HTTPException(status_code=429, detail=str(err)) from err
    except SectionGenerationError as err:
        raise HTTPException(status_code=502, detail=str(err)) from err

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
