import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import GDDSectionCreate, GDDSectionUpdate

router = APIRouter(prefix="/sections", tags=["sections"])


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
