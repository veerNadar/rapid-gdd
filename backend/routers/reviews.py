import io
import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ai.critique import (
    CritiqueError,
    RateLimitError as CritiqueRateLimitError,
    critique_section,
)
from ai.review_parser import (
    RateLimitError as ParseRateLimitError,
    ReviewParsingError,
    parse_gdd_content,
)
from database import get_db
from models import Project, Review, ReviewSectionFeedback
from models.enums import FeedbackStatus, ReviewSource
from schemas import (
    ProjectWithSections,
    PromoteReviewRequest,
    ReviewSectionFeedbackRead,
    ReviewSectionFeedbackUpdate,
    ReviewWithFeedback,
    ReviewWithSections,
)
from services.gdd_sections import persist_section
from services.review_feedback import persist_feedback

logger = logging.getLogger(__name__)

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
    .txt/.docx file — parse it into our section schema with Gemini,
    critique each parsed section against the review checklist, and store
    the review record, the parsed sections, and the critique feedback."""
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
    except ParseRateLimitError as err:
        raise HTTPException(status_code=429, detail=str(err)) from err
    except ReviewParsingError as err:
        raise HTTPException(status_code=502, detail=str(err)) from err

    review = Review(
        project_id=project_id, source=ReviewSource.UPLOADED, raw_content=raw_text
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    populated_sections = {
        section_type: section_content
        for section_type, section_content in parsed_sections.items()
        if section_content
    }
    saved_sections = [
        persist_section(db, project_id, section_type, section_content)
        for section_type, section_content in populated_sections.items()
    ]

    # Critique each parsed section. A rate limit means every further call
    # will fail too, so stop there and keep whatever feedback was already
    # generated; a one-off failure on a single section just skips that
    # section rather than failing the whole (already-successful) upload.
    feedback_rows: list[ReviewSectionFeedback] = []
    for section_type, section_content in populated_sections.items():
        try:
            result = critique_section(
                project, section_type, section_content, populated_sections
            )
        except CritiqueRateLimitError as err:
            logger.warning(
                "review %s: stopping critique early after %d/%d sections: %s",
                review.id,
                len(feedback_rows),
                len(populated_sections),
                err,
            )
            break
        except CritiqueError as err:
            logger.warning(
                "review %s: skipping critique for section=%s: %s",
                review.id,
                section_type.value,
                err,
            )
            continue

        feedback_rows.append(
            persist_feedback(
                db, review.id, section_type, result.critique, result.suggested_rewrite
            )
        )

    return ReviewWithSections(
        review=review, sections=saved_sections, feedback=feedback_rows
    )


@router.get("/{review_id}", response_model=ReviewWithFeedback)
def get_review(review_id: uuid.UUID, db: Session = Depends(get_db)):
    """A review record plus all of its section critique feedback."""
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    feedback = (
        db.query(ReviewSectionFeedback)
        .filter(ReviewSectionFeedback.review_id == review_id)
        .order_by(ReviewSectionFeedback.section_type)
        .all()
    )
    return ReviewWithFeedback(review=review, feedback=feedback)


@router.get("/{review_id}/feedback")
def list_review_feedback(review_id: uuid.UUID, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post(
    "/{review_id}/promote",
    response_model=ProjectWithSections,
    status_code=201,
)
def promote_review(
    review_id: uuid.UUID,
    payload: PromoteReviewRequest,
    db: Session = Depends(get_db),
):
    """Create a new project seeded with this review's accepted/edited
    sections (using each one's final suggested rewrite). Sections that
    are still pending or were rejected are left out — the new project
    starts with only the improvements the user signed off on, and any
    gaps can be filled in later from ProjectView."""
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    original_project = db.get(Project, review.project_id)
    if original_project is None:
        raise HTTPException(status_code=404, detail="Original project not found")

    accepted_feedback = (
        db.query(ReviewSectionFeedback)
        .filter(
            ReviewSectionFeedback.review_id == review_id,
            ReviewSectionFeedback.status.in_(
                [FeedbackStatus.ACCEPTED, FeedbackStatus.EDITED]
            ),
        )
        .all()
    )
    if not accepted_feedback:
        raise HTTPException(
            status_code=400,
            detail="No accepted or edited sections to promote yet",
        )

    new_project = Project(
        title=payload.title or f"{original_project.title} (Reviewed)",
        # Carry over the original intake so generating any remaining
        # sections later stays consistent with this project's premise.
        intake_data=original_project.intake_data,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    saved_sections = [
        persist_section(db, new_project.id, feedback.section_type, feedback.suggested_rewrite)
        for feedback in accepted_feedback
        if feedback.suggested_rewrite
    ]

    return ProjectWithSections(project=new_project, sections=saved_sections)


@router.patch("/feedback/{feedback_id}", response_model=ReviewSectionFeedbackRead)
def update_review_feedback(
    feedback_id: uuid.UUID,
    payload: ReviewSectionFeedbackUpdate,
    db: Session = Depends(get_db),
):
    """Accept, reject, or edit one piece of section feedback. Editing is
    just a status of "edited" plus an updated `suggested_rewrite` — the
    same row and endpoint the Accept/Reject actions use."""
    feedback = db.get(ReviewSectionFeedback, feedback_id)
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")

    if payload.status is not None:
        feedback.status = payload.status
    if payload.suggested_rewrite is not None:
        feedback.suggested_rewrite = payload.suggested_rewrite

    db.commit()
    db.refresh(feedback)
    return feedback
