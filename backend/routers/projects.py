import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{project_id}")
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.patch("/{project_id}")
def update_project(
    project_id: uuid.UUID, payload: ProjectUpdate, db: Session = Depends(get_db)
):
    raise NotImplementedError


@router.delete("/{project_id}")
def delete_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError
