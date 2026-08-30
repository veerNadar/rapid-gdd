import io
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ai.review_parser import RateLimitError, ReviewParsingError, parse_gdd_content
from database import get_db
from models import Project, Review
from models.enums import ReviewSource
from schemas import ReviewSectionFeedbackUpdate, ReviewWithSections
from services.gdd_sections import persist_section

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _extract_text_from_upload(file: UploadFile) -> str:
    """Pull plain text out of an uploaded .txt or .docx file. Anything
    else is treated as plain text best-effort."""
    filename = (file.filename or "").lower()
    raw = file.file.read()

    if filename.endswith(".docx"):
        try:
            from docx import Document
        except ImportError as exc:  # pragma: no cover - dependency is pinned
            raise HTTPException(
                status_code=500, detail="DOCX support is not installed on the server"
            ) from exc
        try:
            document = Document(io.BytesIO(raw))
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail="Could not read this .docx file — it may be corrupt"
            ) from exc
        return "\n".join(paragraph.text for paragraph in document.paragraphs)

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="replace")


@router.get("/")
def list_reviews(project_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=ReviewWithSections, status_code=201)
def create_review(
    project_id: uuid.UUID = Form(...),
    content: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    """Accept a developer's own GDD — pasted as text or uploaded as a
    .txt/.docx file — parse it into our section schema with Gemini, and
    store both the review record and the parsed sections."""
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if file is not None and file.filename:
        raw_text = _extract_text_from_upload(file)
    elif content is not None:
        raw_text = content
    else:
        raise HTTPException(
            status_code=400, detail="Provide either pasted content or a file upload"
        )

    raw_text = raw_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="The provided content is empty")

    try:
        parsed_sections = parse_gdd_content(raw_text)
    except RateLimitError as err:
        raise HTTPException(status_code=429, detail=str(err)) from err
    except ReviewParsingError as err:
        raise HTTPException(status_code=502, detail=str(err)) from err

    review = Review(
        project_id=project_id, source=ReviewSource.UPLOADED, raw_content=raw_text
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    saved_sections = [
        persist_section(db, project_id, section_type, section_content)
        for section_type, section_content in parsed_sections.items()
        if section_content
    ]

    return ReviewWithSections(review=review, sections=saved_sections)


@router.get("/{review_id}")
def get_review(review_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{review_id}/feedback")
def list_review_feedback(review_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.patch("/feedback/{feedback_id}")
def update_review_feedback(
    feedback_id: uuid.UUID,
    payload: ReviewSectionFeedbackUpdate,
    db: Session = Depends(get_db),
):
    raise NotImplementedError
